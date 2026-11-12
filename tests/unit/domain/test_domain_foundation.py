"""Fundación del dominio: enums, entidades, errores y semilla (T012–T017, T035).

Estas pruebas protegen los contratos que consumen Felipe, Matías y Leonardo:
rangos de entidades, catálogos de enums y datos sintéticos deterministas.
"""

from __future__ import annotations

from datetime import date

import pytest

from proyecta.application import ports
from proyecta.domain.entities import Contrato, Perfil, Registro, Usuario, utcnow
from proyecta.domain.enums import (
    PROBABILIDADES_VALIDAS_BP,
    PROBABILIDAD_SUGERIDA_POR_FLUJO_BP,
    Bucket,
    Estado,
    Flujo,
    MotivoCierre,
    Rol,
    Tipo,
    TipoParametro,
)
from proyecta.domain.errors import (
    ErrorAutorizacion,
    ErrorCalculo,
    ErrorConflicto,
    ErrorEstadoInvalido,
    ErrorHCNegativo,
    ErrorMotivoObligatorio,
    ErrorNoEncontrado,
    ErrorPermiso,
    ErrorRango,
    ErrorTransicionInvalida,
    ErrorValidacion,
    OperacionNoPermitida,
    PermisoDenegado,
)
from proyecta.seed.synthetic import generar_semilla


def test_orden_de_flujos_y_probabilidades_sugeridas() -> None:
    assert Flujo.PENDIENTE_RFP.orden == 1
    assert Flujo.PERFILES_SELECCIONADOS.orden == 6
    assert PROBABILIDAD_SUGERIDA_POR_FLUJO_BP[Flujo.PROPUESTA_ENTREGADA] == 5_000
    assert PROBABILIDAD_SUGERIDA_POR_FLUJO_BP[Flujo.PERFILES_SELECCIONADOS] == 10_000
    assert {500, 10_000} <= PROBABILIDADES_VALIDAS_BP


def test_bucket_y_motivos_que_prorratean() -> None:
    assert Bucket.MAB.value == "MAB"
    assert Bucket.BACKLOG_CONTRACTUAL.value == "BACKLOG_CONTRACTUAL"
    assert MotivoCierre.CANCELADA_CLIENTE.value == "CANCELADA_CLIENTE"


def test_entidades_validan_rangos_basicos() -> None:
    with pytest.raises(ErrorRango):
        Perfil(hc=0)
    with pytest.raises(ErrorRango):
        Perfil(hc=1, dedicacion_pct=0)
    with pytest.raises(ErrorRango):
        Perfil(hc=1, fecha_ingreso=date(2026, 2, 1), fecha_fin=date(2026, 1, 1))
    with pytest.raises(ErrorRango):
        Registro(probabilidad_bp=10_001)
    with pytest.raises(ErrorValidacion):
        Usuario(nombre="", email="x@example.test")
    assert Usuario(nombre="Ana", email="ANA@Example.TEST").email == "ana@example.test"


def test_contrato_indefinido_no_admite_fecha_fin() -> None:
    with pytest.raises(ErrorValidacion):
        Contrato(es_indefinido=True, fecha_fin=date(2026, 1, 1))
    with pytest.raises(ErrorValidacion):
        Contrato(es_indefinido=False, fecha_fin=None)
    contrato = Contrato(
        es_indefinido=True,
        fecha_inicio=date(2026, 1, 1),
        monto_mensual_clp=0,
        hc_comprometido=0,
    )
    assert contrato.fecha_fin is None


def test_errores_serializables_y_jerarquia() -> None:
    error = ErrorNoEncontrado(detalle={"registro_id": "abc"})
    assert error.status_sugerido == 404
    assert error.a_dict() == {
        "code": "NO_ENCONTRADO",
        "message": "Recurso no encontrado",
        "details": {"registro_id": "abc"},
    }
    assert issubclass(ErrorHCNegativo, ErrorCalculo)
    assert str(ErrorRango("RANGO_INVALIDO", "fuera")) == "RANGO_INVALIDO: fuera"


