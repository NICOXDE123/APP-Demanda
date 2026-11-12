"""HC proyectado y grilla Altas/Bajas/Cierre (T070, §10.5, RN-47 a RN-51).

``Cierre(r,m) = Cierre(r,m−1) + Altas(r,m) − Bajas(r,m)``

Un perfil con baja en el mes no suma al cierre de ese mes, pero sí genera el
monto de los días trabajados (eso lo resuelve ``active_fraction``). El cierre
no puede ser negativo (RN-48).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Iterable, Sequence

from proyecta.domain.entities import AjusteHC, Perfil
from proyecta.domain.enums import TipoAjuste
from proyecta.domain.errors import ErrorHCNegativo
from proyecta.domain.value_objects import Period


@dataclass(frozen=True, slots=True)
class CierreMes:
    """Dotación al cierre de un mes con sus movimientos."""

    mes: Period
    altas: int
    bajas: int
    cierre: int

    @property
    def neto(self) -> int:
        return self.altas - self.bajas


def hc_al_cierre(perfiles: Sequence[Perfil], mes: Period) -> int:
    """Perfiles activos al último día del mes (``fin`` es el primer día sin actividad)."""
    total = 0
    for perfil in perfiles:
        if perfil.fecha_ingreso > mes.fin:
            continue
        if perfil.fecha_fin is not None and perfil.fecha_fin <= mes.fin:
            continue
        total += perfil.hc
    return total


def hc_actual(perfiles: Sequence[Perfil], fecha: date) -> int:
    """HC activo a una fecha de consulta (RN-46)."""
    return sum(
        perfil.hc
        for perfil in perfiles
        if perfil.fecha_ingreso <= fecha
        and (perfil.fecha_fin is None or perfil.fecha_fin > fecha)
    )


def grilla_hc(
    perfiles: Sequence[Perfil],
    meses: Iterable[Period],
    *,
    ajustes: Sequence[AjusteHC] = (),
    cierre_inicial: int = 0,
) -> list[CierreMes]:
    """Serie de cierre mensual de HC para un registro."""
    if cierre_inicial < 0:
        raise ErrorHCNegativo(
            "HC_NEGATIVO", "El cierre inicial de HC no puede ser negativo"
        )

    serie: list[CierreMes] = []
    cierre = cierre_inicial
    for mes in meses:
        altas = sum(
            perfil.hc
            for perfil in perfiles
            if Period.desde_fecha(perfil.fecha_ingreso) == mes
        ) + sum(
            ajuste.cantidad
            for ajuste in ajustes
            if ajuste.tipo is TipoAjuste.ALTA and Period.desde_fecha(ajuste.mes) == mes
        )
        bajas = sum(
            perfil.hc
            for perfil in perfiles
            if perfil.fecha_fin is not None and Period.desde_fecha(perfil.fecha_fin) == mes
        ) + sum(
            ajuste.cantidad
            for ajuste in ajustes
            if ajuste.tipo is TipoAjuste.BAJA and Period.desde_fecha(ajuste.mes) == mes
        )
        cierre = cierre + altas - bajas
        if cierre < 0:
            raise ErrorHCNegativo(
                "HC_NEGATIVO",
                f"El cierre de HC de {mes} es negativo",
                detalle={"mes": str(mes), "cierre": cierre},
            )
        serie.append(CierreMes(mes=mes, altas=altas, bajas=bajas, cierre=cierre))
    return serie


def grado_certeza(estado: str, tipo: str) -> str:
    """Agrupa el HC por grado de certeza (RN-51).

    Recibe los códigos para no acoplar el motor a enums de presentación.
    """
    if estado in ("EN_CURSO",) or tipo == "CONTINUIDAD":
        return "CONFIRMADO"
    if estado == "ADJUDICADA":
        return "POR_CONFIRMAR"
    return "OPORTUNIDAD"


__all__ = [
    "CierreMes",
    "grado_certeza",
    "grilla_hc",
    "hc_al_cierre",
    "hc_actual",
]
