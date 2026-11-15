"""Mantenedor de parámetros de la MAB (RF-51, FR-037) y consulta de auditoría (US8 esc. 5)."""

from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse

from proyecta.domain.enums import Rol
from proyecta.domain.errors import ErrorDominio
from proyecta.interfaces.web.comun import a_entero, a_fecha, a_uuid, exigir_csrf, exigir_rol, render, texto, errores_por_campo

router = APIRouter(dependencies=[Depends(exigir_csrf)])


def _parametros(request: Request, error: str | None = None, status_code: int = 200, form=None):
    exigir_rol(request, Rol.OPERACIONES, Rol.LIDER)
    almacen = request.app.state.almacen
    usuario = request.state.usuario
    lideres = [u for u in almacen.usuarios.listar() if u.rol is Rol.LIDER]
    if usuario.rol is Rol.LIDER:
        lista_metas = almacen.metas.listar(lider_id=usuario.id)
    else:
        lista_metas = list(almacen.metas.datos)
    metas = sorted(
        lista_metas,
        key=lambda m: (m.mes, getattr(m, "actualizado_en", getattr(m, "creado_en", None)) or datetime.min),
        reverse=True,
    )[:10]
    horas = sorted(
        almacen.parametros.listar("horas_mensuales"),
        key=lambda p: (p.vigente_desde or date.min, getattr(p, "creado_en", None) or datetime.min),
        reverse=True,
    )
    confiabilidades = sorted(
        almacen.parametros.listar("confiabilidad_inicial"),
        key=lambda p: (p.vigente_desde or date.min, getattr(p, "creado_en", None) or datetime.min),
        reverse=True,
    )
    return render(request, "parametros.html", {
        "horas": horas,
        "vigente": almacen.parametros.vigente("horas_mensuales", date.today()),
        "confiabilidades": confiabilidades,
        "confiabilidad_vigente": almacen.parametros.vigente("confiabilidad_inicial", date.today()),
        "otros": [p for p in almacen.parametros.listar()
                  if p.clave not in {"horas_mensuales", "confiabilidad_inicial"}],
        "lideres": lideres,
        "metas": metas,
        "error": error, "ok": request.query_params.get("ok"),
        "form": dict(form or {}), "errores_campo": errores_por_campo([error], form or {}) if error else {},
    }, status_code=status_code)


@router.get("/parametros")
def parametros(request: Request):
    return _parametros(request)


@router.post("/parametros/metas")
async def cambiar_meta(request: Request):
    exigir_rol(request, Rol.OPERACIONES, Rol.LIDER)
    form = await request.form()
    usuario = request.state.usuario
    if usuario.rol is Rol.LIDER:
        lider_id = usuario.id
    else:
        lider_id = a_uuid(form.get("lider_id"))
    monto_clp = a_entero(form.get("monto")) or 0
    desde = a_fecha(form.get("desde")) or date.today()
    motivo = texto(form, "motivo")
    try:
        request.app.state.registros.cambiar_meta_lider(
            usuario, lider_id, monto_clp, desde, motivo
        )
    except ErrorDominio as error:
        return _parametros(request, error.message, error.status_sugerido, form)
    return RedirectResponse("/parametros?ok=1", status_code=303)


@router.post("/parametros/horas")
async def cambiar_horas(request: Request):
    exigir_rol(request, Rol.OPERACIONES)
    form = await request.form()
    try:
        request.app.state.registros.cambiar_horas(
            request.state.usuario, a_entero(form.get("horas")) or 0,
            a_fecha(form.get("desde")) or date.today(), texto(form, "motivo"))
    except ErrorDominio as error:
        return _parametros(request, error.message, error.status_sugerido, form)
    return RedirectResponse("/parametros?ok=1", status_code=303)


@router.post("/parametros/confiabilidad-inicial")
async def cambiar_confiabilidad_inicial(request: Request):
    exigir_rol(request, Rol.OPERACIONES)
    form = await request.form()
    valor = a_entero(form.get("valor"))
    try:
        request.app.state.registros.cambiar_confiabilidad_inicial(
            request.state.usuario, valor if valor is not None else -1,
            a_fecha(form.get("desde")) or date.today(), texto(form, "motivo"))
    except ErrorDominio as error:
        return _parametros(request, error.message, error.status_sugerido, form)
    return RedirectResponse("/parametros?ok=1", status_code=303)


@router.get("/auditoria")
def auditoria(request: Request):
    """Eventos filtrables por registro, usuario, campo y fecha; el líder ve solo los de sus registros."""
    exigir_rol(request, Rol.OPERACIONES, Rol.LIDER)
    almacen = request.app.state.almacen
    usuario = request.state.usuario
    q = request.query_params
    codigo = (q.get("codigo") or "").strip().upper()
    campo = (q.get("campo") or "").strip().lower()
    autor = q.get("usuario") or ""
    desde, hasta = a_fecha(q.get("desde")), a_fecha(q.get("hasta"))
    codigos = {r.id: r.codigo for r in almacen.registros.listar()}
    eventos = []
    total_sin_filtros = 0
    for e in reversed(almacen.auditoria.todos()):
        registro = almacen.registros.obtener(e.registro_id)
        if usuario.rol is Rol.LIDER and (registro is None or registro.owner_id != usuario.id):
            continue
        total_sin_filtros += 1
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

    por_pagina = 25
    total_eventos = len(eventos)
    total_paginas = max(1, (total_eventos + por_pagina - 1) // por_pagina)
    pagina = max(1, min(total_paginas, a_entero(q.get("pagina")) or 1))
    inicio = (pagina - 1) * por_pagina
    eventos_paginados = eventos[inicio:inicio + por_pagina]

    from urllib.parse import urlencode

    def query_auditoria(**cambios):
        params = dict(q)
        params.update(cambios)
        return urlencode({k: v for k, v in params.items() if v})

    return render(request, "auditoria.html", {
        "eventos": eventos_paginados, "pagina": pagina, "total_paginas": total_paginas,
        "total": total_eventos, "codigos": codigos, "usuarios": almacen.usuarios.listar(),
        "total_sin_filtros": total_sin_filtros,
        "q": {"codigo": codigo, "campo": campo, "usuario": autor, "desde": q.get("desde") or "", "hasta": q.get("hasta") or ""},
        "query_auditoria": query_auditoria,
    })
