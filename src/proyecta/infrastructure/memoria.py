"""Persistencia en memoria (sustituto de Datastore, T018–T023) para la Entrega 2.

Implementa los puertos de `application/ports.py` sobre listas. Los datos se pierden al
reiniciar y parten de la semilla sintética (T035): es una limitación declarada de la E2.
Cuando exista el proyecto de GCP (S-12), los adaptadores de Datastore reemplazan esta clase
con los mismos métodos. La auditoría y la bitácora son de solo inserción: no hay métodos
para editar ni borrar (RN-78).
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from typing import Any, Sequence
from uuid import UUID

from proyecta.domain.entities import (
    AjusteHC,
    Bitacora,
    Catalogo,
    Contrato,
    EventoAuditoria,
    MetaComercial,
    Parametro,
    Perfil,
    Registro,
    Sesion,
    TarifaPerfil,
    Usuario,
    VigenciaEstadoCalculo,
)
from proyecta.domain.enums import EntidadAuditoria, TipoCatalogo
from proyecta.domain.value_objects import Period
from proyecta.seed.synthetic import generar_semilla


def _valor(x: Any) -> Any:
    return getattr(x, "value", x)


@dataclass
class Registros:
    datos: dict[UUID, Registro] = field(default_factory=dict)

    def obtener(self, registro_id: UUID) -> Registro | None:
        return self.datos.get(registro_id)

    def listar(self, *, owner_id=None, sector_id=None, tipos=None, estados=None, codigos=None, limite=None):
        tipos = {_valor(t) for t in tipos or ()}
        estados = {_valor(e) for e in estados or ()}
        filas = [
            r for r in self.datos.values()
            if (owner_id is None or r.owner_id == owner_id)
            and (sector_id is None or r.sector_id == sector_id)
            and (not tipos or r.tipo.value in tipos)
            and (not estados or r.estado.value in estados)
            and (not codigos or r.codigo in codigos)
        ]
        filas.sort(key=lambda r: r.codigo)
        return filas[:limite] if limite else filas

    def guardar(self, registro: Registro) -> Registro:
        self.datos[registro.id] = registro
        return registro

    def siguiente_codigo(self) -> str:
        """OPD-#### único e inmutable (FR-002); nunca reutiliza un número."""
        ultimo = max((int(r.codigo[4:]) for r in self.datos.values() if r.codigo), default=0)
        return f"OPD-{ultimo + 1:04d}"


@dataclass
class Perfiles:
    perfiles: list[Perfil] = field(default_factory=list)
    tarifas: list[TarifaPerfil] = field(default_factory=list)
    ajustes: list[AjusteHC] = field(default_factory=list)
    quitados: list[Perfil] = field(default_factory=list)  # no se borra físicamente (AGENTS.md)

    def listar_por_registro(self, registro_id: UUID) -> Sequence[Perfil]:
        return sorted((p for p in self.perfiles if p.registro_id == registro_id), key=lambda p: p.orden)

    def obtener(self, perfil_id: UUID) -> Perfil | None:
        return next((p for p in self.perfiles if p.id == perfil_id), None)

    def tarifas_de(self, perfil_id: UUID) -> Sequence[TarifaPerfil]:
        return sorted((t for t in self.tarifas if t.perfil_id == perfil_id), key=lambda t: t.vigente_desde)

    def ajustes_de(self, registro_id: UUID) -> Sequence[AjusteHC]:
        return [a for a in self.ajustes if a.registro_id == registro_id]

    def guardar(self, perfil: Perfil) -> Perfil:
        if perfil not in self.perfiles:
            self.perfiles.append(perfil)
        return perfil

    def quitar(self, perfil_id: UUID) -> None:
        """Quita el perfil del cálculo (FR-011); se conserva aparte y el cambio queda auditado."""
        self.quitados += [p for p in self.perfiles if p.id == perfil_id]
        self.perfiles = [p for p in self.perfiles if p.id != perfil_id]

    def guardar_tarifa(self, tarifa: TarifaPerfil) -> TarifaPerfil:
        self.tarifas.append(tarifa)
        return tarifa


@dataclass
class Contratos:
    datos: dict[UUID, Contrato] = field(default_factory=dict)

    def obtener_por_registro(self, registro_id: UUID) -> Contrato | None:
        return self.datos.get(registro_id)

    def listar(self) -> Sequence[Contrato]:
        return list(self.datos.values())

    def guardar(self, contrato: Contrato) -> Contrato:
        self.datos[contrato.registro_id] = contrato
        return contrato


