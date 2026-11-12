"""Resolución de vigencias de P, C y horas por mes (T073, RN-37, RN-52, S-01).

Un cambio de probabilidad, confiabilidad u horas aplica desde el mes de su
fecha efectiva y no reescribe meses anteriores. El motor consulta aquí, nunca
una constante escondida.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Iterable, Mapping, Sequence
from uuid import UUID

from proyecta.domain.entities import Parametro, Registro, VigenciaEstadoCalculo
from proyecta.domain.enums import HORAS_MENSUALES_DEFECTO, CampoVigencia
from proyecta.domain.errors import ErrorConfiguracion
from proyecta.domain.value_objects import Period

CLAVE_HORAS = "horas_mensuales"


def resolver_valor_vigente(
    vigencias: Iterable[VigenciaEstadoCalculo],
    campo: CampoVigencia,
    registro_id: UUID,
    mes: Period,
    por_defecto_bp: int,
) -> int:
    """Valor del campo vigente en el mes; si no hay historia, usa el actual."""
    aplicables = [
        vigencia
        for vigencia in vigencias
        if vigencia.campo is campo
        and vigencia.registro_id == registro_id
        and vigencia.vigente_desde <= mes.inicio
    ]
    if not aplicables:
        return por_defecto_bp
    # Empate en el mismo mes: gana el último registrado (dos cambios en un mes).
    return max(aplicables, key=lambda vigencia: (vigencia.vigente_desde, vigencia.creado_en)).valor_bp


def resolver_horas(
    parametros: Iterable[Parametro],
    mes: Period,
    por_defecto: int | Decimal = HORAS_MENSUALES_DEFECTO,
) -> Decimal:
    """Horas mensuales vigentes; el valor inicial es 180 (S-01)."""
    aplicables = [
        parametro
        for parametro in parametros
        if parametro.clave == CLAVE_HORAS
        and parametro.vigente_desde <= mes.inicio
        and (parametro.vigente_hasta is None or parametro.vigente_hasta >= mes.inicio)
    ]
    if not aplicables:
        return Decimal(por_defecto)
    vigente = max(aplicables, key=lambda parametro: (parametro.vigente_desde, parametro.creado_en))
    try:
        valor = Decimal(str(vigente.valor))
    except Exception as exc:  # pragma: no cover - dato corrupto
        raise ErrorConfiguracion(
            "CONFIGURACION_INVALIDA",
            f"El parámetro {CLAVE_HORAS} no es numérico",
            detalle={"valor": vigente.valor},
        ) from exc
    if valor <= 0:
        raise ErrorConfiguracion(
            "CONFIGURACION_INVALIDA", "Las horas mensuales deben ser mayores que cero"
        )
    return valor


@dataclass
class ResolutorVigencias:
    """Resuelve P, C y horas para un conjunto de registros y meses."""

    vigencias: Sequence[VigenciaEstadoCalculo] = ()
    parametros: Sequence[Parametro] = ()
    horas_por_defecto: Decimal = Decimal(HORAS_MENSUALES_DEFECTO)
    _cache_horas: dict[Period, Decimal] = field(default_factory=dict, init=False, repr=False)

    def horas(self, mes: Period) -> Decimal:
        if mes not in self._cache_horas:
            self._cache_horas[mes] = resolver_horas(
                self.parametros, mes, self.horas_por_defecto
            )
        return self._cache_horas[mes]

    def horas_por_mes(self, meses: Iterable[Period]) -> dict[Period, Decimal]:
        return {mes: self.horas(mes) for mes in meses}

    def probabilidad(self, registro: Registro, mes: Period) -> int:
        return resolver_valor_vigente(
            self.vigencias,
            CampoVigencia.PROBABILIDAD,
            registro.id,
            mes,
            registro.probabilidad_bp,
        )

    def confiabilidad(self, registro: Registro, mes: Period) -> int:
        return resolver_valor_vigente(
            self.vigencias,
            CampoVigencia.CONFIABILIDAD,
            registro.id,
            mes,
            registro.confiabilidad_bp,
        )

    def por_registro(
        self, registro_id: UUID
    ) -> Mapping[CampoVigencia, Sequence[VigenciaEstadoCalculo]]:
        resultado: dict[CampoVigencia, list[VigenciaEstadoCalculo]] = {
            CampoVigencia.PROBABILIDAD: [],
            CampoVigencia.CONFIABILIDAD: [],
        }
        for vigencia in self.vigencias:
            if vigencia.registro_id == registro_id:
                resultado[vigencia.campo].append(vigencia)
        return resultado


__all__ = [
    "CLAVE_HORAS",
    "ResolutorVigencias",
    "resolver_horas",
    "resolver_valor_vigente",
]
