"""Dashboard ejecutivo (US4) y lectura de filtros compartida con la lista de registros."""

from __future__ import annotations

import json

from fastapi import APIRouter, Request

from proyecta.application.use_cases.dashboard import Filtros, tablero
from proyecta.domain.enums import Estado, Flujo, Modalidad, TipoCatalogo, Tipo
from proyecta.domain.value_objects import Period
from proyecta.interfaces.web.comun import a_uuid, mes, render

router = APIRouter()


def leer_filtros(request: Request) -> Filtros:
    q = request.query_params
    try:
        periodo = Period.desde_texto(q["desde"]) if q.get("desde") else None
    except Exception:  # periodo mal escrito: se usa el mes en curso
        periodo = None
    meses = q.get("meses")
    f = Filtros(
        texto=(q.get("q") or "").strip()[:100], sector_id=a_uuid(q.get("sector")), cliente_id=a_uuid(q.get("cliente")),
        manager_id=a_uuid(q.get("manager")), owner_id=a_uuid(q.get("owner")),
        tipo=q.get("tipo") if q.get("tipo") in Tipo.__members__ else "",
        estado=q.get("estado") if q.get("estado") in Estado.__members__ else "",
        flujo=q.get("flujo") if q.get("flujo") in Flujo.__members__ else "",
        modalidad=q.get("modalidad") if q.get("modalidad") in Modalidad.__members__ else "",
        solo_activos=q.get("activos") == "1", confirmado=q.get("confirmado") == "1",
        meses=int(meses) if meses in ("3", "6", "12") else 12,
    )
    if periodo:
        f.periodo = periodo
    return f


def opciones_filtro(request: Request) -> dict:
    almacen = request.app.state.almacen
    return {
        "sectores": almacen.opciones(TipoCatalogo.SECTOR), "clientes": almacen.opciones(TipoCatalogo.CLIENTE),
        "managers": almacen.opciones(TipoCatalogo.MANAGER),
        "owners": [u for u in almacen.usuarios.listar() if u.rol.value == "LIDER"],
        "tipos": list(Tipo), "estados": list(Estado), "flujos": list(Flujo), "modalidades": list(Modalidad),
    }


@router.get("/")
def inicio(request: Request):
    f = leer_filtros(request)
    datos = tablero(request.app.state.almacen, request.app.state.calculo, request.state.usuario, f)
    grafico = json.dumps({
        "meses": [mes(m.mes) for m in datos["meses"]],
        "backlog": [m.backlog_clp for m in datos["meses"]],
        "mab": [m.mab_clp for m in datos["meses"]],
        "meta": [datos["meta_mes"][m.mes] for m in datos["meses"]],
        "hc": [m.hc for m in datos["meses"]],
    })
    return render(request, "dashboard.html", {**datos, **opciones_filtro(request), "grafico": grafico})
