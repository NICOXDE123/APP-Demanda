"""Regresiones de datos, navegación y formularios del rediseño de la Entrega 3."""

from html.parser import HTMLParser
import json

from proyecta.infrastructure.memoria import Almacen
from proyecta.main import crear_app
from tests.integration.test_app import entrar


class Elementos(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.elementos = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        self.elementos.append((tag, dict(attrs)))

    def con(self, atributo):
        return [attrs for _, attrs in self.elementos if atributo in attrs]


def cliente_demo(email="operaciones@example.test"):
    almacen = Almacen.con_semilla()
    app = crear_app(almacen)
    cliente, _ = entrar(app, email)
    return cliente, almacen


def test_grafico_identifica_periodos_sin_depender_del_idioma_y_conserva_cambio_de_anio():
    cliente, _ = cliente_demo()
    respuesta = cliente.get("/?vista=personalizada&desde=2026-12&meses=3")
    datos = json.loads(respuesta.context["grafico"])
    serie = json.loads(respuesta.context["serie_completa_json"])
    assert datos["periodos"] == ["2026-12", "2027-01", "2027-02"]
    assert datos["hoy"] == serie["hoy"]
    assert "Meses anteriores" in respuesta.text
    assert "Mes actual" in respuesta.text
    assert "Meses posteriores" in respuesta.text


def test_dashboard_conserva_serie_y_agrega_dotacion_y_composicion_sin_doble_conteo():
    cliente, _ = cliente_demo()
    respuesta = cliente.get("/")
    assert respuesta.status_code == 200
    elementos = Elementos(respuesta.text)
    ids = {a["id"] for a in elementos.con("id")}
    assert {"grafico", "grafico-hc", "datos-grafico", "datos-serie-completa",
            "tabla-serie-mensual", "cuerpo-serie-mensual", "pie-serie-mensual",
            "tab-financiero", "tab-operativo", "lideres", "sectores"} <= ids
    assert len(elementos.con("data-serie")) == 3
    assert "Backlog confirmado · incluido en la MAB" in respuesta.text
    assert respuesta.text.index('id="alertas-operativas"') < respuesta.text.index('id="lideres"')


def test_dashboard_sin_registros_no_divide_por_cero_y_conserva_filtros():
    cliente, _ = cliente_demo()
    respuesta = cliente.get("/?q=ningun-registro-para-esta-busqueda")
    assert respuesta.status_code == 200
    assert "No hay registros con estos filtros" in respuesta.text
    assert "Sin ingresos en el período" in respuesta.text
    elementos = Elementos(respuesta.text)
    assert {"sector", "cliente", "manager", "owner", "tipo", "estado", "flujo",
            "modalidad", "q", "activos"} <= {a["name"] for a in elementos.con("name")}


def test_cobertura_visual_se_acota_sin_ocultar_el_sobrecumplimiento():
    cliente, almacen = cliente_demo()
    for meta in almacen.metas.datos:
        meta.monto_clp = 1
    respuesta = cliente.get("/")
    assert respuesta.status_code == 200
    barras = Elementos(respuesta.text).con("data-cobertura")
    assert barras
    assert all(0 <= float(b["aria-valuenow"]) <= 100 for b in barras)
    assert any(float(b["data-cobertura"]) > 100 for b in barras)


def test_auditoria_paneles_accesibles_conservan_datos_y_paginacion_filtrada():
    cliente, _ = cliente_demo()
    respuesta = cliente.get("/auditoria?campo=creacion&pagina=2")
    assert respuesta.status_code == 200
    elementos = Elementos(respuesta.text)
    botones = elementos.con("data-audit-select")
    paneles = elementos.con("data-audit-panel")
    assert botones and len(botones) == len(paneles)
    assert {b["aria-controls"] for b in botones} == {p["id"] for p in paneles}
    assert sum("hidden" not in p for p in paneles) == 1
    assert {"codigo", "campo", "usuario", "desde", "hasta"} <= {
        a["name"] for a in elementos.con("name")}
    assert "campo=creacion" in respuesta.text and "pagina=1" in respuesta.text
    for etiqueta in ("Valor anterior", "Valor nuevo", "Fecha efectiva", "Motivo", "MAB", "Forecast"):
        assert etiqueta in respuesta.text


def test_parametros_preserva_posts_csrf_y_campos_de_fecha_del_backend():
    cliente, _ = cliente_demo()
    respuesta = cliente.get("/parametros")
    assert respuesta.status_code == 200
    elementos = Elementos(respuesta.text)
    acciones = {a["action"] for a in elementos.con("action") if a.get("method") == "post"}
    assert {"/parametros/horas", "/parametros/confiabilidad-inicial", "/parametros/metas"} <= acciones
    assert len([a for a in elementos.con("name") if a["name"] == "csrf_token"]) == 4
    assert len([a for a in elementos.con("name") if a["name"] == "desde" and a.get("type") == "date"]) == 3
    assert len(elementos.con("data-historial-target")) == 2
    assert "Historia de horas mensuales" in respuesta.text
    assert "Historia de confiabilidad inicial" in respuesta.text
    assert "Metas comerciales vigentes e históricas" in respuesta.text


def test_lider_conserva_meta_propia_y_no_recibe_formularios_exclusivos_de_operaciones():
    cliente, _ = cliente_demo("lider1@example.test")
    respuesta = cliente.get("/parametros")
    elementos = Elementos(respuesta.text)
    acciones = {a["action"] for a in elementos.con("action")}
    assert "/parametros/metas" in acciones
    assert "/parametros/horas" not in acciones
    assert "/parametros/confiabilidad-inicial" not in acciones