def test_contrato_de_error_usa_code_y_message_con_alias_en_espanol() -> None:
    error = ErrorValidacion("MOTIVO_OBLIGATORIO", "Falta el motivo")
    assert error.code == "MOTIVO_OBLIGATORIO"
    assert error.message == "Falta el motivo"
    assert error.codigo == error.code
    assert error.mensaje == error.message
    assert error.a_dict() == {"code": "MOTIVO_OBLIGATORIO", "message": "Falta el motivo"}

    # El nombre en español sigue funcionando para el código escrito antes de T028.
    error.codigo = "CAMPO_OBLIGATORIO"
    assert error.code == "CAMPO_OBLIGATORIO"


def test_errores_de_autorizacion_y_alias_de_compatibilidad() -> None:
    denegado = PermisoDenegado(accion="editar_registro")
    assert isinstance(denegado, ErrorAutorizacion)
    assert denegado.code == "PERMISO_DENEGADO"
    assert denegado.status_sugerido == 403
    assert denegado.accion == "editar_registro"
    assert denegado.a_dict()["details"] == {"accion": "editar_registro"}

    no_permitida = OperacionNoPermitida(accion="borrar_bitacora")
    assert no_permitida.code == "OPERACION_NO_PERMITIDA"
    assert no_permitida.status_sugerido == 405

    assert issubclass(ErrorPermiso, PermisoDenegado)
    assert ErrorPermiso().code == "PERMISO_DENEGADO"


def test_codigos_acordados_con_t028_y_sus_alias() -> None:
    assert ErrorConflicto().code == "CONFLICTO_VERSION"
    assert ErrorTransicionInvalida().code == "TRANSICION_INVALIDA"
    assert ErrorEstadoInvalido().code == "ESTADO_INVALIDO"
    assert issubclass(ErrorEstadoInvalido, ErrorTransicionInvalida)
    assert ErrorMotivoObligatorio().code == "MOTIVO_OBLIGATORIO"
    assert issubclass(ErrorMotivoObligatorio, ErrorValidacion)


def test_puertos_de_aplicacion_existen_y_son_protocolos() -> None:
    for nombre in (
        "Reloj",
        "RepositorioRegistros",
        "RepositorioPerfiles",
        "RepositorioContratos",
        "RepositorioParametros",
        "RepositorioVigencias",
        "RepositorioAuditoria",
        "RepositorioSugerencias",
        "ProveedorIA",
        "Exportador",
    ):
        assert hasattr(ports, nombre)


def test_semilla_es_determinista_y_sin_datos_reales() -> None:
    primera = generar_semilla(cantidad_registros=24, semilla=7)
    segunda = generar_semilla(cantidad_registros=24, semilla=7)

    assert [r.codigo for r in primera.registros] == [r.codigo for r in segunda.registros]
    assert [r.id for r in primera.registros] == [r.id for r in segunda.registros]
    assert len(primera.registros) == 24
    assert len(list(primera.entradas())) == 24

    clientes = [c.etiqueta for c in primera.catalogos if c.tipo.value == "CLIENTE"]
    assert clientes and all(nombre.startswith("Cliente Sintético") for nombre in clientes)
    assert all(usuario.email.endswith("@example.test") for usuario in primera.usuarios)
    assert all(
        "NTT" not in (registro.servicio_proyecto or "") for registro in primera.registros
    )

    adjudicados = [
        registro
        for registro in primera.registros
        if registro.estado in (Estado.ADJUDICADA, Estado.EN_CURSO)
    ]
    ids_con_perfil = {perfil.registro_id for perfil in primera.perfiles}
    assert all(registro.id in ids_con_perfil for registro in adjudicados)


def test_semilla_tipos_y_parametros_base() -> None:
    datos = generar_semilla(cantidad_registros=12, semilla=11)
    horas = [p for p in datos.parametros if p.clave == "horas_mensuales"][0]
    assert horas.tipo is TipoParametro.ENTERO
    assert horas.valor == 180
    contratos = {contrato.registro_id: contrato for contrato in datos.contratos}
    for registro in datos.registros:
        if registro.tipo is Tipo.CONTINUIDAD:
            assert registro.id in contratos
            assert registro.flujo is Flujo.PERFILES_SELECCIONADOS
            assert registro.probabilidad_bp == 10_000
        else:
            assert registro.id not in contratos
    lideres = [u for u in datos.usuarios if u.rol is Rol.LIDER]
    assert lideres
    assert all(registro.owner_id in {u.id for u in lideres} for registro in datos.registros)
    assert utcnow().tzinfo is not None
