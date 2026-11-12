"""Inicio y cierre de sesión (US8, FR-066)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse

from proyecta.infrastructure.auth.sessions import AccesoDenegado
from proyecta.interfaces.web.comun import exigir_csrf, render, texto

COOKIE = "proyecta_sesion"
router = APIRouter()


@router.get("/login")
def formulario(request: Request):
    return render(request, "login.html")


@router.post("/login")
async def iniciar(request: Request):
    form = await request.form()
    ip = request.client.host if request.client else "desconocida"
    try:
        sesion = request.app.state.autenticador.iniciar(
            texto(form, "email"), form.get("password") or "", ip, request.headers.get("user-agent"))
    except AccesoDenegado as error:
        return render(request, "login.html", {"error": str(error), "email": texto(form, "email")}, status_code=401)
    respuesta = RedirectResponse("/", status_code=303)
    respuesta.set_cookie(COOKIE, sesion.id, httponly=True, samesite="strict",
                         secure=request.app.state.cookie_segura, max_age=8 * 3600)
    return respuesta


@router.post("/logout", dependencies=[Depends(exigir_csrf)])
def cerrar(request: Request):
    request.app.state.autenticador.cerrar(request.cookies.get(COOKIE))
    respuesta = RedirectResponse("/login", status_code=303)
    respuesta.delete_cookie(COOKIE)
    return respuesta
