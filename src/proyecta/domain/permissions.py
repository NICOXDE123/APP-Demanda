"""Políticas de rol y propiedad (T028, FR-061 a FR-067, RN-01, AC-10).

Dominio puro: no importa FastAPI, Datastore ni Jinja2. Toda decisión sale de
la matriz de permisos de ``spec.md`` (sección «Matriz de permisos»).

Interfaz para la capa de aplicación e interfaces (Matías / casos de uso)
------------------------------------------------------------------------
1. Construir el ``Actor`` desde la sesión autenticada::

       actor = Actor(usuario_id=str(usuario.id), rol=usuario.rol, activo=usuario.activo)

   ``rol`` acepta el enum ``Rol`` (T012) o su valor de texto
   (``"LIDER"``, ``"OPERACIONES"``, ``"EJECUTIVO"``).

2. Antes de escribir, en el caso de uso (no en la plantilla)::

       exigir(actor, Accion.EDITAR_REGISTRO, owner_id=registro.owner_id)

   Lanza ``PermisoDenegado`` (HTTP 403, ``code`` = ``PERMISO_DENEGADO``) o, para
   editar/borrar bitácora, auditoría o registros, ``OperacionNoPermitida``
   (HTTP 405, ``code`` = ``OPERACION_NO_PERMITIDA``). Ambas heredan de
   ``ErrorAutorizacion`` (``errors.py``) y tienen ``code``, ``message`` y
   ``status_sugerido``, como el esquema ``Error`` del OpenAPI. El caso de uso no debe haber modificado nada.

3. Para listados, dashboards y exportaciones usar ``alcance`` y filtrar::

       match alcance(actor, Accion.EXPORTAR):
           case Alcance.TODOS: ...
           case Alcance.PROPIOS: ...   # filtrar por owner_id == actor.usuario_id
           case Alcance.NINGUNO: ...   # rechazar

4. Para ocultar botones y menús: ``acciones_permitidas(actor)``.

Reglas de seguridad: el sistema niega por defecto (acción desconocida, actor
inactivo, rol desconocido o propiedad no informada se rechazan).

Las excepciones (``PermisoDenegado`` 403 y ``OperacionNoPermitida`` 405) viven
en ``errors.py`` (T016) y heredan de ``ErrorDominio``; aquí solo se importan.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from proyecta.domain.errors import OperacionNoPermitida, PermisoDenegado



class Accion(str, Enum):
    """Acciones autorizables; una por fila de la matriz de permisos."""

    # Registros
    CREAR_REGISTRO = "CREAR_REGISTRO"
    CREAR_CONTINUIDAD = "CREAR_CONTINUIDAD"  # transición «Nueva continuidad»
    VER_REGISTRO = "VER_REGISTRO"
    EDITAR_REGISTRO = "EDITAR_REGISTRO"  # datos, perfiles, fechas y estado
    CAMBIAR_TIPO_FLUJO = "CAMBIAR_TIPO_FLUJO"
    REABRIR_REGISTRO = "REABRIR_REGISTRO"  # solo Operaciones (RN-26)
    # Bitácora y auditoría
    ESCRIBIR_BITACORA = "ESCRIBIR_BITACORA"  # incluye correcciones por referencia
    CONSULTAR_AUDITORIA = "CONSULTAR_AUDITORIA"
    # Ajustes reservados a Operaciones
    AJUSTAR_CONFIABILIDAD = "AJUSTAR_CONFIABILIDAD"
    AJUSTAR_HC = "AJUSTAR_HC"
    # Configuración
    MANTENER_PARAMETROS = "MANTENER_PARAMETROS"  # parámetros y catálogos
    MANTENER_USUARIOS = "MANTENER_USUARIOS"  # incluye roles
    MANTENER_METAS = "MANTENER_METAS"
    VER_METAS = "VER_METAS"
    # Backlog y contratos
    MANTENER_CONTRATO = "MANTENER_CONTRATO"
    VER_CONTRATO = "VER_CONTRATO"
    # Cortes
    CERRAR_PERIODO = "CERRAR_PERIODO"
    VER_CORTES = "VER_CORTES"  # comparar cortes y puente
    # Lectura transversal
    VER_DASHBOARD = "VER_DASHBOARD"
    EXPORTAR = "EXPORTAR"
    # Siempre denegadas (FR-055, RN-78, RN-81): se corrige con una entrada nueva
    EDITAR_BITACORA = "EDITAR_BITACORA"
    BORRAR_BITACORA = "BORRAR_BITACORA"
    EDITAR_AUDITORIA = "EDITAR_AUDITORIA"
    BORRAR_AUDITORIA = "BORRAR_AUDITORIA"
    ELIMINAR_REGISTRO = "ELIMINAR_REGISTRO"  # se cierra con motivo


class Alcance(str, Enum):
    """Sobre qué registros puede actuar un rol para una acción."""

    NINGUNO = "NINGUNO"
    PROPIOS = "PROPIOS"
    TODOS = "TODOS"


_L, _O, _E = "LIDER", "OPERACIONES", "EJECUTIVO"
_N, _P, _T = Alcance.NINGUNO, Alcance.PROPIOS, Alcance.TODOS

# Acción -> (Líder, Operaciones, Ejecutivo). Fuente: spec.md, «Matriz de permisos».
_MATRIZ: dict[Accion, tuple[Alcance, Alcance, Alcance]] = {
    Accion.CREAR_REGISTRO: (_T, _T, _N),
    Accion.CREAR_CONTINUIDAD: (_N, _T, _N),
    Accion.VER_REGISTRO: (_P, _T, _T),
    Accion.EDITAR_REGISTRO: (_P, _T, _N),
    Accion.CAMBIAR_TIPO_FLUJO: (_P, _T, _N),
    Accion.REABRIR_REGISTRO: (_N, _T, _N),
    Accion.ESCRIBIR_BITACORA: (_P, _T, _N),
    Accion.CONSULTAR_AUDITORIA: (_P, _T, _T),
    Accion.AJUSTAR_CONFIABILIDAD: (_N, _T, _N),
    Accion.AJUSTAR_HC: (_N, _T, _N),
    Accion.MANTENER_PARAMETROS: (_N, _T, _N),
    Accion.MANTENER_USUARIOS: (_N, _T, _N),
    Accion.MANTENER_METAS: (_N, _T, _N),
    Accion.VER_METAS: (_N, _T, _T),
    Accion.MANTENER_CONTRATO: (_P, _T, _N),
    Accion.VER_CONTRATO: (_P, _T, _T),
    Accion.CERRAR_PERIODO: (_N, _T, _N),
    Accion.VER_CORTES: (_N, _T, _T),
    Accion.VER_DASHBOARD: (_P, _T, _T),
    Accion.EXPORTAR: (_P, _T, _T),
    Accion.EDITAR_BITACORA: (_N, _N, _N),
    Accion.BORRAR_BITACORA: (_N, _N, _N),
    Accion.EDITAR_AUDITORIA: (_N, _N, _N),
    Accion.BORRAR_AUDITORIA: (_N, _N, _N),
    Accion.ELIMINAR_REGISTRO: (_N, _N, _N),
}
_INDICE_ROL = {_L: 0, _O: 1, _E: 2}


ACCIONES_INMUTABLES = frozenset(
    {
        Accion.EDITAR_BITACORA,
        Accion.BORRAR_BITACORA,
        Accion.EDITAR_AUDITORIA,
        Accion.BORRAR_AUDITORIA,
        Accion.ELIMINAR_REGISTRO,
    }
)


@dataclass(frozen=True, slots=True)
class Actor:
    """Usuario autenticado que intenta la operación."""

    usuario_id: str
    rol: object  # ``Rol`` (T012) o su valor de texto
    activo: bool = True


@dataclass(frozen=True, slots=True)
class Decision:
    permitido: bool
    motivo: str | None = None

    def __bool__(self) -> bool:
        return self.permitido


_OK = Decision(True)


def _rol_valor(rol: object) -> str:
    valor = getattr(rol, "value", rol)
    return str(valor).upper()


def alcance(actor: Actor, accion: Accion) -> Alcance:
    """Alcance del actor para la acción; ``NINGUNO`` si no puede ejecutarla."""
    if not actor.activo:
        return Alcance.NINGUNO
    fila = _MATRIZ.get(accion)
    indice = _INDICE_ROL.get(_rol_valor(actor.rol))
    if fila is None or indice is None:
        return Alcance.NINGUNO
    return fila[indice]


def evaluar(actor: Actor, accion: Accion, *, owner_id: object | None = None) -> Decision:
    """Decide si ``actor`` puede ejecutar ``accion`` sobre un recurso de ``owner_id``.

    Con alcance ``PROPIOS`` el ``owner_id`` es obligatorio: si falta, se niega.
    """
    if not actor.activo:
        return Decision(False, "Usuario inactivo")
    nivel = alcance(actor, accion)
    if nivel is Alcance.TODOS:
        return _OK
    if nivel is Alcance.NINGUNO:
        return Decision(False, f"El rol {_rol_valor(actor.rol)} no puede ejecutar {accion.value}")
    if owner_id is None:
        return Decision(False, "Propiedad del recurso no informada")
    if str(owner_id) != str(actor.usuario_id):
        return Decision(False, "El registro pertenece a otro líder")
    return _OK


def autorizado(actor: Actor, accion: Accion, *, owner_id: object | None = None) -> bool:
    return evaluar(actor, accion, owner_id=owner_id).permitido


def exigir(actor: Actor, accion: Accion, *, owner_id: object | None = None) -> None:
    """Lanza ``OperacionNoPermitida`` (405) para acciones inmutables y
    ``PermisoDenegado`` (403) para el resto si la operación no está permitida."""
    if accion in ACCIONES_INMUTABLES:
        raise OperacionNoPermitida(
            message="Bitácora, auditoría y registros no se editan ni se borran",
            accion=accion.value,
        )
    decision = evaluar(actor, accion, owner_id=owner_id)
    if not decision.permitido:
        raise PermisoDenegado(
            message=decision.motivo or "Operación no autorizada",
            accion=accion.value,
        )


def acciones_permitidas(actor: Actor) -> frozenset[Accion]:
    """Acciones con algún alcance; sirve para mostrar u ocultar opciones en la UI."""
    return frozenset(a for a in Accion if alcance(actor, a) is not Alcance.NINGUNO)


def puede_cambiar_rol(actor: Actor, objetivo_id: object) -> Decision:
    """FR-064: un líder no cambia su propio rol ni el de otra persona."""
    del objetivo_id  # la decisión depende solo del rol del actor
    return evaluar(actor, Accion.MANTENER_USUARIOS)


def puede_desactivar_usuario(
    actor: Actor, objetivo_rol: object, objetivo_activo: bool, operaciones_activos: int
) -> Decision:
    """FR-065: no se puede desactivar al último usuario de Operaciones.

    ``operaciones_activos`` lo calcula el caso de uso (conteo de usuarios
    activos con rol OPERACIONES) para mantener el dominio sin Datastore.
    """
    base = evaluar(actor, Accion.MANTENER_USUARIOS)
    if not base.permitido:
        return base
    if (
        objetivo_activo
        and _rol_valor(objetivo_rol) == _O
        and operaciones_activos <= 1
    ):
        return Decision(False, "No se puede desactivar al último usuario de Operaciones")
    return _OK
