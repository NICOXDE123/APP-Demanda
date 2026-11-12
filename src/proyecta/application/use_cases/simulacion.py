"""Simulación de escenarios en memoria (T145, US10).

La simulación se ejecuta sobre copias de las entidades, no persiste, no cambia
estados ni cortes y rotula el resultado como ``simulado`` (FR-085). Por diseño
no recibe repositorios de escritura: solo puertos de lectura.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import date
from decimal import Decimal
from typing import Any, Mapping, Sequence
from uuid import UUID

from proyecta.application.ports import (
    Reloj,
    RepositorioContratos,
    RepositorioParametros,
    RepositorioPerfiles,
    RepositorioRegistros,
    RepositorioVigencias,
)
from proyecta.application.use_cases.calculo import FiltrosProyeccion, RelojSistema
from proyecta.domain.engine.service import MotorCalculo, ResultadoProyeccion
from proyecta.domain.entities import EntradaCalculo, Parametro, Registro
from proyecta.domain.enums import CampoVigencia, TipoParametro
from proyecta.domain.errors import ErrorValidacion
from proyecta.domain.value_objects import Period, Percentage

CAMPOS_SIMULABLES = frozenset({"probabilidad_bp", "confiabilidad_bp"})
"""Solo se permiten cambios de cálculo; nunca de estado, tipo, flujo o fechas."""


@dataclass(frozen=True, slots=True)
class EscenarioSimulacion:
    periodo: Period
    meses: int = 12
    probabilidad: Decimal | None = None
    confiabilidad: Decimal | None = None
    horas_mensuales: int | None = None
    excluir_registro_ids: frozenset[UUID] = frozenset()
    cambios: Mapping[UUID, Mapping[str, Any]] = field(default_factory=dict)
    filtros: FiltrosProyeccion | None = None

    def __post_init__(self) -> None:
        if self.meses < 1 or self.meses > 36:
            raise ErrorValidacion("CANTIDAD_INVALIDA", "La simulación admite entre 1 y 36 meses")
        if self.probabilidad is not None:
            Percentage.desde_decimal(self.probabilidad)
        if self.confiabilidad is not None:
            Percentage.desde_decimal(self.confiabilidad)
        if self.horas_mensuales is not None and self.horas_mensuales <= 0:
            raise ErrorValidacion("RANGO_INVALIDO", "Las horas mensuales deben ser positivas")
        for registro_id, cambios in self.cambios.items():
            desconocidos = set(cambios) - CAMPOS_SIMULABLES
            if desconocidos:
                raise ErrorValidacion(
                    "VALIDACION",
                    "La simulación no puede cambiar estados, tipos, flujos ni fechas",
                    detalle={
                        "registro_id": str(registro_id),
                        "campos": sorted(desconocidos),
                    },
                )


@dataclass
class SimularEscenario:
    """Calcula un escenario aislado y etiquetado, sin tocar datos reales."""

    registros: RepositorioRegistros
    perfiles: RepositorioPerfiles
    contratos: RepositorioContratos
    parametros: RepositorioParametros
    vigencias: RepositorioVigencias | None = None
    reloj: Reloj = field(default_factory=RelojSistema)
    motor: MotorCalculo = field(default_factory=MotorCalculo)

    # -- Construcción de copias ------------------------------------------
    def _parametros(self, escenario: EscenarioSimulacion) -> list[Parametro]:
        parametros = list(self.parametros.listar("horas_mensuales"))
        if escenario.horas_mensuales is not None:
            parametros.append(
                Parametro(
                    clave="horas_mensuales",
                    valor=escenario.horas_mensuales,
                    tipo=TipoParametro.ENTERO,
                    vigente_desde=date(1900, 1, 1),
                )
            )
        return parametros

    def _registro_simulado(
        self, registro: Registro, escenario: EscenarioSimulacion
    ) -> Registro:
        cambios: dict[str, Any] = {}
        if escenario.probabilidad is not None:
            cambios["probabilidad_bp"] = Percentage.desde_decimal(escenario.probabilidad).bp
        if escenario.confiabilidad is not None:
            cambios["confiabilidad_bp"] = Percentage.desde_decimal(escenario.confiabilidad).bp
        cambios.update(escenario.cambios.get(registro.id, {}))
        return replace(registro, **cambios) if cambios else registro

    def _vigencias_simuladas(
        self, registro_id: UUID, escenario: EscenarioSimulacion
    ) -> list:
        if self.vigencias is None:
            return []
        vigentes = list(self.vigencias.listar(registro_id))
        ocultar: set[CampoVigencia] = set()
        if escenario.probabilidad is not None:
            ocultar.add(CampoVigencia.PROBABILIDAD)
        if escenario.confiabilidad is not None:
            ocultar.add(CampoVigencia.CONFIABILIDAD)
        if escenario.cambios.get(registro_id, {}).get("probabilidad_bp") is not None:
            ocultar.add(CampoVigencia.PROBABILIDAD)
        if escenario.cambios.get(registro_id, {}).get("confiabilidad_bp") is not None:
            ocultar.add(CampoVigencia.CONFIABILIDAD)
        return [vigencia for vigencia in vigentes if vigencia.campo not in ocultar]

    def _entrada(self, registro: Registro, escenario: EscenarioSimulacion) -> EntradaCalculo:
        perfiles = list(self.perfiles.listar_por_registro(registro.id))
        return EntradaCalculo(
            registro=self._registro_simulado(registro, escenario),
            perfiles=perfiles,
            tarifas={perfil.id: list(self.perfiles.tarifas_de(perfil.id)) for perfil in perfiles},
            contrato=self.contratos.obtener_por_registro(registro.id),
            ajustes=list(self.perfiles.ajustes_de(registro.id)),
            vigencias=self._vigencias_simuladas(registro.id, escenario),
        )

    # -- Caso de uso ------------------------------------------------------
    def ejecutar(self, escenario: EscenarioSimulacion) -> ResultadoProyeccion:
        registros = self._listar(escenario)
        entradas: Sequence[EntradaCalculo] = [
            self._entrada(registro, escenario)
            for registro in registros
            if registro.id not in escenario.excluir_registro_ids
        ]
        resultado = self.motor.calcular_proyeccion(
            entradas,
            escenario.periodo,
            escenario.meses,
            parametros=self._parametros(escenario),
        )
        return replace(resultado, simulado=True, etiqueta="simulado")

    def _listar(self, escenario: EscenarioSimulacion) -> Sequence[Registro]:
        filtros = escenario.filtros
        if filtros is None:
            return self.registros.listar()
        return self.registros.listar(
            owner_id=filtros.owner_id,
            sector_id=filtros.sector_id,
            estados=filtros.estados or None,
            tipos=filtros.tipos or None,
        )


__all__ = ["CAMPOS_SIMULABLES", "EscenarioSimulacion", "SimularEscenario"]
