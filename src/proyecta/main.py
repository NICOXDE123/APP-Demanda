"""Punto de entrada de Proyecta (T007, T034): arma la app, conecta casos de uso y repositorios,
exige sesión en todo salvo /login, /health y /static, y agrega cabeceras de seguridad (RNF-05).
"""

from __future__ import annotations

import os
from dataclasses import dataclass, replace
from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from proyecta.application.services.audit import ServicioAuditoria
from proyecta.application.use_cases.calculo import CalcularProyeccion
from proyecta.application.use_cases.registros import ServicioRegistros
from proyecta.domain.enums import Rol
from proyecta.infrastructure.auth.sessions import Autenticador
from proyecta.infrastructure.memoria import Almacen, Registros
from proyecta.interfaces.api.v1 import forecast
from proyecta.interfaces.web.comun import render
from proyecta.interfaces.web.routes import admin, dashboard, registros, sesion

WEB = Path(__file__).parent / "interfaces" / "web"
PUBLICAS = ("/login", "/health", "/static/")
CSP = ("default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; "
       "connect-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'")


@dataclass
class SoloDelLider:
    """Vista de registros limitada al owner: el líder lee solo sus agregados (US8 esc. 3)."""

    registros: Registros
    owner_id: UUID

    def obtener(self, registro_id):
        r = self.registros.obtener(registro_id)
        return r if r and r.owner_id == self.owner_id else None

    def listar(self, **filtros):
        return self.registros.listar(**{**filtros, "owner_id": self.owner_id})


def crear_app(almacen: Almacen | None = None) -> FastAPI:
    entorno = os.environ.get("PROYECTA_ENV", "dev")
    app = FastAPI(title="Proyecta", version="0.2.0", docs_url="/api/docs" if entorno == "dev" else None,
                  redoc_url=None, openapi_url="/api/openapi.json" if entorno == "dev" else None)
    almacen = almacen or Almacen.con_semilla()
    calculo = CalcularProyeccion(almacen.registros, almacen.perfiles, almacen.contratos, almacen.parametros,
                                 almacen.vigencias)
    app.state.almacen = almacen
    app.state.calculo = calculo
    app.state.registros = ServicioRegistros(almacen, calculo, ServicioAuditoria(almacen.auditoria))
    app.state.autenticador = Autenticador(almacen.usuarios, almacen.sesiones)
    app.state.cookie_segura = entorno != "dev"

    @app.middleware("http")
    async def sesion_y_cabeceras(request: Request, call_next):
        request.state.usuario = request.state.sesion = None
        actual = app.state.autenticador.usuario_de(request.cookies.get(sesion.COOKIE))
        if actual:
            request.state.usuario, request.state.sesion = actual
        if not actual and not request.url.path.startswith(PUBLICAS):
            if request.url.path.startswith("/api/"):
                respuesta = JSONResponse({"code": "NO_AUTENTICADO", "message": "Inicia sesión."}, status_code=401)
            else:
                respuesta = RedirectResponse("/login", status_code=303)
        else:
            respuesta = await call_next(request)
        respuesta.headers.update({
            "Content-Security-Policy": CSP, "X-Content-Type-Options": "nosniff", "X-Frame-Options": "DENY",
            "Referrer-Policy": "same-origin", "Cache-Control": "no-store",
        })
        if app.state.cookie_segura:
            respuesta.headers["Strict-Transport-Security"] = "max-age=31536000"
        return respuesta

    @app.exception_handler(StarletteHTTPException)
    async def error_http(request: Request, error: StarletteHTTPException):
        if request.url.path.startswith("/api/") or error.status_code == 405:
            return JSONResponse({"detail": error.detail}, status_code=error.status_code)
        return render(request, "error.html", {"codigo": error.status_code, "detalle": error.detail},
                      status_code=error.status_code)

    api = APIRouter(prefix="/api/v1")
    api.include_router(forecast.router)

    @api.get("/registros/{registro_id}/auditoria")
    def auditoria_registro(request: Request, registro_id: UUID):
        """Contrato de openapi.yaml: solo GET; PUT y DELETE responden 405 (RN-78)."""
        registro = almacen.registros.obtener(registro_id)
        usuario = request.state.usuario
        if registro is None or (usuario.rol is Rol.LIDER and registro.owner_id != usuario.id):
            raise HTTPException(404, "Registro no encontrado")
        return almacen.auditoria.listar_por_registro(registro_id)

    app.include_router(api)
    def calculo_segun_rol(request: Request) -> CalcularProyeccion:
        usuario = request.state.usuario
        if usuario.rol is Rol.LIDER:
            return replace(calculo, registros=SoloDelLider(almacen.registros, usuario.id))
        return calculo

    app.dependency_overrides[forecast.obtener_calculo] = calculo_segun_rol
    app.include_router(sesion.router)
    app.include_router(dashboard.router)
    app.include_router(registros.router)
    app.include_router(admin.router)
    app.mount("/static", StaticFiles(directory=WEB / "static"), name="static")
    app.add_api_route("/health", lambda: {"status": "ok"})
    return app


app = crear_app()
