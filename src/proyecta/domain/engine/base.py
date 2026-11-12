"""Base mensual de un registro (T068, §10.3).

``Base(r,m) = Σ_p [hc × dedicación × tarifa vigente × horas del mes × activo]``

El cálculo se hace en ``Decimal`` y se redondea una sola vez al final del
registro-mes (RN-86). Las horas son un parámetro con vigencia (S-01).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Mapping, Sequence
from uuid import UUID

from proyecta.domain.engine.active_fraction import dias_activos, fraccion_activa
from proyecta.domain.entities import Perfil, TarifaPerfil
from proyecta.domain.errors import ErrorTarifaNoVigente
from proyecta.domain.value_objects import Period, redondear_clp


@dataclass(frozen=True, slots=True)
class ComponenteBase:
    """Aporte de un perfil a la base del registro-mes."""

    perfil_id: UUID
    nombre_perfil_id: UUID | None
    hc: int
    dedicacion_pct: int
    tarifa_hora_centavos: int
    dias_activos: int
    fraccion_activa: Decimal
    subtotal: Decimal

    @property
    def subtotal_clp(self) -> int:
        return redondear_clp(self.subtotal)


@dataclass(frozen=True, slots=True)
class DetalleBase:
    mes: Period
    componentes: tuple[ComponenteBase, ...]
    total: Decimal
    advertencias: tuple[str, ...] = ()

    @property
    def total_clp(self) -> int:
        return redondear_clp(self.total)


def tarifa_vigente(
    tarifas: Sequence[TarifaPerfil], mes: Period
) -> TarifaPerfil | None:
    """Tarifa aplicable al mes; gana la más reciente que solape el período.

    Se compara contra el mes completo (no solo el día 1) porque un perfil puede
    ingresar a mitad de mes y su primera tarifa rige desde esa fecha. El
    prorrateo de días lo resuelve ``fraccion_activa``.
    """
    candidatas = [
        tarifa
        for tarifa in tarifas
        if tarifa.vigente_desde <= mes.fin
        and (tarifa.vigente_hasta is None or tarifa.vigente_hasta >= mes.inicio)
    ]
    if not candidatas:
        return None
    return max(candidatas, key=lambda tarifa: tarifa.vigente_desde)


def detallar_base(
    perfiles: Sequence[Perfil],
    tarifas_por_perfil: Mapping[UUID, Sequence[TarifaPerfil]],
    horas_mes: Decimal | int,
    mes: Period,
    *,
    limite: date | None = None,
    estricto: bool = True,
) -> DetalleBase:
    """Calcula la base con el detalle por perfil y advertencias de datos faltantes."""
    horas = Decimal(horas_mes)
    componentes: list[ComponenteBase] = []
    advertencias: list[str] = []

    for perfil in perfiles:
        tarifa = tarifa_vigente(tarifas_por_perfil.get(perfil.id, ()), mes)
        fraccion = fraccion_activa(perfil, mes, limite)
        if fraccion == 0:
            continue
        if tarifa is None:
            mensaje = f"El perfil {perfil.id} no tiene tarifa vigente en {mes}"
            if estricto:
                raise ErrorTarifaNoVigente(
                    "TARIFA_NO_VIGENTE",
                    mensaje,
                    detalle={"perfil_id": str(perfil.id), "mes": str(mes)},
                )
            advertencias.append(mensaje)
            continue

        subtotal = (
            Decimal(perfil.hc)
            * (Decimal(perfil.dedicacion_pct) / Decimal(100))
            * (Decimal(tarifa.tarifa_hora_centavos) / Decimal(100))
            * horas
            * fraccion
        )
        componentes.append(
            ComponenteBase(
                perfil_id=perfil.id,
                nombre_perfil_id=perfil.nombre_perfil_id,
                hc=perfil.hc,
                dedicacion_pct=perfil.dedicacion_pct,
                tarifa_hora_centavos=tarifa.tarifa_hora_centavos,
                dias_activos=dias_activos(perfil.fecha_ingreso, perfil.fecha_fin, mes, limite),
                fraccion_activa=fraccion,
                subtotal=subtotal,
            )
        )

    total = sum((componente.subtotal for componente in componentes), Decimal(0))
    return DetalleBase(
        mes=mes,
        componentes=tuple(componentes),
        total=total,
        advertencias=tuple(advertencias),
    )


def calcular_base(
    perfiles: Sequence[Perfil],
    tarifas_por_perfil: Mapping[UUID, Sequence[TarifaPerfil]],
    horas_mes: Decimal | int,
    mes: Period,
    *,
    limite: date | None = None,
    estricto: bool = True,
) -> Decimal:
    """Base mensual sin redondear; el redondeo ocurre en el motor."""
    return detallar_base(
        perfiles,
        tarifas_por_perfil,
        horas_mes,
        mes,
        limite=limite,
        estricto=estricto,
    ).total


def tarifa_media(perfiles: Sequence[Perfil], tarifas_por_perfil: Mapping[UUID, Sequence[TarifaPerfil]], mes: Period) -> Decimal | None:
    """Tarifa media ponderada por HC vigente en el mes (RN-45)."""
    suma_hc = 0
    suma = Decimal(0)
    for perfil in perfiles:
        if fraccion_activa(perfil, mes) == 0:
            continue
        tarifa = tarifa_vigente(tarifas_por_perfil.get(perfil.id, ()), mes)
        if tarifa is None:
            continue
        suma_hc += perfil.hc
        suma += Decimal(perfil.hc) * (Decimal(tarifa.tarifa_hora_centavos) / Decimal(100))
    if suma_hc == 0:
        return None
    return suma / Decimal(suma_hc)


__all__ = [
    "ComponenteBase",
    "DetalleBase",
    "calcular_base",
    "detallar_base",
    "tarifa_media",
    "tarifa_vigente",
]
