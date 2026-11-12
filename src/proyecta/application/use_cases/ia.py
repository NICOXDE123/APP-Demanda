"""Casos de uso de sugerencias asistidas con cita y aprobación humana (T144, US10).

La IA nunca escribe: genera una ``SugerenciaIA`` pendiente con la evidencia que
la respalda. Aceptar o descartar es una acción humana explícita y la aceptación
siempre deja un ``EventoAuditoria`` con origen ``IA``.
"""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass, field
from typing import Callable, Iterable, Sequence
from uuid import UUID

from proyecta.application.ports import (
    ContextoSugerencia,
    ProveedorIA,
    Reloj,
    RepositorioAuditoria,
    RepositorioBitacora,
    RepositorioRegistros,
    RepositorioSugerencias,
)
from proyecta.domain.entities import Bitacora, EventoAuditoria, Registro, SugerenciaIA, utcnow
from proyecta.domain.enums import (
    EntidadAuditoria,
    Estado,
    EstadoSugerencia,
    EtiquetaIA,
    Flujo,
    Origen,
)
from proyecta.domain.errors import ErrorConflicto, ErrorIA, ErrorNoEncontrado, ErrorValidacion
from proyecta.infrastructure.ai.vertex import VERSION_PROMPT

AplicadorSugerencia = Callable[[SugerenciaIA, UUID], None]


@dataclass(frozen=True, slots=True)
class Hallazgo:
    """Contradicción detectada entre bitácora y campos del registro."""

    campo: str
    valor_sugerido: str
    cita_bitacora_id: UUID
    justificacion: str
    etiqueta: EtiquetaIA = EtiquetaIA.ESTIMACION


def _normalizar(texto: str) -> str:
    sin_acentos = "".join(
        caracter
        for caracter in unicodedata.normalize("NFKD", texto)
        if not unicodedata.combining(caracter)
    )
    return sin_acentos.lower()


_REGLAS_ESTADO: tuple[tuple[tuple[str, ...], Estado, str], ...] = (
    (("cancel",), Estado.CANCELADA, "La bitácora menciona una cancelación"),
    (("cerrad", "termino de servicio"), Estado.CERRADA, "La bitácora menciona un cierre"),
    (("standby", "stand by", "pausa"), Estado.STANDBY, "La bitácora menciona una pausa"),
    (("adjudic",), Estado.ADJUDICADA, "La bitácora menciona una adjudicación"),
)


def detectar_contradicciones(
    registro: Registro, entradas: Sequence[Bitacora]
) -> list[Hallazgo]:
    """Detección determinista y explicable; no depende de un modelo externo."""
    hallazgos: list[Hallazgo] = []
    vistos: set[tuple[str, str]] = set()

    for entrada in entradas:
        texto = _normalizar(entrada.contenido)
        for claves, estado, justificacion in _REGLAS_ESTADO:
            if any(clave in texto for clave in claves) and registro.estado is not estado:
                clave = ("estado", estado.value)
                if clave in vistos:
                    continue
                vistos.add(clave)
                hallazgos.append(
                    Hallazgo(
                        campo="estado",
                        valor_sugerido=estado.value,
                        cita_bitacora_id=entrada.id,
                        justificacion=justificacion,
                    )
                )
        if "perfiles seleccionados" in texto and registro.flujo is not Flujo.PERFILES_SELECCIONADOS:
            clave = ("flujo", Flujo.PERFILES_SELECCIONADOS.value)
            if clave not in vistos:
                vistos.add(clave)
                hallazgos.append(
                    Hallazgo(
                        campo="flujo",
                        valor_sugerido=Flujo.PERFILES_SELECCIONADOS.value,
                        cita_bitacora_id=entrada.id,
                        justificacion="La bitácora confirma perfiles seleccionados",
                        etiqueta=EtiquetaIA.DATO_VERIFICADO,
                    )
                )
    return hallazgos


def _contexto(registro: Registro, entradas: Sequence[Bitacora]) -> ContextoSugerencia:
    return ContextoSugerencia(
        registro_id=registro.id,
        codigo=registro.codigo,
        estado=registro.estado.value,
        flujo=registro.flujo.value,
        tipo=registro.tipo.value,
        campos={
            "estado": registro.estado.value,
            "flujo": registro.flujo.value,
            "probabilidad_bp": registro.probabilidad_bp,
            "confiabilidad_bp": registro.confiabilidad_bp,
        },
        fragmentos_bitacora=tuple(entrada.contenido[:400] for entrada in entradas),
        evidencias=tuple((entrada.id, entrada.contenido) for entrada in entradas),
    )


