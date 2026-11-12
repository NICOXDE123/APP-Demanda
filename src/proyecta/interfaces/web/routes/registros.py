"""Registros: lista, alta, ficha, edición, perfiles, tarifas, estados, P/C y bitácora (US1, US2, US3, US8).

Solo traducen HTTP a `ServicioRegistros` y renderizan; no tienen fórmulas (Principio II).
Un error de negocio vuelve a mostrar la ficha con el mensaje y el código HTTP que sugiere el dominio
(409 conflicto, 403 permiso, 422 validación), conservando lo escrito.
"""

from __future__ import annotations

from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse

from proyecta.application.use_cases.dashboard import tablero
from proyecta.domain import states
from proyecta.domain.entities import EntradaCalculo, Perfil, Registro, TarifaPerfil
from proyecta.domain.enums import (
    PROBABILIDADES_VALIDAS_BP,
    Estado,
    Flujo,
    FLUJOS_POR_TIPO,
    Modalidad,
    MotivoCierre,
    Rol,
    Tipo,
    TipoCatalogo,
    TipoEventoBitacora,
)
from proyecta.domain.errors import ErrorDominio
from proyecta.domain.value_objects import Period
from proyecta.interfaces.web.comun import (
    a_bp,
    a_centavos,
    a_entero,
    a_fecha,
    a_uuid,
    exigir_csrf,
    render,
    texto,
)
from proyecta.interfaces.web.routes.dashboard import leer_filtros, opciones_filtro

router = APIRouter(dependencies=[Depends(exigir_csrf)])
MAX_PERFILES_ALTA = 4


def _servicio(request: Request):
    return request.app.state.registros


def _catalogos(request: Request) -> dict:
    almacen = request.app.state.almacen
    return {
        "sectores": almacen.opciones(TipoCatalogo.SECTOR), "clientes": almacen.opciones(TipoCatalogo.CLIENTE),
        "managers": almacen.opciones(TipoCatalogo.MANAGER), "nombres_perfil": almacen.opciones(TipoCatalogo.PERFIL),
        "lideres": [u for u in almacen.usuarios.listar() if u.rol is Rol.LIDER],
        "modalidades": list(Modalidad), "flujos": list(Flujo),
    }


# -- Lista y alta -------------------------------------------------------------

@router.get("/registros")
def lista(request: Request):
    f = leer_filtros(request)
    datos = tablero(request.app.state.almacen, request.app.state.calculo, request.state.usuario, f)
    return render(request, "registros/lista.html", {**datos, **opciones_filtro(request)})


def _leer_perfiles(form) -> tuple[list[dict], list[str]]:
    perfiles, errores = [], []
    for i in range(1, MAX_PERFILES_ALTA + 1):
        hc, tarifa, ingreso = (form.get(f"p{i}_{k}") for k in ("hc", "tarifa", "ingreso"))
        if not (hc or tarifa or ingreso):
            continue  # fila vacía: una oportunidad puede nacer sin perfiles (RN-40)
        datos = {"nombre_perfil_id": a_uuid(form.get(f"p{i}_nombre")), "hc": a_entero(hc),
                 "dedicacion_pct": a_entero(form.get(f"p{i}_ded")) or 100, "tarifa_hora_centavos": a_centavos(tarifa),
                 "fecha_ingreso": a_fecha(ingreso), "fecha_fin": a_fecha(form.get(f"p{i}_fin"))}
        if datos["hc"] is None or datos["tarifa_hora_centavos"] is None or datos["fecha_ingreso"] is None:
            errores.append(f"Perfil {i}: completa HC y tarifa con números y el ingreso con una fecha válida.")
            continue
        perfiles.append(datos)
    return perfiles, errores


def _leer_registro(form) -> dict:
    return {
        "tipo": form.get("tipo") if form.get("tipo") in Tipo.__members__ else "OPORTUNIDAD",
        "servicio_proyecto": texto(form, "servicio_proyecto"), "cliente_id": a_uuid(form.get("cliente_id")),
        "sector_id": a_uuid(form.get("sector_id")), "manager_id": a_uuid(form.get("manager_id")),
        "owner_id": a_uuid(form.get("owner_id")), "observaciones": texto(form, "observaciones"),
        "fecha_ingreso": a_fecha(form.get("fecha_ingreso")), "fecha_fin_vigencia": a_fecha(form.get("fecha_fin_vigencia")),
        "flujo": form.get("flujo") if form.get("flujo") in Flujo.__members__ else None,
        "fecha_adjudicacion": a_fecha(form.get("fecha_adjudicacion")), "motivo": texto(form, "motivo"),
    }


