"""MVP de la Entrega 2 por HTTP: sesión, roles, alta, cálculo, estados, auditoría y parámetros.

Usa la app real con el almacén en memoria y la semilla sintética (sin Datastore).
"""

import re
from datetime import date, timedelta
from uuid import UUID

import pytest
from fastapi.testclient import TestClient

from proyecta.domain.enums import Estado, Tipo, TipoCatalogo
from proyecta.main import crear_app

CLAVE = "proyecta-demo"
SIGUIENTE = (date.today().replace(day=1) + timedelta(days=32)).replace(day=1)


@pytest.fixture
def app():
    return crear_app()


def entrar(app, email: str) -> tuple[TestClient, str]:
    cliente = TestClient(app)
    assert cliente.post("/login", data={"email": email, "password": CLAVE}, follow_redirects=False).status_code == 303
    csrf = re.search(r'data-csrf="([^"]+)"', cliente.get("/").text).group(1)
    return cliente, csrf


def alta(app, cliente, csrf, **extra) -> UUID:
    alm = app.state.almacen
    primero = {t: alm.opciones(t)[0].id for t in (TipoCatalogo.CLIENTE, TipoCatalogo.SECTOR, TipoCatalogo.MANAGER)}
    datos = {"csrf_token": csrf, "tipo": "OPORTUNIDAD", "servicio_proyecto": "Mesa QA sintética",
             "cliente_id": primero[TipoCatalogo.CLIENTE], "sector_id": primero[TipoCatalogo.SECTOR],
             "manager_id": primero[TipoCatalogo.MANAGER], "p1_hc": "3", "p1_ded": "100", "p1_tarifa": "2.600",
             "p1_ingreso": SIGUIENTE.isoformat(), **extra}
    r = cliente.post("/registros", data=datos, follow_redirects=False)
    assert r.status_code == 303, r.text
    return UUID(r.headers["location"].split("/")[2].split("?")[0])


def accion(app, cliente, csrf, rid, ruta, **datos):
    version = app.state.almacen.registros.obtener(rid).version
    return cliente.post(f"/registros/{rid}/{ruta}", data={"csrf_token": csrf, "version": version, **datos},
                        follow_redirects=False)


def test_sin_sesion_redirige_al_login_y_la_api_responde_401(app):
    cliente = TestClient(app)
    assert cliente.get("/", follow_redirects=False).headers["location"] == "/login"
    assert cliente.get("/api/v1/forecast").status_code == 401
    assert cliente.get("/health").json() == {"status": "ok"}


def test_bloqueo_tras_cinco_intentos_y_cookie_segura(app):
    cliente = TestClient(app)
    for _ in range(5):
        assert cliente.post("/login", data={"email": "lider1@example.test", "password": "mala"}).status_code == 401
    r = cliente.post("/login", data={"email": "lider1@example.test", "password": CLAVE})
    assert r.status_code == 401 and "Demasiados intentos" in r.text  # bloqueo por IP y por cuenta
    cookie = TestClient(crear_app()).post("/login", data={"email": "lider2@example.test", "password": CLAVE},
                                  follow_redirects=False).headers["set-cookie"]
    assert "HttpOnly" in cookie and "SameSite=strict" in cookie


def test_post_sin_csrf_se_rechaza(app):
    cliente, _ = entrar(app, "operaciones@example.test")
    assert cliente.post("/registros", data={"servicio_proyecto": "x"}).status_code == 403


