"""Integración de la carga sintética sintética (T150, T155, T156).

Cubre el escenario AC-14: cuatro registros, inconsistencias por fila,
recálculo a 180 h, idempotencia y ausencia de datos reales.
"""

from __future__ import annotations

import re
from dataclasses import replace
from datetime import date
from types import SimpleNamespace
from typing import Any, Sequence
from uuid import UUID

from proyecta.application.use_cases.calculo import CalcularProyeccion
from proyecta.application.use_cases.carga import (
    ESTADO_TIPO_INCOHERENTE,
    FECHA_FUTURA,
    FLUJO_TIPO_INCOHERENTE,
    PROBABILIDAD_FUERA_CATALOGO,
    REGISTRO_CERRADO_CON_HC,
    CargarEstructura,
    ResultadoCarga,
)
from proyecta.domain.entities import (
    AjusteHC,
    Contrato,
    Parametro,
    Perfil,
    Registro,
    TarifaPerfil,
    VigenciaEstadoCalculo,
)
from proyecta.domain.enums import Flujo, TipoCatalogo, TipoParametro
from proyecta.domain.errors import ErrorValidacion
from proyecta.domain.value_objects import Period
from proyecta.seed.fixtures import (
    FECHA_FUTURA as FIXTURE_FECHA_FUTURA,
    FixtureCarga,
    cargar_fixture,
    serializar_fixture,
)
from _fakes import (
    FakeRepositorioContratos,
    FakeRepositorioParametros,
    FakeRepositorioPerfiles,
    FakeRepositorioRegistros,
    FakeRepositorioVigencias,
    RelojFijo,
)


class AlmacenEnMemoria:
    """Implementación de ``AlmacenCarga`` sobre los dobles de prueba."""

    def __init__(self, fallar_en: set[str] | None = None) -> None:
        self.registros = FakeRepositorioRegistros()
        self.perfiles = FakeRepositorioPerfiles()
        self.contratos = FakeRepositorioContratos()
        self.vigencias = FakeRepositorioVigencias()
        self.fallar_en = fallar_en or set()

    def buscar_por_codigo(self, codigo: str) -> Registro | None:
        encontrados = self.registros.listar(codigos=[codigo])
        return encontrados[0] if encontrados else None

    def guardar_registro(self, registro: Registro) -> None:
        if registro.codigo in self.fallar_en:
            raise ErrorValidacion("VALIDACION", "La fila no se pudo normalizar")
        self.registros.guardar(registro)

    def guardar_perfil(self, perfil: Perfil) -> None:
        self.perfiles.guardar(perfil)

    def guardar_tarifa(self, tarifa: TarifaPerfil) -> None:
        self.perfiles.guardar_tarifa(tarifa)

    def guardar_contrato(self, contrato: Contrato) -> None:
        self.contratos.guardar(contrato)

    def guardar_ajuste(self, ajuste: AjusteHC) -> None:
        self.perfiles.guardar_ajuste(ajuste)

    def guardar_vigencia(self, vigencia: VigenciaEstadoCalculo) -> None:
        self.vigencias.guardar(vigencia)


def _cargar(fixture: FixtureCarga) -> tuple[AlmacenEnMemoria, ResultadoCarga]:
    almacen = AlmacenEnMemoria()
    resultado = CargarEstructura(almacen).ejecutar(
        fixture.datos, periodo=fixture.periodo
    )
    return almacen, resultado


def _origen(
    registros: Sequence[Registro],
    fixture: FixtureCarga,
    *,
    incluir: UUID | None = None,
) -> Any:
    perfiles = [
        perfil
        for perfil in fixture.datos.perfiles
        if incluir is None or perfil.registro_id == incluir
    ]
    ids = {perfil.id for perfil in perfiles}
    return SimpleNamespace(
        registros=list(registros),
        perfiles=perfiles,
        tarifas=[t for t in fixture.datos.tarifas if t.perfil_id in ids],
        contratos=[],
        ajustes=[],
        vigencias=[],
    )


# --- T150: integración del fixture ------------------------------------------


