"""Bolsas y Forecast (T069, §10.4).

Reglas centrales:

- ``Continuidad`` aporta al **Backlog contractual** y nunca a la MAB.
- ``Oportunidad`` y ``Demanda`` aportan a la **MAB**.
- El *Backlog confirmado* es una vista de la MAB con P=100; no se suma aparte.
- ``Forecast = Backlog contractual + MAB`` y cada registro pertenece a una
  sola bolsa por mes (RN-83).
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from proyecta.domain.engine.active_fraction import fraccion_activa_contrato
from proyecta.domain.entities import Contrato, Registro
from proyecta.domain.enums import (
    MOTIVOS_QUE_PRORRATEAN,
    Bucket,
    Estado,
    MotivoCierre,
    Tipo,
)
from proyecta.domain.value_objects import Period, redondear_clp


def limite_actividad(registro: Registro) -> date | None:
    """Fecha hasta la que el registro sigue aportando cuando su motivo prorratea.

    ``PERDIDA``, ``DESESTIMADA`` y ``DUPLICADO`` salen desde el mes de cierre;
    ``CANCELADA_CLIENTE`` y ``TERMINO_SERVICIO`` prorratean hasta su fecha
    (FR-005 y §8.5).
    """
    if registro.motivo_cierre not in MOTIVOS_QUE_PRORRATEAN:
        return None
    if registro.motivo_cierre is MotivoCierre.CANCELADA_CLIENTE:
        return registro.fecha_cancelacion or registro.fecha_cierre
    return registro.fecha_cierre


def mes_en_calculo(registro: Registro, mes: Period) -> bool:
    """Indica si el registro aporta en el mes, antes de prorratear por días."""
    if registro.estado is Estado.STANDBY:
        return False
    if registro.estado not in (Estado.CERRADA, Estado.CANCELADA):
        return True

    motivo = registro.motivo_cierre
    if motivo not in MOTIVOS_QUE_PRORRATEAN:
        # Sale del Forecast desde el mes de cierre hacia adelante.
        if registro.fecha_cierre is None:
            return False
        return mes < Period.desde_fecha(registro.fecha_cierre)

    limite = limite_actividad(registro)
    if limite is None:
        return False
    return mes <= Period.desde_fecha(limite)


def bolsa_de(registro: Registro) -> Bucket | None:
    """Bolsa exclusiva del registro; ``None`` si está fuera del cálculo."""
    if registro.estado is Estado.STANDBY:
        return None
    if registro.estado in (Estado.CERRADA, Estado.CANCELADA):
        if registro.motivo_cierre not in MOTIVOS_QUE_PRORRATEAN:
            return None
    if registro.tipo is Tipo.CONTINUIDAD:
        return Bucket.BACKLOG_CONTRACTUAL
    return Bucket.MAB


def es_backlog_confirmado(registro: Registro, probabilidad_bp: int) -> bool:
    """Vista de la MAB con P=100; se muestra, no se suma (RN-38, H-07)."""
    return bolsa_de(registro) is Bucket.MAB and probabilidad_bp >= 10_000


def calcular_mab(base_clp: int, probabilidad_bp: int, confiabilidad_bp: int) -> int:
    """``MAB = Base × P × C``, ya redondeada a CLP."""
    factor = (Decimal(probabilidad_bp) / Decimal(10_000)) * (
        Decimal(confiabilidad_bp) / Decimal(10_000)
    )
    return redondear_clp(Decimal(base_clp) * factor)


def calcular_backlog(
    registro: Registro,
    contrato: Contrato | None,
    base_clp: int,
    mes: Period,
    *,
    limite: date | None = None,
) -> int:
    """Backlog contractual del mes.

    Usa el monto mensual del contrato si existe; si no, la Base de los perfiles
    al 100 % (FR-031, RN-61).
    """
    if contrato is None or contrato.monto_mensual_clp is None:
        return base_clp
    fraccion = fraccion_activa_contrato(contrato, mes, limite)
    return redondear_clp(Decimal(contrato.monto_mensual_clp) * fraccion)


__all__ = [
    "bolsa_de",
    "calcular_backlog",
    "calcular_mab",
    "es_backlog_confirmado",
    "limite_actividad",
    "mes_en_calculo",
]