def test_alta_calcula_como_la_spec_y_audita_la_creacion(app):
    """US1 esc. 1 y US3 esc. 1–2: 3 HC × $2.600 × 180 h = $1.404.000; con P 50 % y C 90 %, MAB $631.800."""
    cliente, csrf = entrar(app, "lider1@example.test")
    previa = cliente.post("/registros/vista-previa", data={"csrf_token": csrf, "p1_hc": "3", "p1_tarifa": "2.600",
                                                            "p1_ingreso": SIGUIENTE.isoformat(), "tipo": "OPORTUNIDAD"})
    assert "Base $1.404.000" in previa.text and "no se ha guardado" in previa.text
    antes = len(app.state.almacen.registros.datos)
    rid = alta(app, cliente, csrf)
    alm = app.state.almacen
    r = alm.registros.obtener(rid)
    assert len(alm.registros.datos) == antes + 1
    assert (r.estado, r.flujo.orden, r.probabilidad_bp, r.confiabilidad_bp) == (Estado.PENDIENTE, 1, 1_000, 9_000)
    assert re.fullmatch(r"OPD-\d{4}", r.codigo)
    assert accion(app, cliente, csrf, rid, "probabilidad", valor_bp="5000", desde=SIGUIENTE.isoformat(),
                  motivo="Propuesta solicitada").status_code == 303
    mes = next(d for d in app.state.calculo.calcular_registro(rid).meses if d.mes.inicio == SIGUIENTE)
    assert (mes.base_clp, mes.mab_clp) == (1_404_000, 631_800)
    creacion = alm.auditoria.listar_por_registro(rid)[-1]
    assert creacion.campo == "creacion" and creacion.forecast_despues > 0


def test_alta_invalida_no_guarda_nada(app):
    cliente, csrf = entrar(app, "lider1@example.test")
    antes = len(app.state.almacen.registros.datos)
    r = cliente.post("/registros", data={"csrf_token": csrf, "tipo": "OPORTUNIDAD", "servicio_proyecto": "",
                                         "p1_hc": "0", "p1_tarifa": "100", "p1_ingreso": SIGUIENTE.isoformat()})
    assert r.status_code == 422 and "No se guardó" in r.text
    assert 'id="alta-dialog"' in r.text and "data-dialog-open-on-load" in r.text
    assert len(app.state.almacen.registros.datos) == antes


def test_alta_se_abre_como_modal_desde_registros(app):
    cliente, _ = entrar(app, "lider1@example.test")
    pagina = cliente.get("/registros?activos=1").text

    assert 'aria-controls="alta-dialog" data-dialog-open' in pagina
    assert '<dialog id="alta-dialog"' in pagina
    assert 'href="/registros/nuevo"' not in pagina
    assert cliente.get("/registros/nuevo", follow_redirects=False).headers["location"] == \
        "/registros?activos=1&nuevo=1"
    assert "data-dialog-open-on-load" in cliente.get("/registros?nuevo=1").text


def test_ciclo_de_vida_con_auditoria_por_campo_e_impacto(app):
    cliente, csrf = entrar(app, "lider1@example.test")
    rid = alta(app, cliente, csrf)
    alm = app.state.almacen
    salto = accion(app, cliente, csrf, rid, "estado", destino="EN_CURSO", motivo="x")
    assert salto.status_code == 409 and "adjudicarse" in salto.text
    assert accion(app, cliente, csrf, rid, "estado", destino="ADJUDICADA", motivo="Ganada",
                  fecha=SIGUIENTE.isoformat()).status_code == 303
    r = alm.registros.obtener(rid)
    assert (r.tipo, r.probabilidad_bp) == (Tipo.DEMANDA, 10_000)
    eventos = {e.campo: e for e in alm.auditoria.listar_por_registro(rid)}
    assert {"estado", "tipo", "probabilidad_bp"} <= eventos.keys()
    assert eventos["probabilidad_bp"].motivo == "Ganada"
    assert eventos["probabilidad_bp"].forecast_despues > eventos["probabilidad_bp"].forecast_antes
    assert accion(app, cliente, csrf, rid, "bitacora", contenido="Kickoff con el cliente").status_code == 303
    assert any("Kickoff" in b.contenido for b in alm.bitacora.listar_por_registro(rid))


