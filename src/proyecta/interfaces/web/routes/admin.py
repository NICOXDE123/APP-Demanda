"""Mantenedor de parámetros de la MAB (RF-51, FR-037) y consulta de auditoría (US8 esc. 5)."""

from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse

from proyecta.domain.enums import Rol
from proyecta.domain.errors import ErrorDominio
from proyecta.interfaces.web.comun import a_entero, a_fecha, exigir_csrf, exigir_rol, render, texto

router = APIRouter(dependencies=[Depends(exigir_csrf)])


def _parametros(request: Request, error: str | None = None, status_code: int = 200):
    almacen = request.app.state.almacen
    return render(request, "parametros.html", {
        "horas": list(reversed(almacen.parametros.listar("horas_mensuales"))),
        "vigente": almacen.parametros.vigente("horas_mensuales", date.today()),
        "otros": [p for p in almacen.parametros.listar() if p.clave != "horas_mensuales"],
        "error": error, "ok": request.query_params.get("ok"),
    }, status_code=status_code)


@router.get("/parametros")
def parametros(request: Request):
    return _parametros(request)


@router.post("/parametros/horas")
async def cambiar_horas(request: Request):
    exigir_rol(request, Rol.OPERACIONES)
    form = await request.form()
    try:
        request.app.state.registros.cambiar_horas(
            request.state.usuario, a_entero(form.get("horas")) or 0,
            a_fecha(form.get("desde")) or date.today(), texto(form, "motivo"))
    except ErrorDominio as error:
        return _parametros(request, error.message, error.status_sugerido)
    return RedirectResponse("/parametros?ok=1", status_code=303)


@router.get("/auditoria")
def auditoria(request: Request):
    """Eventos filtrables por registro, usuario, campo y fecha; el líder ve solo los de sus registros."""
    exigir_rol(request, Rol.OPERACIONES, Rol.EJECUTIVO, Rol.LIDER)
    almacen = request.app.state.almacen
    usuario = request.state.usuario
    q = request.query_params
    codigo = (q.get("codigo") or "").strip().upper()
    campo = (q.get("campo") or "").strip().lower()
    autor = q.get("usuario") or ""
    desde, hasta = a_fecha(q.get("desde")), a_fecha(q.get("hasta"))
    codigos = {r.id: r.codigo for r in almacen.registros.listar()}
    eventos = []
    for e in almacen.auditoria.todos():
        registro = almacen.registros.obtener(e.registro_id)
        if usuario.rol is Rol.LIDER and (registro is None or registro.owner_id != usuario.id):
            continue
        if codigo and codigos.get(e.registro_id, "") != codigo:
            continue
        if campo and campo not in e.campo.lower():
            continue
        if autor and str(e.usuario_id) != autor:
            continue
        dia = e.fecha_hora.date()
        if (desde and dia < desde) or (hasta and dia > hasta):
            continue
        eventos.append(e)
    return render(request, "auditoria.html", {
        "eventos": eventos[:500], "total": len(eventos), "codigos": codigos, "usuarios": almacen.usuarios.listar(),
        "q": {"codigo": codigo, "campo": campo, "usuario": autor, "desde": q.get("desde") or "", "hasta": q.get("hasta") or ""},
    })