@dataclass
class GenerarSugerencias:
    """Genera sugerencias pendientes; si la IA falla, no bloquea nada."""

    registros: RepositorioRegistros
    bitacora: RepositorioBitacora
    sugerencias: RepositorioSugerencias
    proveedor: ProveedorIA | None = None
    reloj: Reloj | None = None
    version_prompt: str = VERSION_PROMPT

    def _ahora(self):
        return self.reloj.ahora() if self.reloj is not None else utcnow()

    def ejecutar(self, registro_id: UUID) -> list[SugerenciaIA]:
        registro = self.registros.obtener(registro_id)
        if registro is None:
            raise ErrorNoEncontrado(
                "NO_ENCONTRADO",
                "El registro solicitado no existe",
                detalle={"registro_id": str(registro_id)},
            )
        entradas = list(self.bitacora.listar_por_registro(registro_id))
        if not entradas:
            return []

        hallazgos = detectar_contradicciones(registro, entradas)
        if self.proveedor is not None and self.proveedor.disponible():
            propuesta = self.proveedor.sugerir(_contexto(registro, entradas))
            if propuesta is not None:
                if propuesta.cita_id is None:
                    raise ErrorIA(
                        "IA_SIN_EVIDENCIA", "La propuesta de IA no cita una evidencia"
                    )
                if not any(hallazgo.campo == propuesta.campo for hallazgo in hallazgos):
                    hallazgos.append(
                        Hallazgo(
                            campo=propuesta.campo,
                            valor_sugerido=str(propuesta.valor_sugerido),
                            cita_bitacora_id=propuesta.cita_id,
                            justificacion=propuesta.justificacion,
                            etiqueta=propuesta.etiqueta,
                        )
                    )

        creadas: list[SugerenciaIA] = []
        for hallazgo in hallazgos:
            sugerencia = SugerenciaIA(
                registro_id=registro_id,
                campo=hallazgo.campo,
                valor_sugerido=hallazgo.valor_sugerido,
                cita_bitacora_id=hallazgo.cita_bitacora_id,
                estado=EstadoSugerencia.PENDIENTE,
                version_prompt=self.version_prompt,
                creado_en=self._ahora(),
                etiqueta=hallazgo.etiqueta,
                justificacion=hallazgo.justificacion,
            )
            creadas.append(self.sugerencias.guardar(sugerencia))
        return creadas


@dataclass
class AceptarSugerencia:
    """Aprobación humana; audita con origen IA y no escribe sola en el registro."""

    sugerencias: RepositorioSugerencias
    auditoria: RepositorioAuditoria
    reloj: Reloj | None = None
    aplicador: AplicadorSugerencia | None = None

    def _ahora(self):
        return self.reloj.ahora() if self.reloj is not None else utcnow()

    def ejecutar(self, sugerencia_id: UUID, revisor_id: UUID) -> SugerenciaIA:
        sugerencia = self.sugerencias.obtener(sugerencia_id)
        if sugerencia is None:
            raise ErrorNoEncontrado(
                "NO_ENCONTRADO",
                "La sugerencia no existe",
                detalle={"sugerencia_id": str(sugerencia_id)},
            )
        if sugerencia.estado is not EstadoSugerencia.PENDIENTE:
            raise ErrorConflicto(
                "CONFLICTO_VERSION",
                "La sugerencia ya fue resuelta",
                detalle={"estado": sugerencia.estado.value},
            )
        if revisor_id is None:
            raise ErrorValidacion("CAMPO_OBLIGATORIO", "Se requiere un revisor humano")

        sugerencia.estado = EstadoSugerencia.ACEPTADA
        sugerencia.revisor_id = revisor_id
        sugerencia.resuelto_en = self._ahora()
        guardada = self.sugerencias.guardar(sugerencia)

        self.auditoria.registrar(
            EventoAuditoria(
                entidad=EntidadAuditoria.REGISTRO,
                entidad_id=sugerencia.registro_id,
                registro_id=sugerencia.registro_id,
                campo=sugerencia.campo,
                valor_anterior=None,
                valor_nuevo=sugerencia.valor_sugerido,
                usuario_id=revisor_id,
                fecha_hora=self._ahora(),
                motivo="Aprobación humana de sugerencia IA",
                origen=Origen.IA,
            )
        )
        if self.aplicador is not None:
            self.aplicador(guardada, revisor_id)
        return guardada


@dataclass
class DescartarSugerencia:
    """Descarte humano; no modifica el registro ni genera cambio auditado."""

    sugerencias: RepositorioSugerencias
    reloj: Reloj | None = None

    def ejecutar(self, sugerencia_id: UUID, revisor_id: UUID) -> SugerenciaIA:
        sugerencia = self.sugerencias.obtener(sugerencia_id)
        if sugerencia is None:
            raise ErrorNoEncontrado(
                "NO_ENCONTRADO",
                "La sugerencia no existe",
                detalle={"sugerencia_id": str(sugerencia_id)},
            )
        if sugerencia.estado is not EstadoSugerencia.PENDIENTE:
            raise ErrorConflicto(
                "CONFLICTO_VERSION", "La sugerencia ya fue resuelta"
            )
        sugerencia.estado = EstadoSugerencia.DESCARTADA
        sugerencia.revisor_id = revisor_id
        sugerencia.resuelto_en = (
            self.reloj.ahora() if self.reloj is not None else utcnow()
        )
        return self.sugerencias.guardar(sugerencia)


def resumen_por_etiqueta(sugerencias: Iterable[SugerenciaIA]) -> dict[str, int]:
    """Conteo por clasificación para la pantalla de sugerencias."""
    resumen: dict[str, int] = {}
    for sugerencia in sugerencias:
        resumen[sugerencia.etiqueta.value] = resumen.get(sugerencia.etiqueta.value, 0) + 1
    return resumen


__all__ = [
    "AceptarSugerencia",
    "AplicadorSugerencia",
    "DescartarSugerencia",
    "GenerarSugerencias",
    "Hallazgo",
    "detectar_contradicciones",
    "resumen_por_etiqueta",
]
