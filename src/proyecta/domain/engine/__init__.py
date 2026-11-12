"""Motor de cálculo de Proyecta (Base, MAB, Backlog, Forecast, HC y Gap)."""

from proyecta.domain.engine.bags import (
    bolsa_de,
    calcular_backlog,
    calcular_mab,
    es_backlog_confirmado,
    limite_actividad,
    mes_en_calculo,
)
from proyecta.domain.engine.gap import GapResultado, evaluar_gap
from proyecta.domain.engine.headcount import CierreMes, grilla_hc, hc_actual
from proyecta.domain.engine.service import (
    DetalleRegistroMes,
    ImpactoCalculo,
    MotorCalculo,
    ResultadoProyeccion,
    ResultadoRegistro,
    SerieMes,
    comparar_impacto,
)
from proyecta.domain.engine.vigencias import ResolutorVigencias

__all__ = [
    "CierreMes",
    "DetalleRegistroMes",
    "GapResultado",
    "ImpactoCalculo",
    "MotorCalculo",
    "ResolutorVigencias",
    "ResultadoProyeccion",
    "ResultadoRegistro",
    "SerieMes",
    "bolsa_de",
    "calcular_backlog",
    "calcular_mab",
    "comparar_impacto",
    "es_backlog_confirmado",
    "evaluar_gap",
    "grilla_hc",
    "hc_actual",
    "limite_actividad",
    "mes_en_calculo",
]
