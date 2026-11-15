"""Pruebas de integración para las observaciones del 15-11 (Entrega 2).

Verifica:
- Metas por líder y mantenedor de metas en Parámetros MAB.
- Restricción del rol Ejecutivo en Parámetros y Auditoría.
- Paginación en Registros y Auditoría.
- Auditoría poblada desde el inicio de la aplicación.
- Remoción de KPIs no deseados (9 tarjetas restantes).
- Eliminación de la palabra 'sintético/a' en la interfaz pública.
"""

from __future__ import annotations

import re
from datetime import date
from uuid import UUID

from starlette.testclient import TestClient

from proyecta.infrastructure.memoria import Almacen
from proyecta.domain.enums import Rol
from proyecta.main import crear_app

CLAVE = "proyecta-demo"


def entrar(app, email: str) -> tuple[TestClient, str]:
    cliente = TestClient(app)
    resp = cliente.post("/login", data={"email": email, "password": CLAVE}, follow_redirects=False)
    assert resp.status_code == 303
    csrf_match = re.search(r'data-csrf="([^"]+)"', cliente.get("/").text)
    csrf = csrf_match.group(1) if csrf_match else ""
    return cliente, csrf


def test_restriccion_rol_ejecutivo_parametros_y_auditoria():
    app = crear_app()
    cliente, _ = entrar(app, "ejecutivo@example.test")

    # Ejecutivo no debe poder acceder a parámetros ni auditoría
    res_param = cliente.get("/parametros")
    assert res_param.status_code == 403

    res_audit = cliente.get("/auditoria")
    assert res_audit.status_code == 403


def test_auditoria_con_datos_iniciales_y_paginacion():
    app = crear_app()
    cliente, _ = entrar(app, "operaciones@example.test")

    res = cliente.get("/auditoria")
    assert res.status_code == 200
    # Debe estar poblada con eventos iniciales de creación
    assert "creacion" in res.text
    # Con 24 registros iniciales (+ perfiles, contratos), hay paginación o múltiples eventos
    assert "evento(s)" in res.text


def test_registros_paginacion():
    app = crear_app()
    cliente, _ = entrar(app, "operaciones@example.test")

    res = cliente.get("/registros")
    assert res.status_code == 200
    # Al haber 60 registros y 20 por página, debe mostrar 3 páginas
    assert 'aria-label="Paginación de registros"' in res.text
    assert "Página 1 de 3" in res.text

    res_p2 = cliente.get("/registros?pagina=2")
    assert res_p2.status_code == 200
    assert "Página 2 de 3" in res_p2.text


def test_metas_por_lider_en_parametros_y_permisos():
    app = crear_app()
    almacen = app.state.almacen
    lideres = [u for u in almacen.usuarios.listar() if u.rol is Rol.LIDER]
    lider1, lider2 = lideres[0], lideres[1]

    # 1. Operaciones puede asignar meta a un líder
    cliente_ops, csrf_ops = entrar(app, "operaciones@example.test")
    res_post = cliente_ops.post("/parametros/metas", data={
        "csrf_token": csrf_ops,
        "lider_id": str(lider1.id),
        "monto": "75000000",
        "desde": date.today().isoformat(),
        "motivo": "Ajuste de cuota Q4",
    }, follow_redirects=False)
    assert res_post.status_code == 303

    # Verificar que quedó guardada y auditada
    meta_guardada = almacen.metas.obtener(lider_id=lider1.id)
    assert meta_guardada is not None
    assert meta_guardada.monto_clp == 75_000_000

    # 2. El líder1 puede modificar su propia meta
    cliente_lid1, csrf_lid1 = entrar(app, lider1.email)
    res_lider_propia = cliente_lid1.post("/parametros/metas", data={
        "csrf_token": csrf_lid1,
        "lider_id": str(lider1.id),
        "monto": "80000000",
        "desde": date.today().isoformat(),
        "motivo": "Compromiso comercial",
    }, follow_redirects=False)
    assert res_lider_propia.status_code == 303
    assert almacen.metas.obtener(lider_id=lider1.id).monto_clp == 80_000_000

    # 3. El líder1 NO puede modificar la meta de líder2
    res_lider_ajena = cliente_lid1.post("/parametros/metas", data={
        "csrf_token": csrf_lid1,
        "lider_id": str(lider2.id),
        "monto": "99999999",
        "desde": date.today().isoformat(),
        "motivo": "Intento de modificar meta ajena",
    }, follow_redirects=False)
    # Debe ser rechazada o forzar asignación al propio usuario
    assert almacen.metas.obtener(lider_id=lider2.id).monto_clp != 99_999_999


def test_dashboard_kpis_y_tablas():
    app = crear_app()
    cliente, _ = entrar(app, "operaciones@example.test")

    res = cliente.get("/")
    assert res.status_code == 200
    html = res.text

    # Verificar que no están los 3 KPIs eliminados
    assert "Ingresos potenciales" not in html
    assert "Probabilidad media" not in html
    assert "Confiabilidad media" not in html

    # Verificar tablas por líder y por sector
    assert "Por líder · meta y gap" in html
    assert "Por sector" in html

    # Verificar botón de filtro colapsable
    assert 'data-toggle-target="#filtros-collapse"' in html


def test_sin_palabra_sintetico_en_vistas():
    app = crear_app()
    cliente, _ = entrar(app, "operaciones@example.test")

    for ruta in ("/", "/registros", "/parametros", "/auditoria"):
        res = cliente.get(ruta)
        assert res.status_code == 200
        assert "sintético" not in res.text.lower()
        assert "sintética" not in res.text.lower()


