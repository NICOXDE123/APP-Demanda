"""Auditoría con impacto en MAB y Forecast (T077).

Este módulo es aditivo al servicio de auditoría de la fundación (T029). Aporta
el cálculo del impacto que exige el motor y una función explícita para aceptar
sugerencias de IA con origen ``IA`` (FR-082). La auditoría es de solo inserción:
no hay métodos de actualización ni borrado.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any
from uuid import UUID

from proyecta.application.ports import CambioAuditado, Reloj, RepositorioAuditoria
from proyecta.domain.engine.service import ImpactoCalculo, ResultadoRegistro, comparar_impacto
from proyecta.domain.entities import EventoAuditoria, utcnow
from proyecta.domain.enums import EntidadAuditoria, Origen


def impacto_de_cambio(
    antes: ResultadoRegistro, despues: ResultadoRegistro
) -> ImpactoCalculo:
    """Impacto agregado del horizonte en MAB y Forecast."""
    return comparar_impacto(antes, despues)


def evento_con_impacto(
    cambio: CambioAuditado,
    impacto: ImpactoCalculo | None = None,
    *,
    fecha_hora=None,
) -> EventoAuditoria:
    """Construye el evento de auditoría con los valores de impacto."""
    return EventoAuditoria(
        entidad=EntidadAuditoria(cambio.entidad),
        entidad_id=cambio.entidad_id,
        registro_id=cambio.registro_id or cambio.entidad_id,
        campo=cambio.campo,
        valor_anterior=cambio.valor_anterior,
        valor_nuevo=cambio.valor_nuevo,
        usuario_id=cambio.usuario_id,
        fecha_hora=fecha_hora or utcnow(),
        motivo=cambio.motivo,
        fecha_efectiva=cambio.fecha_efectiva,
        mab_antes=impacto.mab_antes if impacto else None,
        mab_despues=impacto.mab_despues if impacto else None,
        forecast_antes=impacto.forecast_antes if impacto else None,
        forecast_despues=impacto.forecast_despues if impacto else None,
        origen=cambio.origen,
    )


@dataclass
class ServicioAuditoria:
    """Registra cambios auditables, incluido el impacto en MAB/Forecast."""

    repositorio: RepositorioAuditoria
    reloj: Reloj | None = None

    def _ahora(self):
        return self.reloj.ahora() if self.reloj is not None else utcnow()

    def registrar(
        self,
        cambio: CambioAuditado,
        *,
        impacto: ImpactoCalculo | None = None,
    ) -> EventoAuditoria:
        evento = evento_con_impacto(cambio, impacto, fecha_hora=self._ahora())
        return self.repositorio.registrar(evento)

    def registrar_cambio_de_calculo(
        self,
        *,
        entidad: str,
        entidad_id: UUID,
        campo: str,
        valor_anterior: Any,
        valor_nuevo: Any,
        usuario_id: UUID,
        antes: ResultadoRegistro,
        despues: ResultadoRegistro,
        motivo: str | None = None,
        fecha_efectiva: date | None = None,
        registro_id: UUID | None = None,
    ) -> EventoAuditoria:
        """Audita un cambio que altera el cálculo, guardando el impacto."""
        cambio = CambioAuditado(
            entidad=entidad,
            entidad_id=entidad_id,
            campo=campo,
            valor_anterior=valor_anterior,
            valor_nuevo=valor_nuevo,
            usuario_id=usuario_id,
            motivo=motivo,
            fecha_efectiva=fecha_efectiva,
            registro_id=registro_id,
        )
        return self.registrar(cambio, impacto=impacto_de_cambio(antes, despues))

    def registrar_aceptacion_ia(
        self,
        *,
        sugerencia_id: UUID,
        registro_id: UUID,
        campo: str,
        valor_anterior: Any,
        valor_nuevo: Any,
        revisor_id: UUID,
        motivo: str = "Aprobación humana de sugerencia IA",
    ) -> EventoAuditoria:
        """Aceptar una sugerencia siempre genera auditoría con origen ``IA``."""
        evento = EventoAuditoria(
            entidad=EntidadAuditoria.REGISTRO,
            entidad_id=registro_id,
            registro_id=registro_id,
            campo=campo,
            valor_anterior=valor_anterior,
            valor_nuevo=valor_nuevo,
            usuario_id=revisor_id,
            fecha_hora=self._ahora(),
            motivo=motivo,
            origen=Origen.IA,
        )
        return self.repositorio.registrar(evento)


__all__ = ["ServicioAuditoria", "evento_con_impacto", "impacto_de_cambio"]
