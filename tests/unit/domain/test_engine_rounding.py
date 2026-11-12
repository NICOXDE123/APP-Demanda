"""Prorrateo, redondeo y vigencias del motor (T065).

Complementa los casos C-01 a C-08 con las reglas de §10.2, §10.8 y RN-47 a
RN-52: redondeo half-up al final del registro-mes, fracción activa por días,
cierre de HC no negativo y horas con vigencia mensual.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from proyecta.domain.engine.active_fraction import dias_activos, fraccion_activa
from proyecta.domain.engine.base import calcular_base, detallar_base
from proyecta.domain.engine.gap import evaluar_gap
from proyecta.domain.engine.headcount import grilla_hc
from proyecta.domain.engine.vigencias import ResolutorVigencias, resolver_horas
from proyecta.domain.entities import (
    AjusteHC,
    Parametro,
    Perfil,
    TarifaPerfil,
    VigenciaEstadoCalculo,
)
from proyecta.domain.enums import (
    CampoVigencia,
    MotivoCierre,
    TipoAjuste,
    TipoParametro,
)
from proyecta.domain.errors import (
    ErrorHCNegativo,
    ErrorValidacion,
    ErrorRango,
)
from proyecta.domain.value_objects import (
    DateRange,
    Money,
    Percentage,
    Period,
    redondear_clp,
)


def test_redondeo_half_up_a_clp() -> None:
    assert redondear_clp(Decimal("1.4")) == 1
    assert redondear_clp(Decimal("1.5")) == 2
    assert redondear_clp(Decimal("2.5")) == 3
    assert redondear_clp(Decimal("1403999.49")) == 1_403_999
    assert redondear_clp(Decimal("1403999.50")) == 1_404_000
    assert redondear_clp(7) == 7


def test_money_y_porcentajes_validan_y_convierten() -> None:
    assert Money.desde_decimal(Decimal("631800.5")).clp == 631_801
    assert Money(0) + Money(10) == Money(10)
    with pytest.raises(ErrorValidacion):
        Money(1.5)  # type: ignore[arg-type]

    assert Percentage.desde_porcentaje("88,2").bp == 8_820
    assert Percentage.desde_decimal("0.9").bp == 9_000
    assert Percentage.desde_porcentaje(100).a_decimal() == Decimal(1)
    with pytest.raises(ErrorValidacion):
        Percentage.desde_decimal("1.2")
    with pytest.raises(ErrorValidacion):
        Percentage(10_001)


def test_periodo_y_rango_de_fechas() -> None:
    assert str(Period(2026, 1)) == "2026-01"
    assert Period.desde_texto("2026-02").dias == 28
    assert Period(2026, 1).siguiente() == Period(2026, 2)
    assert Period(2026, 1).anterior() == Period(2025, 12)
    assert [str(mes) for mes in Period.serie(Period(2025, 11), 3)] == [
        "2025-11",
        "2025-12",
        "2026-01",
    ]
    with pytest.raises(ErrorValidacion):
        Period.desde_texto("2026-13")

    rango = DateRange(date(2026, 1, 10), date(2026, 1, 20))
    assert rango.dias_solapados(Period(2026, 1)) == 11
    assert rango.contiene(date(2026, 1, 15)) is True
    assert rango.fraccion_activa(Period(2026, 1)) == Decimal(11) / Decimal(31)
    with pytest.raises(ErrorValidacion):
        DateRange(date(2026, 2, 1), date(2026, 1, 1))


def test_fraccion_activa_por_dias_y_fin_exclusivo_del_perfil() -> None:
    perfil = Perfil(hc=4, fecha_ingreso=date(2026, 11, 16))
    assert dias_activos(perfil.fecha_ingreso, perfil.fecha_fin, Period(2026, 11)) == 15
    assert fraccion_activa(perfil, Period(2026, 11)) == Decimal(15) / Decimal(30)

    # ``fecha_fin`` es el primer día sin actividad: todo febrero sigue activo.
    perfil_activo = Perfil(
        hc=1, fecha_ingreso=date(2026, 1, 1), fecha_fin=date(2026, 3, 1)
    )
    assert fraccion_activa(perfil_activo, Period(2026, 2)) == Decimal(1)

    perfil_baja = Perfil(
        hc=1, fecha_ingreso=date(2026, 1, 1), fecha_fin=date(2026, 2, 10)
    )
    assert dias_activos(perfil_baja.fecha_ingreso, perfil_baja.fecha_fin, Period(2026, 2)) == 9


def test_redondeo_al_final_del_registro_mes() -> None:
    marzo = Period(2026, 3)
    perfiles = [
        Perfil(hc=1, fecha_ingreso=date(2026, 3, 17)),
        Perfil(hc=1, fecha_ingreso=date(2026, 3, 17)),
    ]
    tarifas = {
        perfil.id: [
            TarifaPerfil(
                perfil_id=perfil.id,
                tarifa_hora_centavos=260_001,
                vigente_desde=date(2026, 3, 1),
            )
        ]
        for perfil in perfiles
    }

    detalle = detallar_base(perfiles, tarifas, 180, marzo)
    suma_componentes = sum(componente.subtotal_clp for componente in detalle.componentes)

    assert detalle.total_clp == 452_905
    assert suma_componentes == 452_904  # cada componente redondeado por separado
    assert detalle.total_clp != suma_componentes


def test_grilla_hc_altas_bajas_y_cierre() -> None:
    perfiles = [
        Perfil(hc=3, fecha_ingreso=date(2026, 1, 1)),
        Perfil(hc=2, fecha_ingreso=date(2026, 2, 1)),
        Perfil(hc=1, fecha_ingreso=date(2026, 1, 1), fecha_fin=date(2026, 3, 1)),
    ]
    ajustes = [
        AjusteHC(
            mes=date(2026, 2, 1),
            tipo=TipoAjuste.ALTA,
            cantidad=1,
            motivo="Ajuste",
        )
    ]
    serie = grilla_hc(perfiles, Period.serie(Period(2026, 1), 4), ajustes=ajustes)

    assert [(fila.altas, fila.bajas, fila.cierre) for fila in serie] == [
        (4, 0, 4),
        (3, 0, 7),
        (0, 1, 6),
        (0, 0, 6),
    ]


def test_grilla_hc_bloquea_cierre_negativo() -> None:
    perfiles = [Perfil(hc=1, fecha_ingreso=date(2026, 1, 1))]
    ajustes = [AjusteHC(mes=date(2026, 1, 1), tipo=TipoAjuste.BAJA, cantidad=2, motivo="x")]
    with pytest.raises(ErrorHCNegativo):
        grilla_hc(perfiles, [Period(2026, 1)], ajustes=ajustes)


def test_horas_con_vigencia_mensual_sin_reescribir_el_pasado() -> None:
    parametros = [
        Parametro(
            clave="horas_mensuales",
            valor=180,
            tipo=TipoParametro.ENTERO,
            vigente_desde=date(2026, 1, 1),
        ),
        Parametro(
            clave="horas_mensuales",
            valor=160,
            tipo=TipoParametro.ENTERO,
            vigente_desde=date(2026, 4, 1),
        ),
    ]

    assert resolver_horas(parametros, Period(2026, 3)) == Decimal(180)
    assert resolver_horas(parametros, Period(2026, 4)) == Decimal(160)
    assert resolver_horas(parametros, Period(2025, 12)) == Decimal(180)


def test_vigencias_de_probabilidad_y_confiabilidad_por_mes() -> None:
    perfil = Perfil(hc=1, fecha_ingreso=date(2026, 1, 1))
    tarifa = TarifaPerfil(
        perfil_id=perfil.id,
        tarifa_hora_centavos=260_000,
        vigente_desde=date(2026, 1, 1),
    )
    from proyecta.domain.entities import Registro
    from proyecta.domain.enums import Estado, Flujo, Tipo

    registro = Registro(
        codigo="OPD-0002",
        tipo=Tipo.DEMANDA,
        estado=Estado.ADJUDICADA,
        flujo=Flujo.PROPUESTA_ENTREGADA,
        probabilidad_bp=9_000,
        confiabilidad_bp=9_000,
    )
    vigencia = VigenciaEstadoCalculo(
        registro_id=registro.id,
        campo=CampoVigencia.CONFIABILIDAD,
        valor_bp=8_000,
        vigente_desde=date(2026, 4, 1),
        motivo="Baja de confiabilidad",
    )
    resolutor = ResolutorVigencias([vigencia])

    assert resolutor.confiabilidad(registro, Period(2026, 3)) == 9_000
    assert resolutor.confiabilidad(registro, Period(2026, 4)) == 8_000


def test_gap_sin_meta_no_se_calcula() -> None:
    resultado = evaluar_gap(meta_clp=0, forecast_clp=1_000_000)
    assert resultado.cobertura_pct is None
    assert resultado.semaforo == "SIN_META"
    assert resultado.gap_clp == -1_000_000
    with pytest.raises(ErrorRango):
        evaluar_gap(meta_clp=-1, forecast_clp=0)