def test_confiabilidad_solo_operaciones_y_sin_reescribir_meses_anteriores(app):
    lider, csrf_l = entrar(app, "lider1@example.test")
    rid = alta(app, lider, csrf_l)
    assert accion(app, lider, csrf_l, rid, "confiabilidad", valor="50", motivo="x").status_code == 403
    ops, csrf_o = entrar(app, "operaciones@example.test")
    desde = (SIGUIENTE + timedelta(days=62)).replace(day=1)
    assert accion(app, ops, csrf_o, rid, "confiabilidad", valor="50", desde=desde.isoformat(),
                  motivo="Riesgo del cliente").status_code == 303
    meses = {d.mes.inicio: d.confiabilidad_bp for d in app.state.calculo.calcular_registro(rid).meses}
    assert meses[SIGUIENTE] == 9_000 and meses[desde] == 5_000


def test_conflicto_de_version_informa_y_no_pisa(app):
    cliente, csrf = entrar(app, "lider1@example.test")
    rid = alta(app, cliente, csrf)
    r = cliente.post(f"/registros/{rid}/editar", data={"csrf_token": csrf, "version": "0",
                                                        "servicio_proyecto": "Pisado"})
    assert r.status_code == 409 and "Otra persona guardó" in r.text
    assert app.state.almacen.registros.obtener(rid).servicio_proyecto == "Mesa QA sintética"


def test_permisos_de_lider_y_ejecutivo(app):
    lider1, csrf1 = entrar(app, "lider1@example.test")
    rid = alta(app, lider1, csrf1)
    lider2, csrf2 = entrar(app, "lider2@example.test")
    assert lider2.get(f"/registros/{rid}").status_code == 403
    assert accion(app, lider2, csrf2, rid, "bitacora", contenido="x").status_code == 403
    ejecutivo, csrf_e = entrar(app, "ejecutivo@example.test")
    assert ejecutivo.get(f"/registros/{rid}").status_code == 200
    assert ejecutivo.get("/registros/nuevo").status_code == 403
    assert accion(app, ejecutivo, csrf_e, rid, "editar", servicio_proyecto="x").status_code == 403
    # La API de forecast del líder solo suma lo suyo.
    total_lider = lider2.get("/api/v1/forecast").json()["totales"]["forecast_clp"]
    total_ejecutivo = ejecutivo.get("/api/v1/forecast").json()["totales"]["forecast_clp"]
    assert 0 <= total_lider < total_ejecutivo


def test_auditoria_es_solo_lectura(app):
    cliente, csrf = entrar(app, "operaciones@example.test")
    rid = alta(app, cliente, csrf)
    assert cliente.get(f"/api/v1/registros/{rid}/auditoria").status_code == 200
    assert cliente.put(f"/api/v1/registros/{rid}/auditoria").status_code == 405
    assert cliente.delete(f"/api/v1/registros/{rid}/auditoria").status_code == 405


def test_horas_con_vigencia_no_reescriben_meses_anteriores(app):
    ops, csrf = entrar(app, "operaciones@example.test")
    serie_antes = app.state.calculo.ejecutar().meses
    desde = serie_antes[3].mes.inicio
    r = ops.post("/parametros/horas", data={"csrf_token": csrf, "horas": "160", "desde": desde.isoformat(),
                                             "motivo": "Calendario"}, follow_redirects=False)
    assert r.status_code == 303
    serie = app.state.calculo.ejecutar().meses
    assert serie[2].base_clp == serie_antes[2].base_clp
    assert serie[3].base_clp < serie_antes[3].base_clp
    assert app.state.almacen.auditoria.todos()[0].campo == "horas_mensuales"
    lider, csrf_l = entrar(app, "lider1@example.test")
    assert lider.post("/parametros/horas", data={"csrf_token": csrf_l, "horas": "1", "desde": desde.isoformat(),
                                                  "motivo": "x"}).status_code == 403