def test_fixture_crea_cuatro_registros_y_reporta_una_inconsistencia_por_fila() -> None:
    fixture = cargar_fixture()
    almacen, resultado = _cargar(fixture)

    assert resultado.creados == 4
    assert resultado.actualizados == 0
    assert resultado.horas_mensuales == 180
    assert len(almacen.registros.listar()) == 4

    esperadas = {inconsistencia.codigo for inconsistencia in fixture.inconsistencias_esperadas}
    assert set(resultado.codigos) == esperadas
    assert len(resultado.inconsistencias) == 4

    por_fila = {inconsistencia.fila: inconsistencia.codigo for inconsistencia in resultado.inconsistencias}
    assert por_fila == {
        1: REGISTRO_CERRADO_CON_HC,
        2: PROBABILIDAD_FUERA_CATALOGO,
        3: FECHA_FUTURA,
        4: ESTADO_TIPO_INCOHERENTE,
    }
    assert FIXTURE_FECHA_FUTURA == FECHA_FUTURA


def test_fixture_recalcula_con_180_horas() -> None:
    fixture = cargar_fixture()
    almacen, _ = _cargar(fixture)

    parametros = FakeRepositorioParametros(
        [
            Parametro(
                clave="horas_mensuales",
                valor=180,
                tipo=TipoParametro.ENTERO,
                vigente_desde=date(2026, 1, 1),
            )
        ]
    )
    calculo = CalcularProyeccion(
        registros=almacen.registros,
        perfiles=almacen.perfiles,
        contratos=almacen.contratos,
        parametros=parametros,
        vigencias=almacen.vigencias,
        reloj=RelojFijo(),
    )
    demanda = next(
        registro for registro in almacen.registros.listar() if registro.codigo == "OPD-9002"
    )
    resultado = calculo.calcular_registro(demanda.id, Period(2026, 1), meses=3)

    assert resultado.meses
    assert any(detalle.hc > 0 for detalle in resultado.meses)
    assert resultado.total_forecast() > 0


# --- T155: idempotencia y ausencia de datos reales --------------------------


def test_la_carga_es_idempotente_por_codigo() -> None:
    fixture = cargar_fixture()
    almacen, primera = _cargar(fixture)
    segunda = CargarEstructura(almacen).ejecutar(
        fixture.datos, periodo=fixture.periodo
    )

    assert primera.creados == 4
    assert segunda.creados == 0
    assert segunda.actualizados == 4
    assert len(almacen.registros.listar()) == 4
    assert len(almacen.registros.guardados) == 4


def test_el_fixture_no_contiene_datos_reales() -> None:
    fixture = cargar_fixture()

    for usuario in fixture.datos.usuarios:
        assert usuario.email.endswith("@example.test")

    for registro in fixture.datos.registros:
        assert re.fullmatch(r"OPD-\d{4}", registro.codigo)

    clientes = [
        catalogo
        for catalogo in fixture.datos.catalogos
        if catalogo.tipo is TipoCatalogo.CLIENTE
    ]
    assert clientes
    assert all(cliente.etiqueta.startswith("Cliente Sintético") for cliente in clientes)


def test_serializar_fixture_expone_las_inconsistencias_esperadas() -> None:
    fixture = cargar_fixture()
    cuerpo = serializar_fixture(fixture)

    assert cuerpo["fixture"] == "four-records"
    assert cuerpo["periodo"] == "2026-01"
    assert cuerpo["horas_mensuales"] == 180
    assert len(cuerpo["registros"]) == 4
    assert len(cuerpo["inconsistencias_esperadas"]) == 4


# --- Errores por fila -------------------------------------------------------


def test_un_flujo_incoherente_se_reporta_sin_abortar() -> None:
    fixture = cargar_fixture()
    registro = replace(
        fixture.datos.registros[3], flujo=Flujo.PERFILES_SELECCIONADOS
    )
    almacen = AlmacenEnMemoria()
    resultado = CargarEstructura(almacen).ejecutar(
        _origen([registro], fixture, incluir=registro.id), periodo=fixture.periodo
    )

    assert resultado.creados == 1
    assert FLUJO_TIPO_INCOHERENTE in resultado.codigos


def test_una_fila_rechazada_no_detiene_las_demas() -> None:
    fixture = cargar_fixture()
    almacen = AlmacenEnMemoria(fallar_en={"OPD-9003"})
    resultado = CargarEstructura(almacen).ejecutar(
        fixture.datos, periodo=fixture.periodo
    )

    assert resultado.creados == 3
    assert "VALIDACION" in resultado.codigos
    assert almacen.buscar_por_codigo("OPD-9003") is None
    assert almacen.buscar_por_codigo("OPD-9004") is not None
