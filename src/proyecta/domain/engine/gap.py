"""Meta, Gap y cobertura por sector y mes (T071, §10.6).

``Gap = Meta − Forecast`` y ``Cobertura = Forecast / Meta`` cuando la meta es
positiva. Gap positivo significa brecha (rojo); negativo, exceso (verde).
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

from proyecta.domain.errors import ErrorRango

UN_DECIMO = Decimal("0.1")


@dataclass(frozen=True, slots=True)
class GapResultado:
    meta_clp: int
    forecast_clp: int
    gap_clp: int
    cobertura_pct: Decimal | None
    semaforo: str

    @property
    def cumple_meta(self) -> bool:
        return self.gap_clp <= 0


def calcular_gap(meta_clp: int, forecast_clp: int) -> int:
    """Diferencia entre meta y Forecast en CLP entero."""
    if meta_clp < 0 or forecast_clp < 0:
        raise ErrorRango("RANGO_INVALIDO", "Meta y Forecast no pueden ser negativos")
    return meta_clp - forecast_clp


def calcular_cobertura(meta_clp: int, forecast_clp: int) -> Decimal | None:
    """Cobertura en porcentaje (0–100+) redondeada a un decimal.

    Devuelve ``None`` cuando no hay meta: el gap no se calcula y se activa
    ``DQ-12`` (US5, escenario 4).
    """
    if meta_clp < 0 or forecast_clp < 0:
        raise ErrorRango("RANGO_INVALIDO", "Meta y Forecast no pueden ser negativos")
    if meta_clp == 0:
        return None
    cobertura = (Decimal(forecast_clp) / Decimal(meta_clp)) * Decimal(100)
    return cobertura.quantize(UN_DECIMO, rounding=ROUND_HALF_UP)


def semaforo(cobertura_pct: Decimal | None) -> str:
    """Semáforo simple: rojo bajo 100 %, verde desde 100 %."""
    if cobertura_pct is None:
        return "SIN_META"
    return "ROJO" if cobertura_pct < Decimal(100) else "VERDE"


def evaluar_gap(meta_clp: int, forecast_clp: int) -> GapResultado:
    """Resultado completo de Gap para un sector-mes."""
    cobertura = calcular_cobertura(meta_clp, forecast_clp)
    return GapResultado(
        meta_clp=meta_clp,
        forecast_clp=forecast_clp,
        gap_clp=calcular_gap(meta_clp, forecast_clp),
        cobertura_pct=cobertura,
        semaforo=semaforo(cobertura),
    )


__all__ = ["GapResultado", "calcular_cobertura", "calcular_gap", "evaluar_gap", "semaforo"]