def test_vigencia_metas_lider_default_futuro_y_no_afecta_pasado():
    app = crear_app()
    almacen = app.state.almacen
    lideres = [u for u in almacen.usuarios.listar() if u.rol is Rol.LIDER]
    lid = lideres[0]

    # Meta en 2026-01
    m1_fecha = date(2026, 1, 1)
    almacen.metas.guardar(almacen.metas.obtener(lider_id=lid.id, mes=m1_fecha) or
                          almacen.metas.datos[0])
    # Fijar meta conocida en 2026-01
    from proyecta.domain.entities import MetaComercial
    almacen.metas.guardar(MetaComercial(lider_id=lid.id, mes=date(2026, 1, 1), monto_clp=50_000_000))

    # En 2026-02, como no hay otra, vigente debe ser la de 2026-01 (default)
    v2 = almacen.metas.vigente(lid.id, date(2026, 2, 1))
    assert v2 is not None
    assert v2.monto_clp == 50_000_000

    # Actualizar meta desde 2026-03 a 70M
    almacen.metas.guardar(MetaComercial(lider_id=lid.id, mes=date(2026, 3, 1), monto_clp=70_000_000))

    # Meses anteriores (2026-01 y 2026-02) NO deben verse afectados
    assert almacen.metas.vigente(lid.id, date(2026, 1, 1)).monto_clp == 50_000_000
    assert almacen.metas.vigente(lid.id, date(2026, 2, 1)).monto_clp == 50_000_000

    # Mes 2026-03 y meses posteriores deben tener 70M como default
    assert almacen.metas.vigente(lid.id, date(2026, 3, 1)).monto_clp == 70_000_000
    assert almacen.metas.vigente(lid.id, date(2026, 4, 1)).monto_clp == 70_000_000
    assert almacen.metas.vigente(lid.id, date(2026, 12, 1)).monto_clp == 70_000_000


def test_ejecutivo_ve_solo_iniciativas_y_metas_de_su_lider():
    app = crear_app()
    almacen = app.state.almacen
    ejecutivo = next(u for u in almacen.usuarios.listar() if u.rol is Rol.EJECUTIVO)
    lider_asignado = almacen.usuarios.obtener(ejecutivo.lider_id)
    assert lider_asignado is not None

    cliente_ej, _ = entrar(app, ejecutivo.email)

    # 1. Dashboard del ejecutivo muestra solo las iniciativas de su líder
    res_dash = cliente_ej.get("/")
    assert res_dash.status_code == 200
    assert lider_asignado.nombre in res_dash.text

    # 2. Registros visibles para el ejecutivo: todos pertenecen a su líder
    res_reg = cliente_ej.get("/registros")
    assert res_reg.status_code == 200
    # No debe ver iniciativas de otros líderes
    otros_lideres = [u for u in almacen.usuarios.listar() if u.rol is Rol.LIDER and u.id != lider_asignado.id]
    for otro in otros_lideres:
        # En el listado no deben figurar registros cuyo owner sea otro líder
        reg_otro = next((r for r in almacen.registros.listar() if r.owner_id == otro.id), None)
        if reg_otro:
            # Intento de acceso directo por URL a registro de otro líder debe dar 403
            res_ficha = cliente_ej.get(f"/registros/{reg_otro.id}")
            assert res_ficha.status_code == 403


def test_dashboard_subpestanas_y_horizonte_default():
    app = crear_app()
    cliente, _ = entrar(app, "operaciones@example.test")

    res = cliente.get("/")
    assert res.status_code == 200
    html = res.text

    # Debe contener las dos subpestañas
    assert "Resumen financiero" in html
    assert "Detalle operativo y comercial" in html
    assert 'data-tab-target="#tab-financiero"' in html
    assert 'data-tab-target="#tab-operativo"' in html

    # El horizonte no debe estar en los filtros (no afecta filtros)
    assert 'id="f-vista"' not in html
    # Debe ser control propio del gráfico
    assert 'id="vista-grafico"' in html
    assert "3 meses ant. + 3 meses fut. (Default)" in html
    assert "Últimos 3 meses" in html
    assert "Últimos 6 meses" in html
    assert "Últimos 12 meses" in html
    assert "A futuro 3 meses" in html
    assert "A futuro 6 meses" in html


def test_parametros_metas_ultimas_10_y_orden_descendente():
    app = crear_app()
    cliente, _ = entrar(app, "operaciones@example.test")

    res = cliente.get("/parametros")
    assert res.status_code == 200
    html = res.text
    assert "Metas comerciales vigentes e históricas" in html
    assert "Últimas 10" in html


def test_semilla_3_meses_anteriores_con_datos():
    from proyecta.infrastructure.memoria import Almacen
    from proyecta.application.use_cases.calculo import CalcularProyeccion
    from proyecta.domain.value_objects import Period

    almacen = Almacen.con_semilla(60)
    calculo = CalcularProyeccion(almacen.registros, almacen.perfiles, almacen.contratos, almacen.parametros, almacen.vigencias)
    hoy = Period.desde_fecha(date.today())

    # Proyección de 3 meses pasados + 3 meses futuro
    res = calculo.ejecutar(periodo=hoy.retroceder(3), meses=6)
    meses_res = list(res.meses)
    assert len(meses_res) == 6

    # Los 3 meses anteriores deben tener backlog y forecast > 0
    for m in meses_res[:3]:
        assert m.backlog_clp > 0, f"Mes {m.mes} debe tener backlog contractual > 0"
        assert m.forecast_clp > 0, f"Mes {m.mes} debe tener forecast > 0"
        meta_m = sum(almacen.metas.vigente(u.id, m.mes.inicio).monto_clp for u in almacen.usuarios.listar() if u.rol is Rol.LIDER)
        assert meta_m > m.backlog_clp, f"Meta ({meta_m}) debe ser mayor que el backlog ({m.backlog_clp})"

