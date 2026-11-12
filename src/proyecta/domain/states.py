"""Transiciones de estado y flujo del registro (T052–T055, US2; data-model.md «State Machine»).

Funciones puras: validan la transición y devuelven los cambios de campo que produce,
para que el caso de uso los audite uno por uno. No guardan ni conocen HTTP.
Implementación mínima para la Entrega 2; Felipe es el responsable del frente y la revisa.
"""

from __future__ import annotations

from datetime import date

from proyecta.domain.entities import Registro
from proyecta.domain.enums import (
    BP_TOTAL,
    PROBABILIDAD_SUGERIDA_POR_FLUJO_BP,
    Estado,
    Flujo,
    MotivoCierre,
    Rol,
    Tipo,
)
from proyecta.domain.errors import ErrorTransicionInvalida

# Destinos permitidos por estado de origen (los terminales solo se reabren).
_PERMITIDAS: dict[Estado, frozenset[Estado]] = {
    Estado.PENDIENTE: frozenset({Estado.ADJUDICADA, Estado.STANDBY, Estado.CERRADA, Estado.CANCELADA}),
    Estado.ADJUDICADA: frozenset({Estado.EN_CURSO, Estado.STANDBY, Estado.CERRADA, Estado.CANCELADA}),
    Estado.EN_CURSO: frozenset({Estado.STANDBY, Estado.CERRADA, Estado.CANCELADA}),
    Estado.STANDBY: frozenset(),  # solo se reactiva al estado previo
    Estado.CERRADA: frozenset({Estado.PENDIENTE, Estado.ADJUDICADA}),
    Estado.CANCELADA: frozenset({Estado.PENDIENTE, Estado.ADJUDICADA}),
}
MOTIVOS_CIERRE = frozenset({MotivoCierre.PERDIDA, MotivoCierre.DESESTIMADA, MotivoCierre.TERMINO_SERVICIO})
MOTIVOS_CANCELACION = frozenset({MotivoCierre.CANCELADA_CLIENTE, MotivoCierre.DUPLICADO})

Cambios = list[tuple[str, object, object]]  # (campo, valor anterior, valor nuevo)


def _falla(mensaje: str, **detalle: object) -> ErrorTransicionInvalida:
    return ErrorTransicionInvalida("TRANSICION_INVALIDA", mensaje, detalle=detalle or None)


def _asignar(registro: Registro, cambios: Cambios, campo: str, valor: object) -> None:
    anterior = getattr(registro, campo)
    if anterior != valor:
        cambios.append((campo, anterior, valor))
        setattr(registro, campo, valor)


def destinos(registro: Registro, rol: Rol) -> list[Estado]:
    """Estados a los que el usuario puede llevar el registro (para ofrecer solo acciones válidas)."""
    if registro.estado is Estado.STANDBY:
        return [registro.estado_previo] if registro.estado_previo else []
    opciones = set(_PERMITIDAS[registro.estado])
    if registro.es_terminal and rol is not Rol.OPERACIONES:
        return []
    if registro.tipo is Tipo.CONTINUIDAD:
        opciones -= {Estado.PENDIENTE, Estado.ADJUDICADA}
        if registro.es_terminal:
            opciones = {Estado.EN_CURSO}
    return sorted(opciones, key=list(Estado).index)


