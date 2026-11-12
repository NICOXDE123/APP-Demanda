"""Fracción activa por días de un perfil o contrato en un mes (T067, §10.2).

``fecha_fin`` es el primer día sin actividad; por eso se resta un día para
contar el último día trabajado. El prorrateo aplica solo a montos; el HC al
cierre se calcula en ``headcount.py`` (RN-50).
"""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

from proyecta.domain.entities import Contrato, Perfil
from proyecta.domain.value_objects import Period


def _ultimo_dia_activo(
    inicio: date,
    fin_exclusivo: date | None,
    mes: Period,
    limite: date | None = None,
) -> date:
    """Último día con actividad, acotado al mes y a un límite opcional."""
    ultimo = mes.fin
    if fin_exclusivo is not None:
        ultimo = min(ultimo, fin_exclusivo - timedelta(days=1))
    if limite is not None:
        ultimo = min(ultimo, limite)
    return ultimo


def dias_activos(
    inicio: date,
    fin_exclusivo: date | None,
    mes: Period,
    limite: date | None = None,
) -> int:
    """Días del mes con actividad, entre 0 y los días del mes."""
    desde = max(inicio, mes.inicio)
    hasta = _ultimo_dia_activo(inicio, fin_exclusivo, mes, limite)
    if hasta < desde:
        return 0
    return (hasta - desde).days + 1


def fraccion_activa(
    perfil: Perfil,
    mes: Period,
    limite: date | None = None,
) -> Decimal:
    """Fracción 0–1 del mes en que el perfil está activo."""
    dias = dias_activos(perfil.fecha_ingreso, perfil.fecha_fin, mes, limite)
    return Decimal(dias) / Decimal(mes.dias)


def _fin_exclusivo_contrato(contrato: Contrato) -> date | None:
    """En contratos ``fecha_fin`` es el último día cubierto (a diferencia del perfil)."""
    if contrato.es_indefinido or contrato.fecha_fin is None:
        return None
    return contrato.fecha_fin + timedelta(days=1)


def fraccion_activa_contrato(
    contrato: Contrato,
    mes: Period,
    limite: date | None = None,
) -> Decimal:
    """Fracción del mes cubierta por el contrato de continuidad."""
    dias = dias_activos(
        contrato.fecha_inicio, _fin_exclusivo_contrato(contrato), mes, limite
    )
    return Decimal(dias) / Decimal(mes.dias)


def dias_activos_contrato(
    contrato: Contrato,
    mes: Period,
    limite: date | None = None,
) -> int:
    return dias_activos(
        contrato.fecha_inicio, _fin_exclusivo_contrato(contrato), mes, limite
    )


__all__ = [
    "dias_activos",
    "dias_activos_contrato",
    "fraccion_activa",
    "fraccion_activa_contrato",
]
