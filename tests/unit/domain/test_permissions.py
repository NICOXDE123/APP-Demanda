"""Pruebas de T028: matriz de permisos de spec.md (FR-061 a FR-067, AC-09, AC-10)."""

import pytest

from proyecta.domain.enums import Rol
from proyecta.domain.errors import (
    ErrorAutorizacion,
    ErrorDominio,
    OperacionNoPermitida,
    PermisoDenegado,
)
from proyecta.domain.permissions import (
    Accion,
    Actor,
    Alcance,
    acciones_permitidas,
    alcance,
    autorizado,
    evaluar,
    exigir,
    puede_cambiar_rol,
    puede_desactivar_usuario,
)

LIDER = Actor("u-lider-1", "LIDER")
OTRO_LIDER = Actor("u-lider-2", "LIDER")
OPERACIONES = Actor("u-ops-1", "OPERACIONES")
EJECUTIVO = Actor("u-exec-1", "EJECUTIVO")


# --- Líder: solo propios (AC-10) ---------------------------------------------
def test_lider_edita_su_registro():
    assert autorizado(LIDER, Accion.EDITAR_REGISTRO, owner_id="u-lider-1")


def test_lider_no_edita_registro_de_otro_lider():  # AC-10
    d = evaluar(LIDER, Accion.EDITAR_REGISTRO, owner_id="u-lider-2")
    assert not d.permitido and "otro líder" in d.motivo


def test_propiedad_no_informada_se_niega():
    assert not autorizado(LIDER, Accion.EDITAR_REGISTRO)


@pytest.mark.parametrize(
    "accion",
    [Accion.ESCRIBIR_BITACORA, Accion.CAMBIAR_TIPO_FLUJO, Accion.MANTENER_CONTRATO],
)
def test_lider_solo_propios_en_acciones_de_propiedad(accion):
    assert autorizado(LIDER, accion, owner_id="u-lider-1")
    assert not autorizado(OTRO_LIDER, accion, owner_id="u-lider-1")


@pytest.mark.parametrize(
    "accion",
    [
        Accion.AJUSTAR_CONFIABILIDAD,
        Accion.AJUSTAR_HC,
        Accion.MANTENER_PARAMETROS,
        Accion.MANTENER_USUARIOS,
        Accion.MANTENER_METAS,
        Accion.CERRAR_PERIODO,
        Accion.REABRIR_REGISTRO,
        Accion.CREAR_CONTINUIDAD,
    ],
)
def test_lider_no_ejecuta_acciones_de_operaciones(accion):
    assert not autorizado(LIDER, accion, owner_id="u-lider-1")
    assert autorizado(OPERACIONES, accion)


def test_lider_crea_registro_y_ve_alcance_propio():
    assert autorizado(LIDER, Accion.CREAR_REGISTRO)
    for a in (Accion.VER_DASHBOARD, Accion.EXPORTAR, Accion.CONSULTAR_AUDITORIA):
        assert alcance(LIDER, a) is Alcance.PROPIOS


# --- Operaciones: todos -------------------------------------------------------
def test_operaciones_edita_cualquier_registro():
    assert autorizado(OPERACIONES, Accion.EDITAR_REGISTRO, owner_id="u-lider-1")
    assert autorizado(OPERACIONES, Accion.ESCRIBIR_BITACORA, owner_id="u-lider-2")


def test_operaciones_cierra_periodo_y_mantiene_metas():
    assert autorizado(OPERACIONES, Accion.CERRAR_PERIODO)
    assert autorizado(OPERACIONES, Accion.MANTENER_METAS)


# --- Ejecutivo: solo lectura --------------------------------------------------
@pytest.mark.parametrize(
    "accion",
    [
        Accion.CREAR_REGISTRO,
        Accion.EDITAR_REGISTRO,
        Accion.ESCRIBIR_BITACORA,
        Accion.CAMBIAR_TIPO_FLUJO,
        Accion.AJUSTAR_CONFIABILIDAD,
        Accion.AJUSTAR_HC,
        Accion.MANTENER_PARAMETROS,
        Accion.MANTENER_USUARIOS,
        Accion.MANTENER_METAS,
        Accion.MANTENER_CONTRATO,
        Accion.CERRAR_PERIODO,
        Accion.REABRIR_REGISTRO,
    ],
)
def test_ejecutivo_no_escribe(accion):
    assert not autorizado(EJECUTIVO, accion, owner_id="u-lider-1")


@pytest.mark.parametrize(
    "accion",
    [
        Accion.VER_REGISTRO,
        Accion.VER_DASHBOARD,
        Accion.EXPORTAR,
        Accion.CONSULTAR_AUDITORIA,
        Accion.VER_CONTRATO,
        Accion.VER_METAS,
        Accion.VER_CORTES,
    ],
)
def test_ejecutivo_lee_todo(accion):
    assert alcance(EJECUTIVO, accion) is Alcance.TODOS
    assert autorizado(EJECUTIVO, accion)