def transicionar(
    registro: Registro,
    destino: Estado,
    *,
    rol: Rol,
    motivo: str,
    fecha: date,
    perfiles_con_ingreso: int,
    motivo_cierre: MotivoCierre | None = None,
) -> Cambios:
    """Aplica la transición sobre `registro` y devuelve los cambios; si no corresponde, no toca nada."""
    motivo = (motivo or "").strip()
    if not motivo:
        raise _falla("Toda transición exige un motivo escrito (FR-018).")
    if destino not in destinos(registro, rol):
        if registro.estado is Estado.PENDIENTE and destino is Estado.EN_CURSO:
            raise _falla("Una oportunidad Pendiente debe adjudicarse antes de pasar a En Curso.")
        if registro.es_terminal and rol is not Rol.OPERACIONES:
            raise _falla("Solo Operaciones puede reabrir un registro cerrado o cancelado (FR-023).")
        raise _falla(f"No se puede pasar de {registro.estado.value} a {destino.value}.")
    if destino in (Estado.ADJUDICADA, Estado.EN_CURSO) and not registro.es_terminal and perfiles_con_ingreso < 1:
        raise _falla("Se requiere al menos un perfil con HC y fecha de ingreso (US2, escenario 5).")
    if destino is Estado.CERRADA and motivo_cierre not in MOTIVOS_CIERRE:
        raise _falla("Cerrar exige motivo: Pérdida, Desestimada o Término de servicio.")
    if destino is Estado.CANCELADA and motivo_cierre not in MOTIVOS_CANCELACION:
        raise _falla("Cancelar exige motivo: Cancelada por el cliente o Duplicado.")

    cambios: Cambios = []
    if registro.estado is Estado.STANDBY:  # reactivación: restaura el estado previo
        _asignar(registro, cambios, "estado", destino)
        _asignar(registro, cambios, "estado_previo", None)
        return cambios
    if destino is Estado.STANDBY:
        _asignar(registro, cambios, "estado_previo", registro.estado)
        _asignar(registro, cambios, "estado", destino)
        return cambios
    if destino in (Estado.CERRADA, Estado.CANCELADA):
        _asignar(registro, cambios, "estado", destino)
        _asignar(registro, cambios, "motivo_cierre", motivo_cierre)
        _asignar(registro, cambios, "fecha_cierre", fecha)
        if destino is Estado.CANCELADA:
            _asignar(registro, cambios, "fecha_cancelacion", fecha)
        return cambios
    if registro.es_terminal:  # reapertura por Operaciones
        _asignar(registro, cambios, "estado", destino)
        _asignar(registro, cambios, "motivo_cierre", None)
        _asignar(registro, cambios, "fecha_cierre", None)
        _asignar(registro, cambios, "fecha_cancelacion", None)
        if destino is Estado.PENDIENTE and registro.tipo is Tipo.DEMANDA:
            _asignar(registro, cambios, "estado", Estado.ADJUDICADA)  # una demanda vuelve adjudicada
        return cambios
    if destino is Estado.ADJUDICADA:  # F1: adjudicar
        _asignar(registro, cambios, "estado", destino)
        _asignar(registro, cambios, "tipo", Tipo.DEMANDA)
        _asignar(registro, cambios, "fecha_adjudicacion", fecha)
        if registro.flujo.orden < Flujo.PROPUESTA_ENTREGADA.orden:
            _asignar(registro, cambios, "flujo", Flujo.PROPUESTA_ENTREGADA)
        _asignar(registro, cambios, "probabilidad_bp", BP_TOTAL)  # H-01: 100 % al adjudicar
        return cambios
    # ADJUDICADA → EN_CURSO
    _asignar(registro, cambios, "estado", destino)
    _asignar(registro, cambios, "flujo", Flujo.PERFILES_SELECCIONADOS)
    _asignar(registro, cambios, "probabilidad_bp", BP_TOTAL)
    return cambios


def cambiar_flujo(registro: Registro, flujo: Flujo, *, perfiles_con_ingreso: int) -> Cambios:
    """Avanza o retrocede la etapa comercial; en Pendiente sugiere la probabilidad del flujo (FR-019)."""
    if registro.tipo is Tipo.CONTINUIDAD:
        raise _falla("Una continuidad siempre está en el flujo 6 (FR-025).")
    if registro.es_terminal or registro.estado is Estado.STANDBY:
        raise _falla("No se cambia el flujo de un registro cerrado, cancelado o en StandBy.")
    if registro.tipo is Tipo.OPORTUNIDAD and flujo is Flujo.PERFILES_SELECCIONADOS:
        raise _falla("Para confirmar perfiles, primero adjudica la oportunidad.")
    if flujo is Flujo.PERFILES_SELECCIONADOS and perfiles_con_ingreso < 1:
        raise _falla("Confirmar perfiles exige al menos un perfil con HC y fecha de ingreso.")
    cambios: Cambios = []
    _asignar(registro, cambios, "flujo", flujo)
    if registro.estado is Estado.PENDIENTE:
        _asignar(registro, cambios, "probabilidad_bp", PROBABILIDAD_SUGERIDA_POR_FLUJO_BP[flujo])
    return cambios


def probabilidad_fija(registro: Registro) -> bool:
    """P queda en 100 % sin edición en Adjudicada, En Curso, Perfiles seleccionados y Continuidad (FR-020)."""
    return (
        registro.estado in (Estado.ADJUDICADA, Estado.EN_CURSO)
        or registro.flujo is Flujo.PERFILES_SELECCIONADOS
        or registro.tipo is Tipo.CONTINUIDAD
    )


def puede_editar(rol: Rol, usuario_id, registro: Registro) -> bool:
    """Operaciones edita todo; el líder solo lo suyo; el ejecutivo nada (US8, escenarios 3 y 4)."""
    if rol is Rol.OPERACIONES:
        return True
    return rol is Rol.LIDER and registro.owner_id == usuario_id
