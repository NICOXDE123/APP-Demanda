"""Transiciones de estado y flujo (US2; data-model.md «State Machine»)."""

from datetime import date

import pytest

from proyecta.domain import states
from proyecta.domain.entities import Registro
from proyecta.domain.enums import Estado, Flujo, MotivoCierre, Rol, Tipo
from proyecta.domain.errors import ErrorTransicionInvalida

HOY = date(2026, 11, 12)


def oportunidad(**cambios) -> Registro:
    return Registro(codigo="OPD-0001", probabilidad_bp=5_000, **cambios)


def test_adjudicar_cambia_tipo_y_fija_probabilidad_en_100():
    r = oportunidad()
    cambios = states.transicionar(r, Estado.ADJUDICADA, rol=Rol.LIDER, motivo="Ganada", fecha=HOY, perfiles_con_ingreso=1)
    assert (r.estado, r.tipo, r.probabilidad_bp, r.fecha_adjudicacion) == (Estado.ADJUDICADA, Tipo.DEMANDA, 10_000, HOY)
    assert r.flujo is Flujo.PROPUESTA_ENTREGADA
    assert ("probabilidad_bp", 5_000, 10_000) in cambios


def test_pendiente_no_salta_a_en_curso_y_no_modifica_nada():
    r = oportunidad()
    with pytest.raises(ErrorTransicionInvalida, match="adjudicarse"):
        states.transicionar(r, Estado.EN_CURSO, rol=Rol.LIDER, motivo="x", fecha=HOY, perfiles_con_ingreso=1)
    assert r.estado is Estado.PENDIENTE


@pytest.mark.parametrize("destino", [Estado.ADJUDICADA])
def test_adjudicar_sin_perfil_se_bloquea(destino):
    with pytest.raises(ErrorTransicionInvalida, match="al menos un perfil"):
        states.transicionar(oportunidad(), destino, rol=Rol.LIDER, motivo="x", fecha=HOY, perfiles_con_ingreso=0)


def test_toda_transicion_exige_motivo():
    with pytest.raises(ErrorTransicionInvalida, match="motivo"):
        states.transicionar(oportunidad(), Estado.STANDBY, rol=Rol.LIDER, motivo="  ", fecha=HOY, perfiles_con_ingreso=0)


def test_standby_guarda_estado_previo_y_la_reactivacion_lo_restaura():
    r = Registro(codigo="OPD-0002", tipo=Tipo.DEMANDA, estado=Estado.ADJUDICADA)
    states.transicionar(r, Estado.STANDBY, rol=Rol.LIDER, motivo="Pausa", fecha=HOY, perfiles_con_ingreso=1)
    assert (r.estado, r.estado_previo) == (Estado.STANDBY, Estado.ADJUDICADA)
    assert states.destinos(r, Rol.LIDER) == [Estado.ADJUDICADA]
    states.transicionar(r, Estado.ADJUDICADA, rol=Rol.LIDER, motivo="Sigue", fecha=HOY, perfiles_con_ingreso=1)
    assert (r.estado, r.estado_previo) == (Estado.ADJUDICADA, None)


def test_cerrar_y_cancelar_exigen_su_motivo():
    with pytest.raises(ErrorTransicionInvalida):
        states.transicionar(oportunidad(), Estado.CERRADA, rol=Rol.LIDER, motivo="x", fecha=HOY,
                            perfiles_con_ingreso=0, motivo_cierre=MotivoCierre.DUPLICADO)
    r = oportunidad()
    states.transicionar(r, Estado.CANCELADA, rol=Rol.LIDER, motivo="x", fecha=HOY, perfiles_con_ingreso=0,
                        motivo_cierre=MotivoCierre.DUPLICADO)
    assert (r.estado, r.motivo_cierre, r.fecha_cierre) == (Estado.CANCELADA, MotivoCierre.DUPLICADO, HOY)
    assert r.excluido_del_calculo


def test_solo_operaciones_reabre_y_una_demanda_vuelve_adjudicada():
    r = Registro(codigo="OPD-0003", tipo=Tipo.DEMANDA, estado=Estado.CERRADA, motivo_cierre=MotivoCierre.PERDIDA)
    assert states.destinos(r, Rol.LIDER) == []
    with pytest.raises(ErrorTransicionInvalida, match="Operaciones"):
        states.transicionar(r, Estado.PENDIENTE, rol=Rol.LIDER, motivo="x", fecha=HOY, perfiles_con_ingreso=1)
    states.transicionar(r, Estado.PENDIENTE, rol=Rol.OPERACIONES, motivo="Error", fecha=HOY, perfiles_con_ingreso=1)
    assert (r.estado, r.motivo_cierre, r.fecha_cierre) == (Estado.ADJUDICADA, None, None)


def test_continuidad_no_pasa_por_pendiente_ni_cambia_de_flujo():
    r = Registro(codigo="OPD-0004", tipo=Tipo.CONTINUIDAD, estado=Estado.EN_CURSO, flujo=Flujo.PERFILES_SELECCIONADOS)
    assert Estado.PENDIENTE not in states.destinos(r, Rol.OPERACIONES)
    with pytest.raises(ErrorTransicionInvalida, match="flujo 6"):
        states.cambiar_flujo(r, Flujo.PENDIENTE_RFP, perfiles_con_ingreso=1)
    r.estado = Estado.CERRADA
    assert states.destinos(r, Rol.OPERACIONES) == [Estado.EN_CURSO]


def test_flujo_en_pendiente_sugiere_probabilidad_y_confirmar_perfiles_exige_adjudicar():
    r = oportunidad()
    states.cambiar_flujo(r, Flujo.VALIDANDO_CANDIDATOS, perfiles_con_ingreso=0)
    assert r.probabilidad_bp == 7_500
    with pytest.raises(ErrorTransicionInvalida, match="adjudica"):
        states.cambiar_flujo(r, Flujo.PERFILES_SELECCIONADOS, perfiles_con_ingreso=1)
    d = Registro(codigo="OPD-0005", tipo=Tipo.DEMANDA, estado=Estado.ADJUDICADA, probabilidad_bp=10_000)
    with pytest.raises(ErrorTransicionInvalida, match="perfil"):
        states.cambiar_flujo(d, Flujo.PERFILES_SELECCIONADOS, perfiles_con_ingreso=0)
    states.cambiar_flujo(d, Flujo.PERFILES_SELECCIONADOS, perfiles_con_ingreso=1)
    assert d.probabilidad_bp == 10_000 and states.probabilidad_fija(d)
    d.estado = Estado.STANDBY
    with pytest.raises(ErrorTransicionInvalida):
        states.cambiar_flujo(d, Flujo.PENDIENTE_CANDIDATOS, perfiles_con_ingreso=1)


def test_permisos_de_edicion_por_rol_y_propiedad():
    from uuid import uuid4

    lider, otro = uuid4(), uuid4()
    r = oportunidad(owner_id=lider)
    assert states.puede_editar(Rol.LIDER, lider, r)
    assert not states.puede_editar(Rol.LIDER, otro, r)
    assert states.puede_editar(Rol.OPERACIONES, otro, r)
    assert not states.puede_editar(Rol.EJECUTIVO, lider, r)