def _leer_contrato(form) -> dict | None:
    if form.get("tipo") != "CONTINUIDAD":
        return None
    monto = a_centavos(form.get("c_monto"))
    return {"codigo_contrato": texto(form, "c_codigo"), "fecha_inicio": a_fecha(form.get("c_inicio")),
            "fecha_fin": a_fecha(form.get("c_fin")), "monto_mensual_clp": round(monto / 100) if monto else None,
            "hc_comprometido": a_entero(form.get("c_hc")) or 0}


def _form_alta(request: Request, form=None, errores=(), status_code=200):
    siguiente = Period.desde_fecha(date.today()).siguiente().inicio
    form = form or {"tipo": "OPORTUNIDAD", "p1_hc": "3", "p1_ded": "100", "p1_tarifa": "25.000",
                    "p1_ingreso": siguiente.isoformat()}
    return render(request, "registros/nuevo.html", {**_catalogos(request), "form": form, "errores": errores,
                                                     "max_perfiles": MAX_PERFILES_ALTA}, status_code=status_code)


@router.get("/registros/nuevo")
def nuevo(request: Request):
    if request.state.usuario.rol is Rol.EJECUTIVO:
        raise HTTPException(403, "El rol Ejecutivo solo consulta.")
    return _form_alta(request)


@router.post("/registros/vista-previa")
async def vista_previa(request: Request):
    """Fragmento HTMX con Base, MAB, Backlog y Forecast antes de guardar; no persiste nada (FR-009)."""
    form = await request.form()
    perfiles, errores = _leer_perfiles(form)
    if errores:
        return render(request, "registros/_vista_previa.html", {"errores": errores})
    tipo = Tipo(form.get("tipo")) if form.get("tipo") in Tipo.__members__ else Tipo.OPORTUNIDAD
    estado = {Tipo.OPORTUNIDAD: Estado.PENDIENTE, Tipo.DEMANDA: Estado.ADJUDICADA}.get(tipo, Estado.EN_CURSO)
    borrador = Registro(codigo="", tipo=tipo, estado=estado,
                        probabilidad_bp=1_000 if tipo is Tipo.OPORTUNIDAD else 10_000,
                        confiabilidad_bp=10_000 if tipo is Tipo.CONTINUIDAD else 9_000)
    try:
        nuevos = [(Perfil(registro_id=borrador.id, hc=p["hc"], dedicacion_pct=p["dedicacion_pct"],
                          fecha_ingreso=p["fecha_ingreso"], fecha_fin=p["fecha_fin"]), p) for p in perfiles]
    except ErrorDominio as error:
        return render(request, "registros/_vista_previa.html", {"errores": [error.message]})
    entrada = EntradaCalculo(
        registro=borrador, perfiles=[p for p, _ in nuevos],
        tarifas={p.id: [TarifaPerfil(perfil_id=p.id, tarifa_hora_centavos=d["tarifa_hora_centavos"],
                                     vigente_desde=d["fecha_ingreso"])] for p, d in nuevos})
    if tipo is Tipo.CONTINUIDAD:
        from proyecta.domain.entities import Contrato

        c = _leer_contrato(form) or {}
        entrada.contrato = Contrato(registro_id=borrador.id, fecha_inicio=c.get("fecha_inicio") or date.today(),
                                    fecha_fin=c.get("fecha_fin"), monto_mensual_clp=c.get("monto_mensual_clp"))
    resultado = request.app.state.calculo.previsualizar(entrada)
    activo = next((d for d in resultado.meses if d.base_clp or d.backlog_clp), resultado.meses[0])
    return render(request, "registros/_vista_previa.html", {"errores": [], "mes": activo,
                                                            "forecast_12": resultado.total_forecast()})


@router.post("/registros")
async def crear(request: Request):
    form = await request.form()
    perfiles, errores = _leer_perfiles(form)
    if errores:
        return _form_alta(request, form, errores, status_code=422)
    try:
        registro = _servicio(request).crear(request.state.usuario, _leer_registro(form), perfiles, _leer_contrato(form))
    except ErrorDominio as error:
        mensajes = error.detalle.get("errores") if error.detalle else None
        return _form_alta(request, form, mensajes or [error.message], status_code=error.status_sugerido)
    return RedirectResponse(f"/registros/{registro.id}?ok=creado", status_code=303)


