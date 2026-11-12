"""Integración de sugerencias IA y simulación (T142, T148, US10).

Verifica las garantías del principio VIII: cita obligatoria, aprobación humana,
auditoría con origen IA, funcionamiento sin IA y simulación aislada sin escritura.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import uuid4

import pytest

from proyecta.application.ports import ContextoSugerencia, PropuestaIA
from proyecta.application.use_cases.ia import (
    AceptarSugerencia,
    DescartarSugerencia,
    GenerarSugerencias,
)
from proyecta.application.use_cases.simulacion import EscenarioSimulacion, SimularEscenario
from proyecta.domain.entities import (
    Bitacora,
    Parametro,
    Perfil,
    Registro,
    TarifaPerfil,
)
from proyecta.domain.enums import (
    Estado,
    EstadoSugerencia,
    EtiquetaIA,
    Flujo,
    Origen,
    Tipo,
    TipoParametro,
)
from proyecta.domain.errors import ErrorIA, ErrorValidacion
from proyecta.domain.value_objects import Period
from proyecta.infrastructure.ai.vertex import (
    ConfiguracionVertex,
    ProveedorVertexIA,
    construir_prompt,
    sanitizar_contexto,
)
from _fakes import (
    FakeRepositorioAuditoria,
    FakeRepositorioBitacora,
    FakeRepositorioContratos,
    FakeRepositorioParametros,
    FakeRepositorioPerfiles,
    FakeRepositorioRegistros,
    FakeRepositorioSugerencias,
    FakeRepositorioVigencias,
    RelojFijo,
)


def _escenario():
    registro = Registro(
        codigo="OPD-0100",
        tipo=Tipo.DEMANDA,
        estado=Estado.EN_CURSO,
        flujo=Flujo.PERFILES_SELECCIONADOS,
        probabilidad_bp=9_000,
        confiabilidad_bp=9_000,
        fecha_creacion=date(2025, 12, 1),
        fecha_ingreso=date(2026, 1, 1),
    )
    perfil = Perfil(registro_id=registro.id, hc=3, fecha_ingreso=date(2026, 1, 1))
    tarifa = TarifaPerfil(
        perfil_id=perfil.id,
        tarifa_hora_centavos=260_000,
        vigente_desde=date(2026, 1, 1),
    )
    bitacora = Bitacora(
        registro_id=registro.id,
        contenido="El cliente canceló el servicio por reestructuración interna.",
    )
    return registro, perfil, tarifa, bitacora


def test_sugerencia_cita_la_bitacora_y_queda_pendiente() -> None:
    registro, _, _, entrada = _escenario()
    sugerencias = FakeRepositorioSugerencias()
    generador = GenerarSugerencias(
        registros=FakeRepositorioRegistros([registro]),
        bitacora=FakeRepositorioBitacora([entrada]),
        sugerencias=sugerencias,
        reloj=RelojFijo(),
    )

    creadas = generador.ejecutar(registro.id)

    assert len(creadas) == 1
    sugerencia = creadas[0]
    assert sugerencia.campo == "estado"
    assert sugerencia.valor_sugerido == Estado.CANCELADA.value
    assert sugerencia.cita_bitacora_id == entrada.id
    assert sugerencia.estado is EstadoSugerencia.PENDIENTE
    assert sugerencia.etiqueta is EtiquetaIA.ESTIMACION
    assert sugerencias.guardadas == [sugerencia]


def test_aceptar_sugerencia_audita_con_origen_ia_sin_escribir_el_registro() -> None:
    registro, _, _, entrada = _escenario()
    sugerencias = FakeRepositorioSugerencias()
    auditoria = FakeRepositorioAuditoria()
    generador = GenerarSugerencias(
        registros=FakeRepositorioRegistros([registro]),
        bitacora=FakeRepositorioBitacora([entrada]),
        sugerencias=sugerencias,
        reloj=RelojFijo(),
    )
    sugerencia = generador.ejecutar(registro.id)[0]
    revisor = registro.owner_id or registro.id

    aceptada = AceptarSugerencia(
        sugerencias=sugerencias, auditoria=auditoria, reloj=RelojFijo()
    ).ejecutar(sugerencia.id, revisor)

    assert aceptada.estado is EstadoSugerencia.ACEPTADA
    assert aceptada.revisor_id == revisor
    assert len(auditoria.eventos) == 1
    evento = auditoria.eventos[0]
    assert evento.origen is Origen.IA
    assert evento.campo == "estado"
    assert evento.valor_nuevo == Estado.CANCELADA.value
    assert evento.usuario_id == revisor
    assert registro.estado is Estado.EN_CURSO  # la IA no escribió sola


def test_descartar_sugerencia_no_genera_auditoria() -> None:
    registro, _, _, entrada = _escenario()
    sugerencias = FakeRepositorioSugerencias()
    auditoria = FakeRepositorioAuditoria()
    generador = GenerarSugerencias(
        registros=FakeRepositorioRegistros([registro]),
        bitacora=FakeRepositorioBitacora([entrada]),
        sugerencias=sugerencias,
        reloj=RelojFijo(),
    )
    sugerencia = generador.ejecutar(registro.id)[0]

    descartada = DescartarSugerencia(sugerencias=sugerencias, reloj=RelojFijo()).ejecutar(
        sugerencia.id, registro.id
    )

    assert descartada.estado is EstadoSugerencia.DESCARTADA
    assert auditoria.eventos == []


def test_sin_bitacora_no_hay_sugerencias() -> None:
    registro, _, _, _ = _escenario()
    generador = GenerarSugerencias(
        registros=FakeRepositorioRegistros([registro]),
        bitacora=FakeRepositorioBitacora([]),
        sugerencias=FakeRepositorioSugerencias(),
        reloj=RelojFijo(),
    )
    assert generador.ejecutar(registro.id) == []


class ProveedorSinCita:
    def disponible(self) -> bool:
        return True

    def sugerir(self, contexto: ContextoSugerencia) -> PropuestaIA:
        return PropuestaIA(campo="estado", valor_sugerido="CANCELADA", justificacion="x")


def test_propuesta_sin_cita_es_rechazada() -> None:
    registro, _, _, entrada = _escenario()
    generador = GenerarSugerencias(
        registros=FakeRepositorioRegistros([registro]),
        bitacora=FakeRepositorioBitacora([entrada]),
        sugerencias=FakeRepositorioSugerencias(),
        proveedor=ProveedorSinCita(),
        reloj=RelojFijo(),
    )
    with pytest.raises(ErrorIA):
        generador.ejecutar(registro.id)


def test_sin_ia_disponible_el_mvp_sigue_operando() -> None:
    proveedor = ProveedorVertexIA(ConfiguracionVertex(habilitado=False))
    assert proveedor.disponible() is False
    assert proveedor.sugerir(ContextoSugerencia(
        registro_id=uuid4(),
        codigo="OPD-0001",
        estado="PENDIENTE",
        flujo="PENDIENTE_RFP",
        tipo="OPORTUNIDAD",
    )) is None

    registro, _, _, entrada = _escenario()
    generador = GenerarSugerencias(
        registros=FakeRepositorioRegistros([registro]),
        bitacora=FakeRepositorioBitacora([entrada]),
        sugerencias=FakeRepositorioSugerencias(),
        proveedor=proveedor,
        reloj=RelojFijo(),
    )
    assert len(generador.ejecutar(registro.id)) == 1


def test_el_contexto_de_ia_no_envia_datos_de_cliente_ni_tarifas() -> None:
    contexto = ContextoSugerencia(
        registro_id=uuid4(),
        codigo="OPD-0001",
        estado="PENDIENTE",
        flujo="PROPUESTA_ENTREGADA",
        tipo="OPORTUNIDAD",
        campos={
            "cliente": "Banco Real",
            "tarifa_hora_centavos": 260_000,
            "monto_mensual_clp": 45_000_000,
            "estado": "PENDIENTE",
            "probabilidad_bp": 5_000,
        },
        evidencias=(),
    )
    sanitizado = sanitizar_contexto(contexto)
    prompt = construir_prompt(contexto)

    assert "cliente" not in sanitizado.campos
    assert "tarifa_hora_centavos" not in sanitizado.campos
    assert "Banco Real" not in prompt
    assert "260000" not in prompt
    assert "45000000" not in prompt


def _simulador():
    registro = Registro(
        codigo="OPD-0200",
        tipo=Tipo.DEMANDA,
        estado=Estado.ADJUDICADA,
        flujo=Flujo.PROPUESTA_ENTREGADA,
        probabilidad_bp=9_000,
        confiabilidad_bp=9_000,
        fecha_creacion=date(2025, 12, 1),
        fecha_ingreso=date(2026, 1, 1),
    )
    perfil = Perfil(registro_id=registro.id, hc=3, fecha_ingreso=date(2026, 1, 1))
    tarifa = TarifaPerfil(
        perfil_id=perfil.id,
        tarifa_hora_centavos=260_000,
        vigente_desde=date(2026, 1, 1),
    )
    registros = FakeRepositorioRegistros([registro])
    perfiles = FakeRepositorioPerfiles([perfil], [tarifa])
    simulador = SimularEscenario(
        registros=registros,
        perfiles=perfiles,
        contratos=FakeRepositorioContratos([]),
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
        vigencias=FakeRepositorioVigencias([]),
        reloj=RelojFijo(),
    )
    return simulador, registros, perfiles, registro


def test_simulacion_es_aislada_etiquetada_y_no_escribe() -> None:
    simulador, registros, perfiles, registro = _simulador()

    resultado = simulador.ejecutar(
        EscenarioSimulacion(periodo=Period(2026, 1), meses=3, probabilidad=Decimal("0.5"))
    )

    assert resultado.simulado is True
    assert resultado.etiqueta == "simulado"
    assert resultado.a_dict()["simulado"] is True
    assert resultado.meses[0].mab_clp == 631_800
    assert registros.guardados == []
    assert perfiles.guardados == []
    assert registro.probabilidad_bp == 9_000
    assert registro.estado is Estado.ADJUDICADA


def test_simulacion_no_permite_cambiar_estados_ni_fechas() -> None:
    _, _, _, registro = _simulador()
    with pytest.raises(ErrorValidacion):
        EscenarioSimulacion(
            periodo=Period(2026, 1),
            cambios={registro.id: {"estado": Estado.CANCELADA.value}},
        )