def test_confiabilidad_inicial_editable_vigente_y_auditada(app):
    ops, csrf = entrar(app, "operaciones@example.test")
    anterior = alta(app, ops, csrf)
    inicio_mes = date.today().replace(day=1)

    r = ops.post("/parametros/confiabilidad-inicial", data={
        "csrf_token": csrf, "valor": "40", "desde": inicio_mes.isoformat(), "motivo": "Ajuste de política",
    }, follow_redirects=False)

    assert r.status_code == 303
    assert app.state.almacen.registros.obtener(anterior).confiabilidad_bp == 9_000
    nuevo = alta(app, ops, csrf)
    assert app.state.almacen.registros.obtener(nuevo).confiabilidad_bp == 4_000
    demanda = alta(app, ops, csrf, tipo="DEMANDA", flujo="PROPUESTA_ENTREGADA", motivo="Adjudicación")
    assert app.state.almacen.registros.obtener(demanda).confiabilidad_bp == 4_000

    evento = next(e for e in app.state.almacen.auditoria.todos() if e.campo == "confiabilidad_inicial")
    assert (evento.valor_anterior, evento.valor_nuevo, evento.motivo, evento.fecha_efectiva) == (
        90, 40, "Ajuste de política", inicio_mes,
    )
    assert evento.mab_antes == evento.mab_despues
    assert evento.forecast_antes == evento.forecast_despues

    parametros = ops.get("/parametros").text
    assert "Historia de confiabilidad inicial" in parametros
    assert "40 %" in parametros and "90 %" in parametros
    auditoria = ops.get("/auditoria?campo=confiabilidad_inicial").text
    assert "Ajuste de política" in auditoria and "90 %" in auditoria and "40 %" in auditoria

    lider, csrf_lider = entrar(app, "lider1@example.test")
    assert lider.post("/parametros/confiabilidad-inicial", data={
        "csrf_token": csrf_lider, "valor": "50", "desde": inicio_mes.isoformat(), "motivo": "x",
    }).status_code == 403


def test_dashboard_filtra_y_los_totales_son_la_suma_de_lo_visible(app):
    ops, _ = entrar(app, "operaciones@example.test")
    assert ops.get("/").status_code == 200
    total = ops.get("/api/v1/forecast").json()["totales"]["forecast_clp"]
    sectores = app.state.almacen.opciones(TipoCatalogo.SECTOR)
    suma = 0
    from proyecta.application.use_cases.dashboard import Filtros, tablero

    usuario = app.state.almacen.usuarios.por_email("operaciones@example.test")
    for s in sectores:
        suma += tablero(app.state.almacen, app.state.calculo, usuario, Filtros(sector_id=s.id))["kpi"]["forecast"]
        assert ops.get(f"/registros?sector={s.id}").status_code == 200
    assert suma == total


def test_navegacion_identifica_seccion_y_conserva_retorno_local(app):
    from urllib.parse import quote, parse_qs, urlsplit

    cliente, csrf = entrar(app, "lider1@example.test")
    rid = alta(app, cliente, csrf)
    lista = "/registros?q=Mesa&meses=3&desde=2027-01"
    pagina = cliente.get(lista).text
    assert 'aria-current="page"' in pagina
    assert "volver=" in pagina
    ficha = cliente.get(f"/registros/{rid}?volver={quote(lista, safe='')}").text
    assert 'aria-current="location"' in ficha
    assert 'href="/registros?q=Mesa&amp;meses=3&amp;desde=2027-01"' in ficha
    for destino in ("https://example.test", "//example.test", "https://[", "/registros/otro", "/registros?x=\nmal"):
        pagina = cliente.get(f"/registros/{rid}", params={"volver": destino}).text
        assert 'href="/registros?activos=1"' in pagina
    guardado = accion(app, cliente, csrf, rid, "bitacora", contenido="Seguimiento sintético", volver=lista)
    assert parse_qs(urlsplit(guardado.headers["location"]).query)["volver"] == [lista]