# -- Ficha ------------------------------------------------------------------------

def ficha(request: Request, registro_id: UUID, error: str | None = None, status_code: int = 200, form=None):
    almacen = request.app.state.almacen
    usuario = request.state.usuario
    registro = almacen.registros.obtener(registro_id)
    if registro is None:
        raise HTTPException(404, "Registro no encontrado")
    if usuario.rol is Rol.LIDER and registro.owner_id != usuario.id:
        raise HTTPException(403, "Solo puedes ver tus registros.")
    resultado = request.app.state.calculo.calcular_registro(registro.id)
    perfiles = almacen.perfiles.listar_por_registro(registro.id)
    editable = states.puede_editar(usuario.rol, usuario.id, registro)
    return render(request, "registros/ficha.html", {
        **_catalogos(request), "r": registro, "resultado": resultado, "editable": editable,
        "perfiles": [(p, almacen.perfiles.tarifas_de(p.id)) for p in perfiles],
        "contrato": almacen.contratos.obtener_por_registro(registro.id),
        "bitacora": almacen.bitacora.listar_por_registro(registro.id),
        "eventos": almacen.auditoria.listar_por_registro(registro.id),
        "vigencias": sorted(almacen.vigencias.listar(registro.id), key=lambda v: (v.campo.value, v.vigente_desde)),
        "destinos": states.destinos(registro, usuario.rol) if editable else [],
        "flujos_tipo": [f for f in Flujo if f in FLUJOS_POR_TIPO[registro.tipo]],
        "p_fija": states.probabilidad_fija(registro), "probabilidades": sorted(PROBABILIDADES_VALIDAS_BP - {10_000}),
        "motivos_cierre": list(MotivoCierre), "tipos_bitacora": [t for t in TipoEventoBitacora if t.value != "MIGRACION"],
        "error": error, "ok": request.query_params.get("ok"), "form": form or {}, "hoy": date.today(),
    }, status_code=status_code)


@router.get("/registros/{registro_id}")
def ver(request: Request, registro_id: UUID):
    return ficha(request, registro_id)


async def _accion(request: Request, registro_id: UUID, hacer, ok: str):
    """Ejecuta la acción; si el dominio la rechaza, vuelve a la ficha con el mensaje y lo escrito."""
    form = await request.form()
    try:
        hacer(form, request.state.usuario, a_entero(form.get("version")) or 0)
    except ErrorDominio as error:
        return ficha(request, registro_id, error.message, error.status_sugerido, dict(form))
    return RedirectResponse(f"/registros/{registro_id}?ok={ok}", status_code=303)


@router.post("/registros/{registro_id}/editar")
async def editar(request: Request, registro_id: UUID):
    def hacer(form, usuario, version):
        campos = {
            "servicio_proyecto": texto(form, "servicio_proyecto"), "cliente_id": a_uuid(form.get("cliente_id")),
            "sector_id": a_uuid(form.get("sector_id")), "manager_id": a_uuid(form.get("manager_id")),
            "modalidad": Modalidad(form.get("modalidad")) if form.get("modalidad") in Modalidad.__members__ else None,
            "studio": form.get("studio") == "1", "cuenta": texto(form, "cuenta") or "No Aplica",
            "id_externo": texto(form, "id_externo"), "observaciones": texto(form, "observaciones"),
            "fecha_ingreso": a_fecha(form.get("fecha_ingreso")), "fecha_fin_vigencia": a_fecha(form.get("fecha_fin_vigencia")),
            "en_staffing": form.get("en_staffing") == "1", "en_invoicing": form.get("en_invoicing") == "1",
        }
        obligatorios = ("cliente_id", "sector_id", "manager_id", "modalidad")  # un valor inválido no borra el campo
        campos = {k: v for k, v in campos.items() if not (k in obligatorios and v is None)}
        _servicio(request).editar(usuario, registro_id, version, campos)
    return await _accion(request, registro_id, hacer, "guardado")


@router.post("/registros/{registro_id}/estado")
async def estado(request: Request, registro_id: UUID):
    def hacer(form, usuario, version):
        if form.get("destino") not in Estado.__members__:
            raise _error("Elige el estado de destino.")
        motivo_cierre = MotivoCierre(form["motivo_cierre"]) if form.get("motivo_cierre") in MotivoCierre.__members__ else None
        _servicio(request).transicionar(usuario, registro_id, version, Estado(form["destino"]), texto(form, "motivo"),
                                        a_fecha(form.get("fecha")) or date.today(), motivo_cierre)
    return await _accion(request, registro_id, hacer, "estado")


