"""Pruebas de tooltips ejecutivos con definición y cálculo en el dashboard (US4)."""

import re
from html.parser import HTMLParser
from proyecta.infrastructure.memoria import Almacen
from proyecta.main import crear_app
from tests.integration.test_app import entrar


class ExtractorAyudas(HTMLParser):
    def __init__(self):
        super().__init__()
        self.kpis = []
        self.botones_ayuda = []
        self.th_ayudas = []
        self.seccion_ayudas = []
        self.inline_ayudas = []

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        clases = d.get("class", "").split()

        if "kpi" in clases:
            self.kpis.append(d)
        if "btn-ayuda-kpi" in clases:
            self.botones_ayuda.append(d)
        if "th-ayuda-btn" in clases:
            self.th_ayudas.append(d)
        if "btn-ayuda-seccion" in clases:
            self.seccion_ayudas.append(d)
        if "btn-ayuda-inline" in clases:
            self.inline_ayudas.append(d)


def test_dashboard_contiene_tooltips_con_definicion_y_calculo():
    almacen = Almacen.con_semilla()
    app = crear_app(almacen)
    cliente, _ = entrar(app, "operaciones@example.test")

    respuesta = cliente.get("/")
    assert respuesta.status_code == 200

    extractor = ExtractorAyudas()
    extractor.feed(respuesta.text)

    # 1. Indicadores (9 KPIs en grilla tras retirar potencial, P media y C media)
    assert len(extractor.kpis) == 9, f"Se esperaban 9 tarjetas KPI, se encontraron {len(extractor.kpis)}"
    assert len(extractor.botones_ayuda) == 9, f"Se esperaban 9 botones de ayuda KPI, encontrados {len(extractor.botones_ayuda)}"

    for kpi in extractor.kpis:
        titulo = kpi.get("data-ayuda-titulo")
        definicion = kpi.get("data-ayuda-def")
        calculo = kpi.get("data-ayuda-calc")

        assert titulo, "La tarjeta KPI debe tener data-ayuda-titulo"
        assert definicion, f"El KPI '{titulo}' debe tener definición (data-ayuda-def)"
        assert calculo, f"El KPI '{titulo}' debe tener fórmula/cálculo (data-ayuda-calc)"
        assert len(definicion) > 20, f"Definición demasiado corta para '{titulo}'"
        assert len(calculo) > 20, f"Cálculo demasiado corto para '{titulo}'"

    # 2. Encabezados de tablas / grillas (Serie mensual, Líder, Sector, Clientes, Estado, Flujo)
    assert len(extractor.th_ayudas) >= 24, f"Se esperaban al menos 24 encabezados de grilla con ayuda, encontrados {len(extractor.th_ayudas)}"
    for th in extractor.th_ayudas:
        titulo = th.get("data-ayuda-titulo")
        definicion = th.get("data-ayuda-def")
        calculo = th.get("data-ayuda-calc")
        assert titulo, "Encabezado de tabla debe tener data-ayuda-titulo"
        assert definicion, f"Encabezado '{titulo}' debe tener definición"
        assert calculo, f"Encabezado '{titulo}' debe tener cálculo"

    # 3. Secciones de alertas y brecha
    assert len(extractor.seccion_ayudas) == 4, f"Se esperaban 4 botones de sección en Alertas, encontrados {len(extractor.seccion_ayudas)}"
    for sec in extractor.seccion_ayudas:
        assert sec.get("data-ayuda-def") and sec.get("data-ayuda-calc")

    assert len(extractor.inline_ayudas) >= 1
    for inl in extractor.inline_ayudas:
        assert inl.get("data-ayuda-def") and inl.get("data-ayuda-calc")
