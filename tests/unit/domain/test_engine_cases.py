"""Casos de referencia del motor C-01 a C-08 (T064).

Cada caso reproduce la tabla §10.9 de ``docs/fuentes/requerimientos.md``. Si
alguno cambia, debe existir una decisión de negocio documentada.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from proyecta.domain.engine.gap import evaluar_gap
from proyecta.domain.engine.service import MotorCalculo
from proyecta.domain.entities import (
    Contrato,
    EntradaCalculo,
    Perfil,
    Registro,
    TarifaPerfil,
)
from proyecta.domain.enums import Estado, Flujo, Tipo
from proyecta.domain.value_objects import Period

ENERO = Period(2026, 1)
MESES_6 = Period.serie(ENERO, 6)


def registro(
    *,
    tipo: Tipo = Tipo.DEMANDA,
    estado: Estado = Estado.ADJUDICADA,
    flujo: Flujo = Flujo.PROPUESTA_ENTREGADA,
    probabilidad_bp: int = 9_000,
    confiabilidad_bp: int = 9_000,
) -> Registro:
    return Registro(
        codigo="OPD-0001",
        tipo=tipo,
        estado=estado,
        flujo=flujo,
        probabilidad_bp=probabilidad_bp,
        confiabilidad_bp=confiabilidad_bp,
        fecha_creacion=date(2025, 12, 1),
        fecha_ingreso=date(2026, 1, 1),
    )


def perfil(
    *,
    hc: int,
    tarifa_hora_clp: int,
    ingreso: date = date(2026, 1, 1),
    fin: date | None = None,
    dedicacion: int = 100,
) -> tuple[Perfil, TarifaPerfil]:
    creado = Perfil(
        hc=hc,
        dedicacion_pct=dedicacion,
        fecha_ingreso=ingreso,
        fecha_fin=fin,
    )
    tarifa = TarifaPerfil(
        perfil_id=creado.id,
        tarifa_hora_centavos=tarifa_hora_clp * 100,
        vigente_desde=ingreso,
    )
    return creado, tarifa


def calcular(reg: Registro, perfiles, meses=(ENERO,), contrato: Contrato | None = None):
    perfiles = list(perfiles)
    entrada = EntradaCalculo(
        registro=reg,
        perfiles=[item[0] for item in perfiles],
        tarifas={item[0].id: [item[1]] for item in perfiles},
        contrato=contrato,
    )
    return MotorCalculo().calcular_registro(entrada, list(meses))


def test_c01_base_y_mab_de_oportunidad_pendiente() -> None:
    reg = registro(
        tipo=Tipo.OPORTUNIDAD,
        estado=Estado.PENDIENTE,
        flujo=Flujo.PROPUESTA_ENTREGADA,
        probabilidad_bp=5_000,
        confiabilidad_bp=9_000,
    )
    resultado = calcular(reg, [perfil(hc=3, tarifa_hora_clp=2_600)])
    detalle = resultado.meses[0]

    assert detalle.base_clp == 1_404_000
    assert detalle.mab_clp == 631_800
    assert detalle.forecast_clp == 631_800
    assert detalle.backlog_clp == 0


def test_c02_misma_base_en_adjudicada_con_90_por_ciento() -> None:
    reg = registro(probabilidad_bp=9_000, confiabilidad_bp=9_000)
    detalle = calcular(reg, [perfil(hc=3, tarifa_hora_clp=2_600)]).meses[0]

    assert detalle.base_clp == 1_404_000
    assert detalle.mab_clp == 1_137_240


def test_c03_perfiles_seleccionados_al_100_por_ciento() -> None:
    reg = registro(
        estado=Estado.EN_CURSO,
        flujo=Flujo.PERFILES_SELECCIONADOS,
        probabilidad_bp=10_000,
        confiabilidad_bp=9_000,
    )
    detalle = calcular(reg, [perfil(hc=3, tarifa_hora_clp=2_600)]).meses[0]

    assert detalle.mab_clp == 1_263_600
    assert detalle.backlog_confirmado is True


def test_c04_dos_perfiles() -> None:
    reg = registro(
        estado=Estado.PENDIENTE,
        flujo=Flujo.PROPUESTA_ENTREGADA,
        probabilidad_bp=5_000,
        confiabilidad_bp=8_000,
    )
    detalle = calcular(
        reg,
        [
            perfil(hc=3, tarifa_hora_clp=2_600),
            perfil(hc=2, tarifa_hora_clp=2_300),
        ],
    ).meses[0]

    assert detalle.base_clp == 2_232_000
    assert detalle.mab_clp == 892_800
    assert len(detalle.componentes) == 2


def test_c05_prorrateo_de_ingreso_el_dia_16() -> None:
    reg = registro(
        estado=Estado.EN_CURSO,
        flujo=Flujo.PERFILES_SELECCIONADOS,
        probabilidad_bp=10_000,
        confiabilidad_bp=9_000,
    )
    noviembre = Period(2026, 11)
    detalle = calcular(
        reg,
        [perfil(hc=4, tarifa_hora_clp=2_600, ingreso=date(2026, 11, 16))],
        meses=(noviembre,),
    ).meses[0]

    assert detalle.componentes[0].dias_activos == 15
    assert detalle.base_clp == 936_000
    assert detalle.mab_clp == 842_400


def test_c06_continuidad_aporta_backlog_y_nunca_mab() -> None:
    reg = registro(
        tipo=Tipo.CONTINUIDAD,
        estado=Estado.EN_CURSO,
        flujo=Flujo.PERFILES_SELECCIONADOS,
        probabilidad_bp=10_000,
        confiabilidad_bp=10_000,
    )
    contrato = Contrato(
        registro_id=reg.id,
        codigo_contrato="CTR-0001",
        fecha_inicio=date(2026, 1, 1),
        fecha_fin=date(2026, 6, 30),
        monto_mensual_clp=45_000_000,
        hc_comprometido=10,
    )
    resultado = calcular(reg, [], meses=MESES_6, contrato=contrato)

    assert all(detalle.mab_clp == 0 for detalle in resultado.meses)
    assert all(detalle.backlog_clp == 45_000_000 for detalle in resultado.meses)
    assert sum(detalle.backlog_clp for detalle in resultado.meses) == 270_000_000


def test_c07_gap_y_cobertura_de_la_meta() -> None:
    resultado = evaluar_gap(meta_clp=1_700_000_000, forecast_clp=1_500_000_000)

    assert resultado.gap_clp == 200_000_000
    assert resultado.cobertura_pct == Decimal("88.2")
    assert resultado.semaforo == "ROJO"


def test_c08_cambio_de_confiabilidad_reduce_la_mab() -> None:
    reg90 = registro(probabilidad_bp=9_000, confiabilidad_bp=9_000)
    reg80 = registro(probabilidad_bp=9_000, confiabilidad_bp=8_000)
    perfil_unico = [perfil(hc=3, tarifa_hora_clp=2_600)]

    antes = calcular(reg90, perfil_unico).meses[0].mab_clp
    despues = calcular(reg80, perfil_unico).meses[0].mab_clp

    assert antes == 1_137_240
    assert despues == 1_010_880
    assert despues - antes == -126_360


def test_ac05_probabilidad_100_no_se_suma_tambien_al_backlog() -> None:
    reg = registro(
        estado=Estado.EN_CURSO,
        flujo=Flujo.PERFILES_SELECCIONADOS,
        probabilidad_bp=10_000,
        confiabilidad_bp=9_000,
    )
    detalle = calcular(reg, [perfil(hc=3, tarifa_hora_clp=2_600)]).meses[0]

    assert detalle.backlog_clp == 0
    assert detalle.mab_clp == detalle.forecast_clp


def test_un_registro_pertenece_a_una_sola_bolsa_por_mes() -> None:
    demanda = registro(estado=Estado.EN_CURSO, flujo=Flujo.PERFILES_SELECCIONADOS)
    continuidad = registro(tipo=Tipo.CONTINUIDAD, estado=Estado.EN_CURSO, flujo=Flujo.PERFILES_SELECCIONADOS)
    contrato = Contrato(
        registro_id=continuidad.id,
        codigo_contrato="CTR-0002",
        fecha_inicio=date(2026, 1, 1),
        fecha_fin=date(2026, 12, 31),
        monto_mensual_clp=10_000_000,
        hc_comprometido=3,
    )

    detalle_demanda = calcular(demanda, [perfil(hc=1, tarifa_hora_clp=2_000)]).meses[0]
    detalle_continuidad = calcular(
        continuidad, [], contrato=contrato
    ).meses[0]

    assert (detalle_demanda.mab_clp > 0) != (detalle_demanda.backlog_clp > 0)
    assert (detalle_continuidad.mab_clp > 0) != (detalle_continuidad.backlog_clp > 0)
    assert detalle_demanda.mab_clp + detalle_demanda.backlog_clp == detalle_demanda.forecast_clp