@router.post("/registros/{registro_id}/flujo")
async def flujo(request: Request, registro_id: UUID):
    def hacer(form, usuario, version):
        if form.get("flujo") not in Flujo.__members__:
            raise _error("Elige el flujo.")
        _servicio(request).cambiar_flujo(usuario, registro_id, version, Flujo(form["flujo"]), texto(form, "motivo"),
                                         a_fecha(form.get("fecha")) or date.today())
    return await _accion(request, registro_id, hacer, "flujo")


@router.post("/registros/{registro_id}/probabilidad")
async def probabilidad(request: Request, registro_id: UUID):
    def hacer(form, usuario, version):
        _servicio(request).cambiar_probabilidad(usuario, registro_id, version, a_entero(form.get("valor_bp")) or -1,
                                                a_fecha(form.get("desde")) or date.today(), texto(form, "motivo"))
    return await _accion(request, registro_id, hacer, "probabilidad")


@router.post("/registros/{registro_id}/confiabilidad")
async def confiabilidad(request: Request, registro_id: UUID):
    def hacer(form, usuario, version):
        valor = a_bp(form.get("valor"))
        _servicio(request).cambiar_confiabilidad(usuario, registro_id, version, -1 if valor is None else valor,
                                                 a_fecha(form.get("desde")) or date.today(), texto(form, "motivo"))
    return await _accion(request, registro_id, hacer, "confiabilidad")


@router.post("/registros/{registro_id}/perfiles")
async def agregar_perfil(request: Request, registro_id: UUID):
    def hacer(form, usuario, version):
        perfiles, errores = _leer_perfiles(form)
        if errores or not perfiles:
            raise _error(errores[0] if errores else "Completa el perfil.")
        _servicio(request).agregar_perfil(usuario, registro_id, version, {**perfiles[0], "motivo": texto(form, "motivo")})
    return await _accion(request, registro_id, hacer, "perfil")


@router.post("/registros/{registro_id}/perfiles/{perfil_id}")
async def editar_perfil(request: Request, registro_id: UUID, perfil_id: UUID):
    def hacer(form, usuario, version):
        datos = {"hc": a_entero(form.get("hc")), "dedicacion_pct": a_entero(form.get("ded")),
                 "fecha_ingreso": a_fecha(form.get("ingreso")), "fecha_fin": a_fecha(form.get("fin"))}
        if None in (datos["hc"], datos["dedicacion_pct"], datos["fecha_ingreso"]):
            raise _error("HC, dedicación e ingreso son obligatorios.")
        _servicio(request).editar_perfil(usuario, registro_id, version, perfil_id, datos, texto(form, "motivo"))
    return await _accion(request, registro_id, hacer, "perfil")


@router.post("/registros/{registro_id}/perfiles/{perfil_id}/quitar")
async def quitar_perfil(request: Request, registro_id: UUID, perfil_id: UUID):
    def hacer(form, usuario, version):
        _servicio(request).quitar_perfil(usuario, registro_id, version, perfil_id, texto(form, "motivo"))
    return await _accion(request, registro_id, hacer, "perfil")


@router.post("/registros/{registro_id}/perfiles/{perfil_id}/tarifa")
async def nueva_tarifa(request: Request, registro_id: UUID, perfil_id: UUID):
    def hacer(form, usuario, version):
        _servicio(request).nueva_tarifa(usuario, registro_id, version, perfil_id, a_centavos(form.get("tarifa")) or 0,
                                        a_fecha(form.get("desde")) or date.today(), texto(form, "motivo"))
    return await _accion(request, registro_id, hacer, "tarifa")


@router.post("/registros/{registro_id}/bitacora")
async def bitacora(request: Request, registro_id: UUID):
    def hacer(form, usuario, _version):
        tipo = TipoEventoBitacora(form["tipo"]) if form.get("tipo") in TipoEventoBitacora.__members__ else TipoEventoBitacora.SEGUIMIENTO
        _servicio(request).agregar_bitacora(usuario, registro_id, tipo, texto(form, "contenido"),
                                            texto(form, "proxima_accion"), a_fecha(form.get("fecha_compromiso")),
                                            a_uuid(form.get("referencia_id")))
    return await _accion(request, registro_id, hacer, "bitacora")


def _error(mensaje: str) -> ErrorDominio:
    from proyecta.domain.errors import ErrorValidacion

    return ErrorValidacion("VALIDACION", mensaje)
