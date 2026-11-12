"""Piezas compartidas de la interfaz web: plantillas, formatos es-CL, sesión y CSRF.

Las rutas solo traducen HTTP a casos de uso y renderizan; no tienen fórmulas (Principio II).
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any
from uuid import UUID
from zoneinfo import ZoneInfo

from fastapi import HTTPException, Request
from fastapi.templating import Jinja2Templates

from proyecta.domain.enums import Rol
from proyecta.infrastructure.auth.sessions import csrf_valido

SANTIAGO = ZoneInfo("America/Santiago")
MESES = "ene feb mar abr may jun jul ago sep oct nov dic".split()

ETIQUETAS = {
    "OPORTUNIDAD": "Oportunidad", "DEMANDA": "Demanda", "CONTINUIDAD": "Continuidad",
    "PENDIENTE": "Pendiente", "ADJUDICADA": "Adjudicada", "EN_CURSO": "En Curso", "STANDBY": "StandBy",
    "CERRADA": "Cerrada", "CANCELADA": "Cancelada",
    "PENDIENTE_RFP": "1 · Pendiente RFP", "PROPUESTA_EN_CURSO": "2 · Propuesta en curso",
    "PROPUESTA_ENTREGADA": "3 · Propuesta entregada", "PENDIENTE_CANDIDATOS": "4 · Pendiente candidatos",
    "VALIDANDO_CANDIDATOS": "5 · Validando candidatos", "PERFILES_SELECCIONADOS": "6 · Perfiles seleccionados",
    "LIDER": "Líder", "OPERACIONES": "Operaciones", "EJECUTIVO": "Ejecutivo",
    "NTT": "NTT", "SUBCONTRATACION": "Subcontratación",
    "PERDIDA": "Pérdida", "DESESTIMADA": "Desestimada", "CANCELADA_CLIENTE": "Cancelada por el cliente",
    "TERMINO_SERVICIO": "Término de servicio", "DUPLICADO": "Duplicado",
    "SEGUIMIENTO": "Seguimiento", "DECISION": "Decisión", "REUNION": "Reunión", "ESTADO": "Estado",
    "INCIDENCIA": "Incidencia", "MIGRACION": "Migración",
    "MAB": "MAB", "BACKLOG_CONTRACTUAL": "Backlog contractual",
    "REGISTRO": "Registro", "PERFIL": "Perfil", "TARIFA": "Tarifa", "PARAMETRO": "Parámetro",
    "INTERFAZ": "Interfaz", "IA": "IA", "CARGA": "Carga",
}


def _v(x: Any) -> Any:
    return getattr(x, "value", x)


def pesos(n: int | None) -> str:
    """CLP con punto de miles (NFR-009)."""
    if n is None:
        return "—"
    return ("−$" if n < 0 else "$") + f"{abs(int(n)):,}".replace(",", ".")


def pct(bp: int | None) -> str:
    return "—" if bp is None else f"{bp / 100:g} %".replace(".", ",")


def fecha(d: date | None) -> str:
    return d.strftime("%d-%m-%Y") if d else "—"


def mes(m: Any) -> str:
    inicio = getattr(m, "inicio", m)
    return f"{MESES[inicio.month - 1]} {inicio.year}"


def local(t: datetime | None) -> str:
    return t.astimezone(SANTIAGO).strftime("%d-%m-%Y %H:%M") if t else "—"


def valor(v: Any, campo: str = "") -> str:
    """Valor de auditoría legible: etiquetas en español, porcentajes desde puntos base y tarifas en pesos."""
    if v is None:
        return "—"
    if campo.endswith("_bp") and isinstance(v, int):
        return pct(v)
    if campo.startswith("tarifa") and isinstance(v, int):
        return pesos(round(v / 100)) + "/h"
    if isinstance(v, dict):
        return " · ".join(f"{k.replace('_bp', '')}: {pct(x) if k.endswith('_bp') else ETIQUETAS.get(x, x)}"
                          for k, x in v.items())
    return str(ETIQUETAS.get(v, v)) if isinstance(v, str) else str(v)


templates = Jinja2Templates(directory=Path(__file__).parent / "templates")  # autoescape activo
templates.env.filters.update(pesos=pesos, pct=pct, valor=valor, fecha=fecha, mes=mes, local=local,
                             etiqueta=lambda x: ETIQUETAS.get(_v(x), _v(x) or "—"),
                             centavos=lambda c: pesos(round(c / 100)) if c is not None else "—")


def render(request: Request, plantilla: str, contexto: dict[str, Any] | None = None, status_code: int = 200):
    usuario = getattr(request.state, "usuario", None)
    sesion = getattr(request.state, "sesion", None)
    almacen = request.app.state.almacen
    base = {"usuario": usuario, "csrf": sesion.csrf_token if sesion else "",
            "rol": usuario.rol.value if usuario else None, "cat": almacen.catalogos.etiqueta,
            "nombre_usuario": lambda uid: (almacen.usuarios.obtener(uid).nombre if uid and almacen.usuarios.obtener(uid) else "—")}
    return templates.TemplateResponse(request, plantilla, {**base, **(contexto or {})}, status_code=status_code)


# -- Seguridad --------------------------------------------------------------

async def exigir_csrf(request: Request) -> None:
    """Dependencia de los routers web: todo POST lleva el token de la sesión (RNF-05)."""
    if request.method != "POST":
        return
    sesion = getattr(request.state, "sesion", None)
    enviado = request.headers.get("X-CSRF-Token")
    if not enviado:
        enviado = (await request.form()).get("csrf_token")
    if sesion is None or not csrf_valido(sesion, enviado):
        raise HTTPException(403, "Token CSRF inválido o ausente; recarga la página.")


def exigir_rol(request: Request, *roles: Rol) -> None:
    if request.state.usuario.rol not in roles:
        raise HTTPException(403, "Tu rol no tiene acceso a esta sección.")


# -- Lectura de formularios ---------------------------------------------------

def texto(form, campo: str) -> str:
    return (form.get(campo) or "").strip()


def a_fecha(valor: str | None) -> date | None:
    try:
        return date.fromisoformat(valor) if valor else None
    except ValueError:
        return None


def a_entero(valor: str | None) -> int | None:
    try:
        return int(str(valor).strip()) if valor not in (None, "") else None
    except ValueError:
        return None


def a_uuid(valor: str | None) -> UUID | None:
    try:
        return UUID(valor) if valor else None
    except ValueError:
        return None


def a_centavos(valor: str | None) -> int | None:
    """Monto en pesos escrito a la chilena («25.000» o «25000,50») → centavos."""
    if not valor:
        return None
    limpio = str(valor).strip().replace("$", "").replace(".", "").replace(",", ".")
    try:
        monto = Decimal(limpio)
    except InvalidOperation:
        return None
    return int(monto * 100) if monto.is_finite() else None


def a_bp(valor: str | None) -> int | None:
    """Porcentaje («50» o «12,5») → puntos base."""
    if valor in (None, ""):
        return None
    try:
        p = Decimal(str(valor).replace(",", ".").replace("%", "").strip())
    except InvalidOperation:
        return None
    return int(p * 100) if p.is_finite() else None