@dataclass
class Parametros:
    datos: list[Parametro] = field(default_factory=list)

    def listar(self, clave: str | None = None) -> Sequence[Parametro]:
        return sorted((p for p in self.datos if clave is None or p.clave == clave), key=lambda p: p.vigente_desde)

    def vigente(self, clave: str, mes: date) -> Parametro | None:
        candidatos = [p for p in self.datos if p.clave == clave and p.vigente_desde <= mes]
        return max(candidatos, key=lambda p: (p.vigente_desde, p.creado_en)) if candidatos else None

    def guardar(self, parametro: Parametro) -> Parametro:
        self.datos.append(parametro)
        return parametro


@dataclass
class Vigencias:
    datos: list[VigenciaEstadoCalculo] = field(default_factory=list)

    def listar(self, registro_id: UUID, campo=None) -> Sequence[VigenciaEstadoCalculo]:
        return [v for v in self.datos if v.registro_id == registro_id and (campo is None or v.campo is campo)]

    def listar_todas(self) -> Sequence[VigenciaEstadoCalculo]:
        return list(self.datos)

    def guardar(self, vigencia: VigenciaEstadoCalculo) -> VigenciaEstadoCalculo:
        self.datos.append(vigencia)
        return vigencia


def _ts_evento(x: Any) -> float:
    dt = getattr(x, "fecha_hora", None) or getattr(x, "creado_en", None) or getattr(x, "momento", None)
    if dt is None:
        return 0.0
    if dt.tzinfo is not None:
        return dt.timestamp()
    return dt.replace(tzinfo=timezone.utc).timestamp()


@dataclass
class SoloInsercion:
    """Bitácora y auditoría: listar y registrar, nada más (RN-78, RN-81)."""

    datos: list = field(default_factory=list)

    def listar_por_registro(self, registro_id: UUID) -> Sequence:
        return sorted((x for x in self.datos if x.registro_id == registro_id),
                      key=_ts_evento, reverse=True)

    def todos(self) -> Sequence:
        return sorted(self.datos, key=_ts_evento, reverse=True)

    def registrar(self, entrada):
        self.datos.append(entrada)
        return entrada


@dataclass
class Usuarios:
    datos: dict[UUID, Usuario] = field(default_factory=dict)

    def obtener(self, usuario_id: UUID) -> Usuario | None:
        return self.datos.get(usuario_id)

    def por_email(self, email: str) -> Usuario | None:
        email = (email or "").strip().lower()
        return next((u for u in self.datos.values() if u.email == email), None)

    def listar(self) -> list[Usuario]:
        return list(self.datos.values())


@dataclass
class Sesiones:
    datos: dict[str, Sesion] = field(default_factory=dict)

    def obtener(self, sesion_id: str) -> Sesion | None:
        return self.datos.get(sesion_id)

    def guardar(self, sesion: Sesion) -> Sesion:
        self.datos[sesion.id] = sesion
        return sesion


@dataclass
class Catalogos:
    datos: list[Catalogo] = field(default_factory=list)

    def listar(self, tipo=None, *, activos: bool = True) -> Sequence[Catalogo]:
        return sorted((c for c in self.datos if (tipo is None or c.tipo is tipo) and (c.activo or not activos)),
                      key=lambda c: c.orden)

    def etiqueta(self, catalogo_id: UUID | None) -> str:
        return next((c.etiqueta for c in self.datos if c.id == catalogo_id), "—")