# --- Inmutabilidad y no borrado (AC-09, FR-055) -------------------------------
@pytest.mark.parametrize(
    "accion",
    [
        Accion.EDITAR_BITACORA,
        Accion.BORRAR_BITACORA,
        Accion.EDITAR_AUDITORIA,
        Accion.BORRAR_AUDITORIA,
        Accion.ELIMINAR_REGISTRO,
    ],
)
@pytest.mark.parametrize("actor", [LIDER, OPERACIONES, EJECUTIVO])
def test_nadie_edita_borra_auditoria_bitacora_ni_registros(actor, accion):
    assert not autorizado(actor, accion, owner_id=actor.usuario_id)
    with pytest.raises(OperacionNoPermitida) as exc:  # HTTP 405
        exigir(actor, accion, owner_id=actor.usuario_id)
    assert exc.value.code == "OPERACION_NO_PERMITIDA"
    assert not isinstance(exc.value, PermisoDenegado)
    assert isinstance(exc.value, ErrorAutorizacion) and exc.value.message
    assert exc.value.status_sugerido == 405


def test_rechazo_por_rol_o_propiedad_es_403():
    with pytest.raises(PermisoDenegado) as exc:
        exigir(LIDER, Accion.EDITAR_REGISTRO, owner_id="u-lider-2")
    assert exc.value.code == "PERMISO_DENEGADO"
    assert exc.value.status_sugerido == 403
    assert isinstance(exc.value, ErrorDominio)
    assert exc.value.accion == Accion.EDITAR_REGISTRO.value
    assert "otro líder" in exc.value.message
    with pytest.raises(PermisoDenegado):
        exigir(EJECUTIVO, Accion.CREAR_REGISTRO)


# --- Denegación por defecto ---------------------------------------------------
def test_actor_inactivo_se_niega():
    inactivo = Actor("u-ops-9", "OPERACIONES", activo=False)
    assert not autorizado(inactivo, Accion.VER_DASHBOARD)
    assert acciones_permitidas(inactivo) == frozenset()


def test_rol_desconocido_se_niega():
    assert not autorizado(Actor("x", "SPONSOR"), Accion.VER_DASHBOARD)


def test_acepta_enum_con_value():
    class Rol:
        value = "OPERACIONES"

    assert autorizado(Actor("u", Rol()), Accion.CERRAR_PERIODO)


def test_exigir_permitido_no_lanza():
    exigir(OPERACIONES, Accion.CERRAR_PERIODO)


def test_toda_accion_tiene_fila_en_la_matriz():
    for accion in Accion:
        for actor in (LIDER, OPERACIONES, EJECUTIVO):
            assert isinstance(alcance(actor, accion), Alcance)


def test_acciones_permitidas_para_ui():
    assert Accion.EDITAR_REGISTRO not in acciones_permitidas(EJECUTIVO)
    assert Accion.MANTENER_METAS in acciones_permitidas(OPERACIONES)
    assert Accion.MANTENER_METAS not in acciones_permitidas(LIDER)


# --- Usuarios y roles (FR-064, FR-065) ----------------------------------------
def test_lider_no_cambia_su_rol_ni_el_de_otro():
    assert not puede_cambiar_rol(LIDER, "u-lider-1")
    assert not puede_cambiar_rol(LIDER, "u-lider-2")
    assert puede_cambiar_rol(OPERACIONES, "u-lider-1")


def test_no_se_desactiva_al_ultimo_operaciones():
    d = puede_desactivar_usuario(OPERACIONES, "OPERACIONES", True, operaciones_activos=1)
    assert not d.permitido and "último" in d.motivo
    assert puede_desactivar_usuario(OPERACIONES, "OPERACIONES", True, operaciones_activos=2)
    assert puede_desactivar_usuario(OPERACIONES, "LIDER", True, operaciones_activos=1)


def test_lider_no_desactiva_usuarios():
    assert not puede_desactivar_usuario(LIDER, "LIDER", True, operaciones_activos=3)


# --- Integración con los enums reales de Fundación (T012) -----------------------
def test_acepta_enum_rol_real():
    for rol, esperado in ((Rol.LIDER, False), (Rol.OPERACIONES, True), (Rol.EJECUTIVO, False)):
        assert autorizado(Actor("u", rol), Accion.CERRAR_PERIODO) is esperado


def test_propiedad_compara_uuid_con_texto():
    from uuid import uuid4

    uid = uuid4()
    assert autorizado(Actor(uid, Rol.LIDER), Accion.EDITAR_REGISTRO, owner_id=uid)
    assert autorizado(Actor(str(uid), Rol.LIDER), Accion.EDITAR_REGISTRO, owner_id=uid)
    assert not autorizado(Actor(uid, Rol.LIDER), Accion.EDITAR_REGISTRO, owner_id=uuid4())


def test_codigo_y_mensaje_siguen_el_contrato_del_openapi():
    with pytest.raises(PermisoDenegado) as exc:
        exigir(EJECUTIVO, Accion.CREAR_REGISTRO)
    cuerpo = exc.value.a_dict()
    assert cuerpo["code"] == "PERMISO_DENEGADO"
    assert cuerpo["message"]
    assert cuerpo["details"] == {"accion": "CREAR_REGISTRO"}
