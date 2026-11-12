"""Integración de la serie de 12 meses y vigencias (T066, T078, US3).

Cubre AC-17 (horas con vigencia), P/C con vigencia mensual, previsualización
sin persistencia y el contrato de ``GET /forecast``.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from proyecta.application.use_cases.calculo import CalcularProyeccion, FiltrosProyeccion
from proyecta.domain.entities import (
    Contrato,
    EntradaCalculo,
    Parametro,
    Perfil,
    Registro,
    TarifaPerfil,
    VigenciaEstadoCalculo,
)
from proyecta.domain.enums import (
    CampoVigencia,
    Estado,
    Flujo,
    Tipo,
    TipoParametro,
)
from proyecta.domain.value_objects import Period
from _fakes import (
    FakeRepositorioContratos,
    FakeRepositorioParametros,
    FakeRepositorioPerfiles,
    FakeRepositorioRegistros,
    FakeRepositorioVigencias,
    RelojFijo,
)


def _registro(
    *,
    codigo: str,
    tipo: Tipo = Tipo.DEMANDA,
    estado: Estado = Estado.EN_CURSO,
    flujo: Flujo = Flujo.PERFILES_SELECCIONADOS,
    probabilidad_bp: int = 10_000,
    confiabilidad_bp: int = 9_000,
    owner_id=None,
    sector_id=None,
) -> Registro:
    return Registro(
        codigo=codigo,
        tipo=tipo,
        estado=estado,
        flujo=flujo,
        probabilidad_bp=probabilidad_bp,
        confiabilidad_bp=confiabilidad_bp,
        owner_id=owner_id,
        sector_id=sector_id,
        fecha_creacion=date(2025, 12, 1),
        fecha_ingreso=date(2026, 1, 1),
    )


def _perfil(registro: Registro, *, hc: int, tarifa_clp: int) -> tuple[Perfil, TarifaPerfil]:
    perfil = Perfil(registro_id=registro.id, hc=hc, fecha_ingreso=date(2026, 1, 1))
    tarifa = TarifaPerfil(
        perfil_id=perfil.id,
        tarifa_hora_centavos=tarifa_clp * 100,
        vigente_desde=date(2026, 1, 1),
    )
    return perfil, tarifa


def _escenario(confiabilidad_vigencia: VigenciaEstadoCalculo | None = None):
    demanda = _registro(codigo="OPD-0001", probabilidad_bp=10_000)
    continuidad = _registro(
        codigo="OPD-0002",
        tipo=Tipo.CONTINUIDAD,
        estado=Estado.EN_CURSO,
        probabilidad_bp=10_000,
        confiabilidad_bp=10_000,
    )
    perfil, tarifa = _perfil(demanda, hc=3, tarifa_clp=2_600)
    contrato = Contrato(
        registro_id=continuidad.id,
        codigo_contrato="CTR-0001",
        fecha_inicio=date(2026, 1, 1),
        fecha_fin=date(2026, 12, 31),
        monto_mensual_clp=45_000_000,
        hc_comprometido=10,
    )
    return (
        CalcularProyeccion(
            registros=FakeRepositorioRegistros([demanda, continuidad]),
            perfiles=FakeRepositorioPerfiles([perfil], [tarifa]),
            contratos=FakeRepositorioContratos([contrato]),
            parametros=FakeRepositorioParametros(
                [
                    Parametro(
                        clave="horas_mensuales",
                        valor=180,
                        tipo=TipoParametro.ENTERO,
                        vigente_desde=date(2026, 1, 1),
                    )
                ]
            ),
            vigencias=FakeRepositorioVigencias(
                [confiabilidad_vigencia] if confiabilidad_vigencia else []
            ),
            reloj=RelojFijo(),
        ),
        demanda,
        continuidad,
        perfil,
        tarifa,
    )


def test_serie_de_12_meses_cumple_forecast_y_suma_totales() -> None:
    caso, demanda, continuidad, _, _ = _escenario()

    resultado = caso.ejecutar(Period(2026, 1), meses=12)

    assert len(resultado.meses) == 12
    assert len(resultado.detalles) == 24
    for fila in resultado.meses:
        assert fila.forecast_clp == fila.backlog_clp + fila.mab_clp
        assert fila.backlog_clp == 45_000_000
        assert fila.mab_clp == 1_263_600
    assert resultado.totales.forecast_clp == sum(fila.forecast_clp for fila in resultado.meses)
    assert resultado.totales.backlog_clp == 45_000_000 * 12
    assert resultado.detalles_de(demanda.id)[0].base_clp == 1_404_000
    assert resultado.detalles_de(continuidad.id)[0].mab_clp == 0


def test_vistas_de_3_6_y_12_meses() -> None:
    caso, _, _, _, _ = _escenario()
    for cantidad in (3, 6, 12):
        resultado = caso.ejecutar("2026-01", meses=cantidad)
        assert len(resultado.meses) == cantidad


def test_ac17_horas_con_vigencia_solo_desde_el_mes_efectivo() -> None:
    caso, demanda, _, _, _ = _escenario()
    caso.parametros = FakeRepositorioParametros(
        [
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
    )
    resultado = caso.calcular_registro(demanda.id, Period(2026, 1), meses=6)
    por_mes = {str(detalle.mes): detalle for detalle in resultado.meses}

    assert por_mes["2026-01"].base_clp == 1_404_000
    assert por_mes["2026-03"].base_clp == 1_404_000
    assert por_mes["2026-04"].base_clp == 1_248_000
    assert por_mes["2026-04"].mab_clp == 1_123_200
    assert por_mes["2026-03"].mab_clp == 1_263_600


def test_confiabilidad_con_vigencia_no_reescribe_meses_anteriores() -> None:
    vigencia = VigenciaEstadoCalculo(
        campo=CampoVigencia.CONFIABILIDAD,
        valor_bp=8_000,
        vigente_desde=date(2026, 3, 1),
        motivo="Ajuste de confiabilidad",
    )
    caso, demanda, _, _, _ = _escenario()
    vigencia.registro_id = demanda.id
    caso.vigencias = FakeRepositorioVigencias([vigencia])

    resultado = caso.calcular_registro(demanda.id, Period(2026, 1), meses=4)
    por_mes = {str(detalle.mes): detalle for detalle in resultado.meses}

    assert por_mes["2026-02"].confiabilidad_bp == 9_000
    assert por_mes["2026-02"].mab_clp == 1_263_600
    assert por_mes["2026-03"].confiabilidad_bp == 8_000
    assert por_mes["2026-03"].mab_clp == 1_123_200


def test_previsualizacion_no_persiste_ni_cambia_estados() -> None:
    caso, demanda, _, perfil, tarifa = _escenario()
    estado_original = demanda.estado
    borrador = EntradaCalculo(
        registro=demanda,
        perfiles=[perfil],
        tarifas={perfil.id: [tarifa]},
    )

    resultado = caso.previsualizar(borrador, Period(2026, 1), meses=3)

    assert len(resultado.meses) == 3
    assert caso.registros.guardados == []
    assert caso.perfiles.guardados == []
    assert demanda.estado is estado_original


def test_filtros_por_owner_y_sector() -> None:
    from uuid import uuid4

    caso, demanda, continuidad, _, _ = _escenario()
    owner = uuid4()
    sector = uuid4()
    demanda.owner_id = owner
    demanda.sector_id = sector

    solo_owner = caso.ejecutar(
        Period(2026, 1),
        meses=1,
        filtros=FiltrosProyeccion(owner_id=owner),
    )
    assert {detalle.registro_id for detalle in solo_owner.detalles} == {demanda.id}

    solo_sector = caso.ejecutar(
        Period(2026, 1),
        meses=1,
        filtros=FiltrosProyeccion(sector_id=sector),
    )
    assert {detalle.registro_id for detalle in solo_sector.detalles} == {demanda.id}

    detalle_continuidad = caso.calcular_registro(continuidad.id, Period(2026, 1), meses=1)
    assert detalle_continuidad.meses[0].backlog_clp == 45_000_000


def test_api_forecast_respeta_el_esquema_del_contrato() -> None:
    fastapi = pytest.importorskip("fastapi")
    from fastapi.testclient import TestClient

    from proyecta.interfaces.api.v1.forecast import obtener_calculo, router

    caso, _, _, _, _ = _escenario()
    app = fastapi.FastAPI()
    app.include_router(router, prefix="/api/v1")
    app.dependency_overrides[obtener_calculo] = lambda: caso

    cliente = TestClient(app)
    respuesta = cliente.get("/api/v1/forecast", params={"periodo": "2026-01", "meses": 3})

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["periodo"] == "2026-01"
    assert len(cuerpo["meses"]) == 3
    for mes in cuerpo["meses"]:
        assert set(mes) == {"mes", "backlog_contractual", "mab", "forecast", "hc"}
        assert mes["forecast"] == mes["backlog_contractual"] + mes["mab"]
