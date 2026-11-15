"""Dashboard ejecutivo (US4) y lectura de filtros compartida con la lista de registros."""

from __future__ import annotations

import json

from datetime import date
from fastapi import APIRouter, Request

from proyecta.application.use_cases.dashboard import Filtros, tablero, visibles
from proyecta.domain.enums import Estado, Flujo, Modalidad, Rol, TipoCatalogo, Tipo
from proyecta.domain.value_objects import Period
from proyecta.interfaces.web.comun import a_uuid, mes, render

router = APIRouter()


def leer_filtros(request: Request) -> Filtros:
    q = request.query_params
    vista = q.get("vista") or "default"
    hoy_periodo = Period.desde_fecha(date.today())

    if vista in ("default", "3m_ant_3m_fut"):
        periodo_def = hoy_periodo.retroceder(3)
        meses_def = 6
    elif vista == "ultimos_3m":
        periodo_def = hoy_periodo.retroceder(3)
        meses_def = 3
    elif vista == "ultimos_6m":
        periodo_def = hoy_periodo.retroceder(6)
        meses_def = 6
    elif vista == "ultimos_12m":
        periodo_def = hoy_periodo.retroceder(12)
        meses_def = 12
    elif vista == "futuro_3m":
        periodo_def = hoy_periodo
        meses_def = 3
    elif vista == "futuro_6m":
        periodo_def = hoy_periodo
        meses_def = 6
    else:  # personalizada
        periodo_def = hoy_periodo.retroceder(3)
        meses_def = 6

    try:
        periodo = Period.desde_texto(q["desde"]) if q.get("desde") else periodo_def
    except Exception:
        periodo = periodo_def
    meses_val = q.get("meses")
    meses = int(meses_val) if meses_val in ("3", "6", "12") else meses_def

    f = Filtros(
        texto=(q.get("q") or "").strip()[:100], sector_id=a_uuid(q.get("sector")), cliente_id=a_uuid(q.get("cliente")),
        manager_id=a_uuid(q.get("manager")), owner_id=a_uuid(q.get("owner")),
        tipo=q.get("tipo") if q.get("tipo") in Tipo.__members__ else "",
        estado=q.get("estado") if q.get("estado") in Estado.__members__ else "",
        flujo=q.get("flujo") if q.get("flujo") in Flujo.__members__ else "",
        modalidad=q.get("modalidad") if q.get("modalidad") in Modalidad.__members__ else "",
        solo_activos=q.get("activos") == "1", confirmado=q.get("confirmado") == "1",
        periodo=periodo, meses=meses, vista=vista,
    )
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
    almacen = request.app.state.almacen
    usuario = request.state.usuario
    calculo = request.app.state.calculo
    datos = tablero(almacen, calculo, usuario, f)

    hoy = Period.desde_fecha(date.today())
    # Serie completa de 18 meses para cambio dinámico de vistas en el cliente
    inicio_18m = hoy.retroceder(12)
    registros_visibles = visibles(almacen, usuario, f)
    calc_18m = calculo.ejecutar(periodo=inicio_18m, meses=18, registros=registros_visibles)

    if usuario.rol is Rol.LIDER:
        lids = [usuario.id]
    elif usuario.rol is Rol.EJECUTIVO and usuario.lider_id:
        lids = [usuario.lider_id]
    elif f.owner_id:
        lids = [f.owner_id]
    else:
        lids = [u.id for u in almacen.usuarios.listar() if u.rol is Rol.LIDER]

    serie_completa = []
    for m in calc_18m.meses:
        meta_m = sum(almacen.metas.vigente(u, m.mes.inicio).monto_clp if almacen.metas.vigente(u, m.mes.inicio) else 0 for u in lids)
        serie_completa.append({
            "periodo": str(m.mes),
            "etiqueta": mes(m.mes),
            "backlog": m.backlog_clp,
            "mab": m.mab_clp,
            "forecast": m.forecast_clp,
            "meta": meta_m,
            "hc": m.hc,
        })

    grafico = json.dumps({
        "meses": [mes(m.mes) for m in datos["meses"]],
        "backlog": [m.backlog_clp for m in datos["meses"]],
        "mab": [m.mab_clp for m in datos["meses"]],
        "meta": [datos["meta_mes"][m.mes] for m in datos["meses"]],
        "hc": [m.hc for m in datos["meses"]],
    })
    serie_completa_json = json.dumps({
        "hoy": str(hoy),
        "meses": serie_completa,
    })
    return render(request, "dashboard.html", {
        **datos,
        **opciones_filtro(request),
        "grafico": grafico,
        "serie_completa_json": serie_completa_json,
        "vista_grafico": f.vista,
    })