def test_error_web_es_html_y_validacion_api_sigue_json(app):
    cliente, _ = entrar(app, "operaciones@example.test")
    invalida = cliente.get("/registros/no-es-uuid")
    assert invalida.status_code == 422
    assert "text/html" in invalida.headers["content-type"]
    assert "El enlace del registro no es válido" in invalida.text
    assert "No encontramos la página solicitada" in cliente.get("/no-existe").text
    api = cliente.get("/api/v1/registros/no-es-uuid/auditoria")
    assert api.status_code == 422 and "detail" in api.json()


def test_alta_error_identifica_hc_y_conserva_campos(app):
    cliente, csrf = entrar(app, "lider1@example.test")
    respuesta = cliente.post("/registros", data={
        "csrf_token": csrf, "tipo": "OPORTUNIDAD", "servicio_proyecto": "Borrador sintético",
        "p1_hc": "", "p1_tarifa": "2.600", "p1_ingreso": SIGUIENTE.isoformat(),
    })
    assert respuesta.status_code == 422
    assert 'href="#p1_hc"' in respuesta.text
    assert 'id="p1_hc"' in respuesta.text and 'aria-invalid="true"' in respuesta.text
    assert "Completa HC con un número entero" in respuesta.text
    assert 'value="Borrador sintético"' in respuesta.text


def test_error_tarifa_conserva_borrador_solo_en_formulario_afectado(app):
    cliente, csrf = entrar(app, "lider1@example.test")
    rid = alta(app, cliente, csrf)
    perfil = app.state.almacen.perfiles.listar_por_registro(rid)[0]
    respuesta = accion(app, cliente, csrf, rid, f"perfiles/{perfil.id}/tarifa",
                       tarifa="mala", desde=SIGUIENTE.isoformat(), motivo="Borrador de tarifa")
    assert respuesta.status_code == 422
    assert 'name="tarifa"' in respuesta.text and 'value="mala"' in respuesta.text
    assert respuesta.text.count('value="Borrador de tarifa"') == 1
    assert 'data-error-summary' in respuesta.text


def test_conflicto_conserva_version_del_borrador_hasta_revision(app):
    cliente, csrf = entrar(app, "lider1@example.test")
    rid = alta(app, cliente, csrf)
    app.state.almacen.registros.obtener(rid).studio = True
    respuesta = cliente.post(f"/registros/{rid}/editar", data={
        "csrf_token": csrf, "version": "0", "servicio_proyecto": "Mi borrador",
        "observaciones": "Texto pendiente", "cuenta": "Cuenta borrador",
    })
    assert respuesta.status_code == 409
    assert 'value="Cuenta borrador"' in respuesta.text and "Texto pendiente" in respuesta.text
    assert 'name="version" value="0"' in respuesta.text
    assert "checked" not in re.search(r'<input[^>]*name="studio"[^>]*>', respuesta.text).group(0)
    assert "Revisar versión vigente" in respuesta.text


def test_error_parametro_conserva_valores_y_no_modifica_historia(app):
    cliente, csrf = entrar(app, "operaciones@example.test")
    antes = len(app.state.almacen.parametros.listar("horas_mensuales"))
    respuesta = cliente.post("/parametros/horas", data={
        "csrf_token": csrf, "horas": "0", "desde": SIGUIENTE.isoformat(), "motivo": "Ajuste pendiente",
    })
    assert respuesta.status_code == 422
    assert 'value="0"' in respuesta.text
    assert respuesta.text.count('value="Ajuste pendiente"') == 1
    assert len(app.state.almacen.parametros.listar("horas_mensuales")) == antes


def test_vacios_dashboard_y_auditoria_explican_recuperacion(app):
    cliente, _ = entrar(app, "operaciones@example.test")
    vacio = cliente.get("/?q=sin-coincidencias-auditoria").text
    assert "No hay registros con estos filtros" in vacio
    assert "Las metas" in vacio and "Limpiar filtros" in vacio
    assert "Todavía no hay eventos registrados" in cliente.get("/auditoria").text
    assert 'href="/auditoria"' in cliente.get("/auditoria?codigo=OPD-0000").text
