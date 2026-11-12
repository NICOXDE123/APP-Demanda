"""Caso de uso de cálculo y previsualización (T074, US3).

Orquesta repositorios y motor. La previsualización es transitoria: no escribe
en repositorios, no altera estados ni cortes y no crea eventos (US3, escenario 6).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Sequence
from uuid import UUID

from proyecta.application.ports import (
    Reloj,
    RepositorioContratos,
    RepositorioParametros,
    RepositorioPerfiles,
    RepositorioRegistros,
    RepositorioVigencias,
)
from proyecta.domain.engine.service import (
    MotorCalculo,
    ResultadoProyeccion,
    ResultadoRegistro,
)
from proyecta.domain.engine.vigencias import ResolutorVigencias
from proyecta.domain.entities import EntradaCalculo, Parametro, Registro, utcnow
from proyecta.domain.errors import ErrorNoEncontrado
from proyecta.domain.value_objects import Period


@dataclass(frozen=True, slots=True)
class FiltrosProyeccion:
    owner_id: UUID | None = None
    sector_id: UUID | None = None
    estados: tuple[str, ...] = ()
    tipos: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class RelojSistema:
    """Implementación por defecto del puerto ``Reloj``."""

    def ahora(self):
        return utcnow()

    def hoy(self) -> date:
        return self.ahora().date()


@dataclass
class CalcularProyeccion:
    """Serie de 12 meses y detalle por registro."""

    registros: RepositorioRegistros
    perfiles: RepositorioPerfiles
    contratos: RepositorioContratos
    parametros: RepositorioParametros
    vigencias: RepositorioVigencias | None = None
    reloj: Reloj = field(default_factory=RelojSistema)
    motor: MotorCalculo = field(default_factory=MotorCalculo)

    # -- API interna ------------------------------------------------------
    def _parametros(self) -> Sequence[Parametro]:
        return self.parametros.listar("horas_mensuales")

    def _entrada(self, registro: Registro) -> EntradaCalculo:
        perfiles = list(self.perfiles.listar_por_registro(registro.id))
        tarifas = {perfil.id: list(self.perfiles.tarifas_de(perfil.id)) for perfil in perfiles}
        vigencias = (
            list(self.vigencias.listar(registro.id)) if self.vigencias is not None else []
        )
        return EntradaCalculo(
            registro=registro,
            perfiles=perfiles,
            tarifas=tarifas,
            contrato=self.contratos.obtener_por_registro(registro.id),
            ajustes=list(self.perfiles.ajustes_de(registro.id)),
            vigencias=vigencias,
        )

    def _listar(self, filtros: FiltrosProyeccion | None) -> Sequence[Registro]:
        if filtros is None:
            return self.registros.listar()
        return self.registros.listar(
            owner_id=filtros.owner_id,
            sector_id=filtros.sector_id,
            estados=filtros.estados or None,
            tipos=filtros.tipos or None,
        )

    # -- Casos de uso -----------------------------------------------------
    def ejecutar(
        self,
        periodo: Period | str | None = None,
        meses: int = 12,
        filtros: FiltrosProyeccion | None = None,
        registros: Sequence[Registro] | None = None,
    ) -> ResultadoProyeccion:
        """``registros`` permite calcular sobre un subconjunto ya filtrado (dashboard, FR-048)."""
        periodo = self._resolver_periodo(periodo)
        visibles = self._listar(filtros) if registros is None else registros
        entradas = [self._entrada(registro) for registro in visibles]
        return self.motor.calcular_proyeccion(
            entradas, periodo, meses, parametros=self._parametros()
        )

    def calcular_registro(
        self,
        registro_id: UUID,
        periodo: Period | str | None = None,
        meses: int = 12,
    ) -> ResultadoRegistro:
        registro = self.registros.obtener(registro_id)
        if registro is None:
            raise ErrorNoEncontrado(
                "NO_ENCONTRADO",
                "El registro solicitado no existe",
                detalle={"registro_id": str(registro_id)},
            )
        periodo = self._resolver_periodo(periodo)
        entrada = self._entrada(registro)
        resolutor = ResolutorVigencias(entrada.vigencias, self._parametros())
        return self.motor.calcular_registro(entrada, Period.serie(periodo, meses), resolutor)

    def previsualizar(
        self,
        borrador: EntradaCalculo,
        periodo: Period | str | None = None,
        meses: int = 12,
    ) -> ResultadoRegistro:
        """Cálculo transitorio de una edición en curso; nunca persiste."""
        periodo = self._resolver_periodo(periodo)
        resolutor = ResolutorVigencias(borrador.vigencias, self._parametros())
        return self.motor.calcular_registro(
            borrador, Period.serie(periodo, meses), resolutor
        )

    # -- Utilidades -------------------------------------------------------
    def _resolver_periodo(self, periodo: Period | str | None) -> Period:
        if periodo is None:
            return Period.desde_fecha(self.reloj.hoy())
        if isinstance(periodo, str):
            return Period.desde_texto(periodo)
        return periodo


__all__ = ["CalcularProyeccion", "FiltrosProyeccion", "RelojSistema"]
