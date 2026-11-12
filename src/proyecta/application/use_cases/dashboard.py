"""Filtros y tablero ejecutivo (US4; FR-046 a FR-049).

Solo agrega resultados del motor: los totales son la suma de los registros visibles,
nunca promedios recalculados (US4 esc. 2). No contiene fórmulas de negocio.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Any
from uuid import UUID

from proyecta.application.use_cases.calculo import CalcularProyeccion
from proyecta.domain.entities import Registro, Usuario
from proyecta.domain.enums import Bucket, Estado, Rol, Tipo
from proyecta.domain.value_objects import Period
from proyecta.infrastructure.memoria import Almacen

ACTIVOS = (Estado.PENDIENTE, Estado.ADJUDICADA, Estado.EN_CURSO)


@dataclass
class Filtros:
    texto: str = ""
    sector_id: UUID | None = None
    cliente_id: UUID | None = None
    manager_id: UUID | None = None
    owner_id: UUID | None = None
    tipo: str = ""
    estado: str = ""
    flujo: str = ""
    modalidad: str = ""
    solo_activos: bool = False
    confirmado: bool = False  # vista de Backlog confirmado (FR-032)
    periodo: Period = field(default_factory=lambda: Period.desde_fecha(date.today()))
    meses: int = 12

    def a_query(self, **cambios: Any) -> str:
        valores = {
            "q": self.texto, "sector": self.sector_id, "cliente": self.cliente_id, "manager": self.manager_id,
            "owner": self.owner_id, "tipo": self.tipo, "estado": self.estado, "flujo": self.flujo,
            "modalidad": self.modalidad, "activos": "1" if self.solo_activos else "",
            "confirmado": "1" if self.confirmado else "", "desde": str(self.periodo), "meses": self.meses,
        }
        valores.update(cambios)
        from urllib.parse import urlencode

        return urlencode({k: v for k, v in valores.items() if v not in (None, "", False)})


def visibles(almacen: Almacen, usuario: Usuario, f: Filtros) -> list[Registro]:
    """Registros que el usuario puede ver (el líder, solo los suyos) y que cumplen los filtros (FR-006, FR-048)."""
    texto = f.texto.lower()
    filas = []
    for r in almacen.registros.listar():
        if usuario.rol is Rol.LIDER and r.owner_id != usuario.id:
            continue
        if texto and texto not in f"{r.codigo} {r.servicio_proyecto} {almacen.catalogos.etiqueta(r.cliente_id)}".lower():
            continue
        if any(v is not None and getattr(r, campo) != v for campo, v in (
                ("sector_id", f.sector_id), ("cliente_id", f.cliente_id),
                ("manager_id", f.manager_id), ("owner_id", f.owner_id))):
            continue
        if any(v and getattr(r, campo).value != v for campo, v in (
                ("tipo", f.tipo), ("estado", f.estado), ("flujo", f.flujo), ("modalidad", f.modalidad))):
            continue
        if f.solo_activos and r.estado not in ACTIVOS:
            continue
        filas.append(r)
    return filas


def tablero(almacen: Almacen, calculo: CalcularProyeccion, usuario: Usuario, f: Filtros) -> dict[str, Any]:
    registros = visibles(almacen, usuario, f)
    resultado = calculo.ejecutar(periodo=f.periodo, meses=f.meses, registros=registros)
    por_registro: dict[UUID, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    confirmado_mes: dict[Period, int] = defaultdict(int)
    for d in resultado.detalles:
        fila = por_registro[d.registro_id]
        fila["forecast"] += d.forecast_clp
        fila["mab"] += d.mab_clp
        fila["backlog"] += d.backlog_clp
        fila["base"] += d.base_clp if d.bolsa is Bucket.MAB else 0
        fila["potencial"] += d.ingreso_potencial_clp
        fila["base_p"] += d.base_clp * d.probabilidad_bp if d.bolsa is Bucket.MAB else 0
        fila["base_c"] += d.base_clp * d.confiabilidad_bp if d.bolsa is Bucket.MAB else 0
        if d.backlog_confirmado:
            fila["confirmado"] += d.mab_clp
            confirmado_mes[d.mes] += d.mab_clp
    filas = [(r, por_registro[r.id]) for r in registros]
    if f.confirmado:
        filas = [(r, c) for r, c in filas if c["confirmado"]]

    meses = list(resultado.meses)
    sectores_visibles = {r.sector_id for r in registros} if (f.sector_id or usuario.rol is Rol.LIDER) else None
    meta_mes = {m.mes: sum(x.monto_clp for x in almacen.metas.listar()
                           if x.mes == m.mes.inicio and (sectores_visibles is None or x.sector_id in sectores_visibles))
                for m in meses}
    total = resultado.totales
    meta = sum(meta_mes.values())
    base_mab = sum(c["base"] for _, c in filas)

    def agrupar(clave) -> list[dict[str, Any]]:
        grupos: dict[Any, dict[str, int]] = defaultdict(lambda: defaultdict(int))
        for r, c in filas:
            g = grupos[clave(r)]
            g["registros"] += 1
            g["forecast"] += c["forecast"]
            g["mab"] += c["mab"]
            g["backlog"] += c["backlog"]
        return sorted(({"clave": k, **v} for k, v in grupos.items()), key=lambda g: -g["forecast"])

    hoy = date.today()
    proximos = []
    for r in registros:
        if r.estado not in ACTIVOS:
            continue
        ingresos = [p.fecha_ingreso for p in almacen.perfiles.listar_por_registro(r.id)] or [r.fecha_ingreso]
        futuros = [d for d in ingresos if d and hoy <= d <= hoy + timedelta(days=90)]
        if futuros:
            dias = (min(futuros) - hoy).days
            proximos.append({"r": r, "fecha": min(futuros), "tramo": 30 if dias <= 30 else 60 if dias <= 60 else 90})
    ids = {r.id for r in registros}
    contratos = []
    for c in almacen.contratos.listar():
        if c.registro_id in ids and c.fecha_fin and c.fecha_fin <= hoy + timedelta(days=90):
            dias = (c.fecha_fin - hoy).days
            contratos.append({"c": c, "r": almacen.registros.obtener(c.registro_id), "dias": dias,
                              "estado": "Vencido" if dias < 0 else "Por vencer"})
    liberaciones = [{"p": p, "r": almacen.registros.obtener(p.registro_id)}
                    for p in almacen.perfiles.perfiles
                    if p.registro_id in ids and p.fecha_fin and hoy <= p.fecha_fin <= hoy + timedelta(days=90)]

    return {
        "filtros": f, "resultado": resultado, "meses": meses, "meta_mes": meta_mes,
        "confirmado_mes": confirmado_mes,
        "filas": sorted(filas, key=lambda x: -x[1]["forecast"]),
        "kpi": {
            "forecast": total.forecast_clp, "mab": total.mab_clp, "backlog": total.backlog_clp,
            "confirmado": sum(confirmado_mes.values()), "potencial": total.ingreso_potencial_clp,
            "meta": meta, "gap": meta - total.forecast_clp,
            "cobertura_bp": round(total.forecast_clp * 10_000 / meta) if meta > 0 else None,
            "hc_inicio": meses[0].hc if meses else 0, "hc_fin": meses[-1].hc if meses else 0,
            "oportunidades": sum(1 for r in registros if r.tipo is Tipo.OPORTUNIDAD and r.estado is Estado.PENDIENTE),
            "demandas": sum(1 for r in registros if r.tipo is Tipo.DEMANDA and r.estado in (Estado.ADJUDICADA, Estado.EN_CURSO)),
            "continuidades": sum(1 for r in registros if r.tipo is Tipo.CONTINUIDAD and r.estado is Estado.EN_CURSO),
            "probabilidad_bp": round(sum(c["base_p"] for _, c in filas) / base_mab) if base_mab else None,
            "confiabilidad_bp": round(sum(c["base_c"] for _, c in filas) / base_mab) if base_mab else None,
            "registros": len(filas),
            "sin_perfiles": sum(1 for r in registros if r.estado in ACTIVOS and not almacen.perfiles.listar_por_registro(r.id)),
        },
        "por_sector": agrupar(lambda r: r.sector_id),
        "meta_sector": {s: sum(x.monto_clp for x in almacen.metas.listar(sector_id=s)
                               if any(x.mes == m.mes.inicio for m in meses))
                        for s in {r.sector_id for r in registros}},
        "por_owner": agrupar(lambda r: r.owner_id),
        "por_cliente": agrupar(lambda r: r.cliente_id)[:10],
        "por_estado": agrupar(lambda r: r.estado.value),
        "por_flujo": agrupar(lambda r: r.flujo.value),
        "proximos": sorted(proximos, key=lambda x: x["fecha"]),
        "contratos": sorted(contratos, key=lambda x: x["dias"]),
        "liberaciones": liberaciones,
    }
