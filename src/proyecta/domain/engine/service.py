"""Fachada del motor de cálculo y contrato de resultados (T072).

Es el único punto que combina Base, bolsas, HC y vigencias. No conoce HTTP,
plantillas ni persistencia: recibe entidades y devuelve resultados inmutables
listos para la API y el dashboard.

Garantías del contrato:

- ``Forecast = Backlog contractual + MAB`` en cada mes.
- Cada registro pertenece a una sola bolsa por mes.
- Los totales suman valores ya redondeados (RN-88).
- El detalle conserva los componentes que explican cada cifra (US3, escenario 5).
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from decimal import Decimal
from typing import Iterable, Sequence
from uuid import UUID

from proyecta.domain.engine.base import ComponenteBase, detallar_base
from proyecta.domain.engine.bags import (
    bolsa_de,
    calcular_backlog,
    calcular_mab,
    es_backlog_confirmado,
    limite_actividad,
    mes_en_calculo,
)
from proyecta.domain.engine.headcount import CierreMes, grilla_hc
from proyecta.domain.engine.vigencias import ResolutorVigencias
from proyecta.domain.entities import EntradaCalculo, Parametro, Registro
from proyecta.domain.enums import Bucket
from proyecta.domain.value_objects import Period, redondear_clp

FORMULA_BASE = "Base = Σ hc × dedicación × tarifa_hora × horas_mes × fracción_activa"
FORMULA_MAB = "MAB = Base × probabilidad × confiabilidad"
FORMULA_BACKLOG = "Backlog = monto_mensual × fracción_activa_contrato"
FORMULA_FORECAST = "Forecast = Backlog contractual + MAB"
VERSION_MOTOR = "1.0.0"


@dataclass(frozen=True, slots=True)
class DetalleRegistroMes:
    """Cifras explicadas de un registro en un mes."""

    registro_id: UUID
    codigo: str
    mes: Period
    bolsa: Bucket | None
    base_clp: int
    probabilidad_bp: int
    confiabilidad_bp: int
    mab_clp: int
    backlog_clp: int
    forecast_clp: int
    ingreso_potencial_clp: int
    hc: int
    componentes: tuple[ComponenteBase, ...] = ()
    advertencias: tuple[str, ...] = ()
    excluido: bool = False
    backlog_confirmado: bool = False

    @property
    def formula(self) -> str:
        if self.bolsa is Bucket.BACKLOG_CONTRACTUAL:
            return FORMULA_BACKLOG
        return FORMULA_MAB

    @property
    def probabilidad_pct(self) -> Decimal:
        return Decimal(self.probabilidad_bp) / Decimal(100)

    @property
    def confiabilidad_pct(self) -> Decimal:
        return Decimal(self.confiabilidad_bp) / Decimal(100)

    def a_dict(self) -> dict:
        return {
            "registro_id": str(self.registro_id),
            "codigo": self.codigo,
            "mes": str(self.mes),
            "bolsa": self.bolsa.value if self.bolsa else None,
            "base_clp": self.base_clp,
            "probabilidad_bp": self.probabilidad_bp,
            "confiabilidad_bp": self.confiabilidad_bp,
            "mab_clp": self.mab_clp,
            "backlog_clp": self.backlog_clp,
            "forecast_clp": self.forecast_clp,
            "ingreso_potencial_clp": self.ingreso_potencial_clp,
            "hc": self.hc,
            "excluido": self.excluido,
            "backlog_confirmado": self.backlog_confirmado,
            "formula": self.formula,
            "advertencias": list(self.advertencias),
            "componentes": [
                {
                    "perfil_id": str(componente.perfil_id),
                    "nombre_perfil_id": (
                        str(componente.nombre_perfil_id)
                        if componente.nombre_perfil_id
                        else None
                    ),
                    "hc": componente.hc,
                    "dedicacion_pct": componente.dedicacion_pct,
                    "tarifa_hora_centavos": componente.tarifa_hora_centavos,
                    "dias_activos": componente.dias_activos,
                    "fraccion_activa": float(componente.fraccion_activa),
                    "subtotal_clp": componente.subtotal_clp,
                }
                for componente in self.componentes
            ],
        }


@dataclass(frozen=True, slots=True)
class SerieMes:
    """Fila agregada de la serie mensual."""

    mes: Period
    base_clp: int
    mab_clp: int
    backlog_clp: int
    forecast_clp: int
    ingreso_potencial_clp: int
    hc: int

    def a_dict(self) -> dict:
        return {
            "mes": str(self.mes),
            "base_clp": self.base_clp,
            "mab_clp": self.mab_clp,
            "backlog_clp": self.backlog_clp,
            "forecast_clp": self.forecast_clp,
            "ingreso_potencial_clp": self.ingreso_potencial_clp,
            "hc": self.hc,
        }

    def a_contrato(self) -> dict:
        """Forma exacta del esquema ``Forecast`` de ``openapi.yaml``."""
        return {
            "mes": str(self.mes),
            "backlog_contractual": self.backlog_clp,
            "mab": self.mab_clp,
            "forecast": self.forecast_clp,
            "hc": self.hc,
        }


@dataclass(frozen=True, slots=True)
class TotalesSerie:
    base_clp: int
    mab_clp: int
    backlog_clp: int
    forecast_clp: int
    ingreso_potencial_clp: int

    def a_dict(self) -> dict:
        return {
            "base_clp": self.base_clp,
            "mab_clp": self.mab_clp,
            "backlog_clp": self.backlog_clp,
            "forecast_clp": self.forecast_clp,
            "ingreso_potencial_clp": self.ingreso_potencial_clp,
        }


@dataclass(frozen=True, slots=True)
class ResultadoRegistro:
    """Serie de un registro con su detalle mes a mes."""

    registro: Registro
    meses: tuple[DetalleRegistroMes, ...]

    @property
    def serie(self) -> tuple[SerieMes, ...]:
        return tuple(
            SerieMes(
                mes=detalle.mes,
                base_clp=detalle.base_clp,
                mab_clp=detalle.mab_clp,
                backlog_clp=detalle.backlog_clp,
                forecast_clp=detalle.forecast_clp,
                ingreso_potencial_clp=detalle.ingreso_potencial_clp,
                hc=detalle.hc,
            )
            for detalle in self.meses
        )

    def total_mab(self) -> int:
        return sum(detalle.mab_clp for detalle in self.meses)

    def total_forecast(self) -> int:
        return sum(detalle.forecast_clp for detalle in self.meses)


@dataclass(frozen=True, slots=True)
class ImpactoCalculo:
    """Impacto de un cambio en MAB y Forecast para la auditoría (T077)."""

    mab_antes: int
    mab_despues: int
    forecast_antes: int
    forecast_despues: int

    @property
    def mab_delta(self) -> int:
        return self.mab_despues - self.mab_antes

    @property
    def forecast_delta(self) -> int:
        return self.forecast_despues - self.forecast_antes

    def a_dict(self) -> dict:
        return {
            "mab_antes": self.mab_antes,
            "mab_despues": self.mab_despues,
            "forecast_antes": self.forecast_antes,
            "forecast_despues": self.forecast_despues,
            "mab_delta": self.mab_delta,
            "forecast_delta": self.forecast_delta,
        }


@dataclass(frozen=True, slots=True)
class ResultadoProyeccion:
    """Serie agregada de 12 meses con el detalle que la respalda."""

    periodo: Period
    meses: tuple[SerieMes, ...]
    detalles: tuple[DetalleRegistroMes, ...]
    totales: TotalesSerie
    advertencias: tuple[str, ...] = ()
    simulado: bool = False
    etiqueta: str | None = None
    version_motor: str = VERSION_MOTOR

    def detalles_de(self, registro_id: UUID) -> tuple[DetalleRegistroMes, ...]:
        return tuple(detalle for detalle in self.detalles if detalle.registro_id == registro_id)

    def a_dict(self) -> dict:
        return {
            "periodo": str(self.periodo),
            "version_motor": self.version_motor,
            "simulado": self.simulado,
            "etiqueta": self.etiqueta,
            "serie": [mes.a_dict() for mes in self.meses],
            "meses": [mes.a_contrato() for mes in self.meses],
            "totales": self.totales.a_dict(),
            "advertencias": list(self.advertencias),
        }


class MotorCalculo:
    """Motor único y determinista de Base, MAB, Backlog, Forecast y HC."""

    def __init__(self, *, estricto: bool = False) -> None:
        self.estricto = estricto

    # -- Registro ---------------------------------------------------------
    def calcular_registro(
        self,
        entrada: EntradaCalculo,
        meses: Sequence[Period],
        resolutor: ResolutorVigencias | None = None,
    ) -> ResultadoRegistro:
        registro = entrada.registro
        resolutor = resolutor or ResolutorVigencias(entrada.vigencias)
        grilla: dict[Period, CierreMes] = {
            fila.mes: fila
            for fila in grilla_hc(
                entrada.perfiles, meses, ajustes=entrada.ajustes
            )
        }
        limite = limite_actividad(registro)
        bolsa = bolsa_de(registro)

        detalles: list[DetalleRegistroMes] = []
        for mes in meses:
            horas = resolutor.horas(mes)
            probabilidad = resolutor.probabilidad(registro, mes)
            confiabilidad = resolutor.confiabilidad(registro, mes)
            computable = mes_en_calculo(registro, mes) and bolsa is not None

            detalle_base = detallar_base(
                entrada.perfiles,
                entrada.tarifas,
                horas,
                mes,
                limite=limite,
                estricto=self.estricto,
            )
            base_clp = detalle_base.total_clp

            if not computable:
                detalles.append(
                    DetalleRegistroMes(
                        registro_id=registro.id,
                        codigo=registro.codigo,
                        mes=mes,
                        bolsa=None,
                        base_clp=0,
                        probabilidad_bp=probabilidad,
                        confiabilidad_bp=confiabilidad,
                        mab_clp=0,
                        backlog_clp=0,
                        forecast_clp=0,
                        ingreso_potencial_clp=0,
                        hc=0,
                        componentes=detalle_base.componentes,
                        advertencias=detalle_base.advertencias,
                        excluido=True,
                    )
                )
                continue

            mab_clp = 0
            backlog_clp = 0
            ingreso_potencial_clp = 0
            if bolsa is Bucket.MAB:
                mab_clp = calcular_mab(base_clp, probabilidad, confiabilidad)
                ingreso_potencial_clp = base_clp
            else:  # BACKLOG_CONTRACTUAL
                backlog_clp = calcular_backlog(
                    registro, entrada.contrato, base_clp, mes, limite=limite
                )
                ingreso_potencial_clp = backlog_clp

            if bolsa is Bucket.BACKLOG_CONTRACTUAL and not entrada.perfiles:
                hc = entrada.contrato.hc_comprometido if entrada.contrato else 0
            else:
                hc = grilla[mes].cierre

            detalles.append(
                DetalleRegistroMes(
                    registro_id=registro.id,
                    codigo=registro.codigo,
                    mes=mes,
                    bolsa=bolsa,
                    base_clp=base_clp,
                    probabilidad_bp=probabilidad,
                    confiabilidad_bp=confiabilidad,
                    mab_clp=mab_clp,
                    backlog_clp=backlog_clp,
                    forecast_clp=backlog_clp + mab_clp,
                    ingreso_potencial_clp=ingreso_potencial_clp,
                    hc=hc,
                    componentes=detalle_base.componentes,
                    advertencias=detalle_base.advertencias,
                    backlog_confirmado=es_backlog_confirmado(registro, probabilidad),
                )
            )

        return ResultadoRegistro(registro=registro, meses=tuple(detalles))

    # -- Proyección -------------------------------------------------------
    def calcular_proyeccion(
        self,
        entradas: Iterable[EntradaCalculo],
        periodo: Period,
        cantidad_meses: int = 12,
        resolutor: ResolutorVigencias | None = None,
        parametros: Sequence[Parametro] = (),
    ) -> ResultadoProyeccion:
        meses = Period.serie(periodo, cantidad_meses)
        acumulado: dict[Period, dict[str, int | Decimal]] = {
            mes: {"base": 0, "mab": 0, "backlog": 0, "forecast": 0, "potencial": 0, "hc": 0}
            for mes in meses
        }
        detalles: list[DetalleRegistroMes] = []
        advertencias: list[str] = []

        for entrada in entradas:
            resolutor_registro = resolutor or ResolutorVigencias(
                entrada.vigencias, parametros
            )
            resultado = self.calcular_registro(entrada, meses, resolutor_registro)
            detalles.extend(resultado.meses)
            for detalle in resultado.meses:
                fila = acumulado[detalle.mes]
                fila["base"] += detalle.base_clp
                fila["mab"] += detalle.mab_clp
                fila["backlog"] += detalle.backlog_clp
                fila["forecast"] += detalle.forecast_clp
                fila["potencial"] += detalle.ingreso_potencial_clp
                fila["hc"] += detalle.hc
                for advertencia in detalle.advertencias:
                    advertencias.append(f"{detalle.codigo}: {advertencia}")

        serie = tuple(
            SerieMes(
                mes=mes,
                base_clp=int(acumulado[mes]["base"]),
                mab_clp=int(acumulado[mes]["mab"]),
                backlog_clp=int(acumulado[mes]["backlog"]),
                forecast_clp=int(acumulado[mes]["forecast"]),
                ingreso_potencial_clp=int(acumulado[mes]["potencial"]),
                hc=int(acumulado[mes]["hc"]),
            )
            for mes in meses
        )
        totales = TotalesSerie(
            base_clp=sum(fila.base_clp for fila in serie),
            mab_clp=sum(fila.mab_clp for fila in serie),
            backlog_clp=sum(fila.backlog_clp for fila in serie),
            forecast_clp=sum(fila.forecast_clp for fila in serie),
            ingreso_potencial_clp=sum(fila.ingreso_potencial_clp for fila in serie),
        )
        return ResultadoProyeccion(
            periodo=periodo,
            meses=serie,
            detalles=tuple(detalles),
            totales=totales,
            advertencias=tuple(dict.fromkeys(advertencias)),
        )


def comparar_impacto(antes: ResultadoRegistro, despues: ResultadoRegistro) -> ImpactoCalculo:
    """Impacto en MAB y Forecast de dos versiones del mismo registro (T077)."""
    return ImpactoCalculo(
        mab_antes=antes.total_mab(),
        mab_despues=despues.total_mab(),
        forecast_antes=antes.total_forecast(),
        forecast_despues=despues.total_forecast(),
    )


def clonar_entrada(entrada: EntradaCalculo, **cambios: object) -> EntradaCalculo:
    """Copia superficial segura para simulación; nunca toca el repositorio."""
    return replace(entrada, **cambios)  # type: ignore[arg-type]


__all__ = [
    "FORMULA_BACKLOG",
    "FORMULA_BASE",
    "FORMULA_FORECAST",
    "FORMULA_MAB",
    "VERSION_MOTOR",
    "ComponenteBase",
    "DetalleRegistroMes",
    "ImpactoCalculo",
    "MotorCalculo",
    "ResultadoProyeccion",
    "ResultadoRegistro",
    "SerieMes",
    "TotalesSerie",
    "clonar_entrada",
    "comparar_impacto",
    "redondear_clp",
]
