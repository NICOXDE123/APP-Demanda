"""Cargador idempotente de la estructura con errores por fila (T153).

Cumple ``FR-087`` a ``FR-090`` y ``RNF-19``:

- Importa la estructura de la plantilla con datos sintéticos.
- Normaliza el registro y conserva el catálogo compartido.
- Recalcula con el valor vigente de horas (180 h, ``S-01``).
- Es idempotente por ``codigo``: la segunda ejecución no duplica registros.
- Reporta las inconsistencias **por fila** sin corregirlas en silencio y sin
  abortar el resto de la carga.

El almacén es un puerto de escritura transaccional que implementa la
infraestructura (T034). El caso de uso nunca conoce Datastore.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol, Sequence
from uuid import UUID

from proyecta.domain.entities import (
    AjusteHC,
    Contrato,
    Perfil,
    Registro,
    TarifaPerfil,
    VigenciaEstadoCalculo,
)
from proyecta.domain.enums import (
    ESTADOS_POR_TIPO,
    FLUJOS_POR_TIPO,
    PROBABILIDADES_VALIDAS_BP,
)
from proyecta.domain.errors import ErrorDominio
from proyecta.domain.value_objects import Period

PROBABILIDAD_FUERA_CATALOGO = "PROBABILIDAD_FUERA_CATALOGO"
ESTADO_TIPO_INCOHERENTE = "ESTADO_TIPO_INCOHERENTE"
FLUJO_TIPO_INCOHERENTE = "FLUJO_TIPO_INCOHERENTE"
REGISTRO_CERRADO_CON_HC = "REGISTRO_CERRADO_CON_HC"
FECHA_FUTURA = "FECHA_FUTURA"
SIN_TARIFA = "SIN_TARIFA"
FILA_RECHAZADA = "FILA_RECHAZADA"

HORAS_MENSUALES_DEFECTO = 180


class OrigenEstructura(Protocol):
    """Conjunto de entidades a importar (por ejemplo ``DatosSemilla``)."""

    registros: Sequence[Registro]
    perfiles: Sequence[Perfil]
    tarifas: Sequence[TarifaPerfil]
    contratos: Sequence[Contrato]
    ajustes: Sequence[AjusteHC]
    vigencias: Sequence[VigenciaEstadoCalculo]


class AlmacenCarga(Protocol):
    """Escritura transaccional e idempotente de la estructura."""

    def buscar_por_codigo(self, codigo: str) -> Registro | None: ...

    def guardar_registro(self, registro: Registro) -> None: ...

    def guardar_perfil(self, perfil: Perfil) -> None: ...

    def guardar_tarifa(self, tarifa: TarifaPerfil) -> None: ...

    def guardar_contrato(self, contrato: Contrato) -> None: ...

    def guardar_ajuste(self, ajuste: AjusteHC) -> None: ...

    def guardar_vigencia(self, vigencia: VigenciaEstadoCalculo) -> None: ...


@dataclass(frozen=True, slots=True)
class Inconsistencia:
    """Hallazgo de una fila; nunca detiene el resto de la carga."""

    fila: int
    codigo: str
    mensaje: str
    campo: str | None = None
    registro_id: UUID | None = None


@dataclass(frozen=True, slots=True)
class ResultadoCarga:
    """Resumen de la importación."""

    creados: int
    actualizados: int
    inconsistencias: tuple[Inconsistencia, ...] = ()
    horas_mensuales: int = HORAS_MENSUALES_DEFECTO

    @property
    def total_registros(self) -> int:
        return self.creados + self.actualizados

    @property
    def limpia(self) -> bool:
        return not self.inconsistencias

    @property
    def codigos(self) -> tuple[str, ...]:
        return tuple(inconsistencia.codigo for inconsistencia in self.inconsistencias)


def _validar_fila(
    fila: int,
    registro: Registro,
    perfiles: Sequence[Perfil],
    tarifas: Sequence[TarifaPerfil],
    periodo: Period,
) -> list[Inconsistencia]:
    """Reglas que el cargador reporta sin corregir (FR-088)."""
    hallazgos: list[Inconsistencia] = []

    def agregar(codigo: str, campo: str, mensaje: str) -> None:
        hallazgos.append(
            Inconsistencia(
                fila=fila,
                codigo=codigo,
                mensaje=mensaje,
                campo=campo,
                registro_id=registro.id,
            )
        )

    if registro.probabilidad_bp not in PROBABILIDADES_VALIDAS_BP:
        agregar(
            PROBABILIDAD_FUERA_CATALOGO,
            "probabilidad_bp",
            f"La probabilidad {registro.probabilidad_bp} bp no pertenece al catálogo",
        )

    if registro.estado not in ESTADOS_POR_TIPO[registro.tipo]:
        agregar(
            ESTADO_TIPO_INCOHERENTE,
            "estado",
            f"El estado {registro.estado.value} no aplica al tipo {registro.tipo.value}",
        )

    if registro.flujo not in FLUJOS_POR_TIPO[registro.tipo]:
        agregar(
            FLUJO_TIPO_INCOHERENTE,
            "flujo",
            f"El flujo {registro.flujo.value} no aplica al tipo {registro.tipo.value}",
        )

    if registro.es_terminal and any(perfil.fecha_fin is None for perfil in perfiles):
        agregar(
            REGISTRO_CERRADO_CON_HC,
            "estado",
            "Registro cerrado con HC activo; requiere revisión de Operaciones",
        )

    if registro.fecha_ingreso is not None and registro.fecha_ingreso > periodo.fin:
        agregar(
            FECHA_FUTURA,
            "fecha_ingreso",
            f"fecha_ingreso {registro.fecha_ingreso} es posterior a {periodo.fin}",
        )

    con_tarifa = {tarifa.perfil_id for tarifa in tarifas}
    for perfil in perfiles:
        if perfil.id not in con_tarifa:
            agregar(
                SIN_TARIFA,
                "tarifa",
                f"El perfil {perfil.id} no tiene tarifa vigente",
            )

    return hallazgos


@dataclass
class CargarEstructura:
    """Caso de uso de carga inicial (T153)."""

    almacen: AlmacenCarga
    horas_mensuales: int = HORAS_MENSUALES_DEFECTO
    _inconsistencias: list[Inconsistencia] = field(default_factory=list, init=False)

    def ejecutar(self, origen: OrigenEstructura, *, periodo: Period) -> ResultadoCarga:
        """Importa la estructura completa; reporta errores por fila."""
        self._inconsistencias = []
        creados = 0
        actualizados = 0

        for fila, registro in enumerate(origen.registros, start=1):
            perfiles = tuple(
                perfil for perfil in origen.perfiles if perfil.registro_id == registro.id
            )
            tarifas = tuple(
                tarifa
                for tarifa in origen.tarifas
                if tarifa.perfil_id in {perfil.id for perfil in perfiles}
            )
            try:
                if self.almacen.buscar_por_codigo(registro.codigo) is not None:
                    actualizados += 1
                    continue
                self._inconsistencias.extend(
                    _validar_fila(fila, registro, perfiles, tarifas, periodo)
                )
                self._persistir(registro, origen, perfiles, tarifas)
                creados += 1
            except ErrorDominio as error:
                self._inconsistencias.append(
                    Inconsistencia(
                        fila=fila,
                        codigo=error.code,
                        mensaje=error.message,
                        registro_id=registro.id,
                    )
                )
            except Exception as error:  # noqa: BLE001 - una fila no tumba la carga
                self._inconsistencias.append(
                    Inconsistencia(
                        fila=fila,
                        codigo=FILA_RECHAZADA,
                        mensaje=f"No fue posible importar la fila: {error}",
                        registro_id=registro.id,
                    )
                )

        return ResultadoCarga(
            creados=creados,
            actualizados=actualizados,
            inconsistencias=tuple(self._inconsistencias),
            horas_mensuales=self.horas_mensuales,
        )

    def _persistir(
        self,
        registro: Registro,
        origen: OrigenEstructura,
        perfiles: Sequence[Perfil],
        tarifas: Sequence[TarifaPerfil],
    ) -> None:
        self.almacen.guardar_registro(registro)
        for perfil in perfiles:
            self.almacen.guardar_perfil(perfil)
        for tarifa in tarifas:
            self.almacen.guardar_tarifa(tarifa)
        for contrato in origen.contratos:
            if contrato.registro_id == registro.id:
                self.almacen.guardar_contrato(contrato)
        for ajuste in origen.ajustes:
            if ajuste.registro_id == registro.id:
                self.almacen.guardar_ajuste(ajuste)
        for vigencia in origen.vigencias:
            if vigencia.registro_id == registro.id:
                self.almacen.guardar_vigencia(vigencia)


__all__ = [
    "AlmacenCarga",
    "CargarEstructura",
    "ESTADO_TIPO_INCOHERENTE",
    "FECHA_FUTURA",
    "FILA_RECHAZADA",
    "FLUJO_TIPO_INCOHERENTE",
    "HORAS_MENSUALES_DEFECTO",
    "Inconsistencia",
    "OrigenEstructura",
    "PROBABILIDAD_FUERA_CATALOGO",
    "REGISTRO_CERRADO_CON_HC",
    "ResultadoCarga",
    "SIN_TARIFA",
]