@dataclass
class Metas:
    datos: list[MetaComercial] = field(default_factory=list)

    def obtener(self, sector_id: UUID | None = None, mes: date | None = None, *, lider_id: UUID | None = None) -> MetaComercial | None:
        if lider_id:
            if mes is not None:
                return next((m for m in self.datos if m.lider_id == lider_id and m.mes == mes), None)
            return self.vigente(lider_id, date.today())
        return next((m for m in self.datos if (sector_id is None or m.sector_id == sector_id) and (mes is None or m.mes == mes)), None)

    def listar(self, *, sector_id: UUID | None = None, lider_id: UUID | None = None) -> Sequence[MetaComercial]:
        return [m for m in self.datos
                if (sector_id is None or m.sector_id == sector_id)
                and (lider_id is None or m.lider_id == lider_id)]

    def vigente(self, lider_id: UUID, mes: date) -> MetaComercial | None:
        """Meta comercial vigente para el líder en el mes (no afecta anteriores y rige como default hacia el futuro)."""
        candidatos = [m for m in self.datos if m.lider_id == lider_id and m.mes <= mes]
        return max(candidatos, key=lambda m: (m.mes, m.creado_en)) if candidatos else None

    def guardar(self, meta: MetaComercial) -> None:
        if meta.lider_id:
            # No afecta metas anteriores (mes < meta.mes) y fija la nueva como default para meses posteriores (mes >= meta.mes)
            self.datos = [m for m in self.datos if not (m.lider_id == meta.lider_id and m.mes >= meta.mes)]
            self.datos.append(meta)
        else:
            existente = next((m for m in self.datos if m.id == meta.id or (m.sector_id == meta.sector_id and m.mes == meta.mes)), None)
            if existente:
                existente.monto_clp = meta.monto_clp
                existente.actualizado_en = meta.actualizado_en
                existente.usuario_id = meta.usuario_id
            else:
                self.datos.append(meta)


@dataclass
class Almacen:
    """Todos los repositorios de la app; la fachada que inyecta `main.py`."""

    registros: Registros = field(default_factory=Registros)
    perfiles: Perfiles = field(default_factory=Perfiles)
    contratos: Contratos = field(default_factory=Contratos)
    parametros: Parametros = field(default_factory=Parametros)
    vigencias: Vigencias = field(default_factory=Vigencias)
    bitacora: SoloInsercion = field(default_factory=SoloInsercion)
    auditoria: SoloInsercion = field(default_factory=SoloInsercion)
    usuarios: Usuarios = field(default_factory=Usuarios)
    sesiones: Sesiones = field(default_factory=Sesiones)
    catalogos: Catalogos = field(default_factory=Catalogos)
    metas: Metas = field(default_factory=Metas)

    @classmethod
    def con_semilla(cls, cantidad: int = 60, primer_mes: Period | None = None) -> "Almacen":
        """Datos 100 % sintéticos (SC-012); el horizonte arranca en el mes en curso."""
        datos = generar_semilla(cantidad, primer_mes or Period.desde_fecha(date.today()))
        from proyecta.infrastructure.auth.sessions import hash_password  # evita ciclo al importar

        clave = os.environ.get("PROYECTA_DEMO_PASSWORD", "proyecta-demo")
        hash_demo = hash_password(clave)
        for usuario in datos.usuarios:
            usuario.password_hash = hash_demo
        for meta in datos.metas:  # asegurar que la meta supere al backlog contractual
            meta.monto_clp = max(meta.monto_clp, 120_000_000)
        eventos_auditoria = [
            EventoAuditoria(
                entidad=EntidadAuditoria.REGISTRO,
                entidad_id=r.id,
                registro_id=r.id,
                campo="creacion",
                valor_anterior=None,
                valor_nuevo={
                    "codigo": r.codigo,
                    "tipo": r.tipo.value,
                    "estado": r.estado.value,
                    "flujo": r.flujo.value,
                    "probabilidad_bp": r.probabilidad_bp,
                    "confiabilidad_bp": r.confiabilidad_bp,
                    "perfiles": sum(1 for p in datos.perfiles if p.registro_id == r.id),
                },
                usuario_id=r.creado_por or r.owner_id,
                fecha_hora=r.creado_en,
                fecha_efectiva=r.fecha_creacion,
                motivo="Creación inicial del registro",
                mab_antes=0,
                forecast_antes=0,
            )
            for r in datos.registros
        ]
        return cls(
            registros=Registros({r.id: r for r in datos.registros}),
            perfiles=Perfiles(datos.perfiles, datos.tarifas, datos.ajustes),
            contratos=Contratos({c.registro_id: c for c in datos.contratos}),
            parametros=Parametros(datos.parametros),
            vigencias=Vigencias(datos.vigencias),
            bitacora=SoloInsercion(),
            auditoria=SoloInsercion(eventos_auditoria),
            usuarios=Usuarios({u.id: u for u in datos.usuarios}),
            catalogos=Catalogos(datos.catalogos),
            metas=Metas(datos.metas),
        )

    def opciones(self, tipo: TipoCatalogo) -> list[Catalogo]:
        return list(self.catalogos.listar(tipo))
