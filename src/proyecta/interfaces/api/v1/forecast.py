"""Rutas API de Forecast y detalle de cálculo (T075, US3).

El router no calcula: delega en ``CalcularProyeccion``. El wiring concreto se
inyecta desde ``interfaces/api/v1/router.py`` (T034) mediante
``app.dependency_overrides`` o una fábrica equivalente.

Contrato: ``GET /forecast`` respeta el esquema ``Forecast`` de
``contracts/openapi.yaml`` (``periodo`` y ``meses`` con
``backlog_contractual``, ``mab``, ``forecast`` y ``hc``). El detalle por
registro se expone en ``GET /forecast/registros/{registro_id}``.
"""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from proyecta.application.use_cases.calculo import CalcularProyeccion, FiltrosProyeccion
from proyecta.domain.errors import ErrorDominio
from proyecta.domain.value_objects import Period

router = APIRouter(tags=["Dashboard"])


def obtener_calculo() -> CalcularProyeccion:  # pragma: no cover - wiring
    raise RuntimeError(
        "El caso de uso CalcularProyeccion no está configurado; "
        "inyéctalo desde el router /api/v1 (T034)."
    )


CasoCalculo = Annotated[CalcularProyeccion, Depends(obtener_calculo)]
PeriodoQuery = Annotated[
    str | None,
    Query(pattern=r"^[0-9]{4}-(0[1-9]|1[0-2])$", description="Mes inicial YYYY-MM"),
]


def _periodo(valor: str | None) -> Period | None:
    return Period.desde_texto(valor) if valor else None


@router.get("/forecast", response_model=None)
def obtener_forecast(
    caso: CasoCalculo,
    periodo: PeriodoQuery = None,
    sector_id: UUID | None = None,
    owner_id: UUID | None = None,
    meses: Annotated[int, Query(ge=1, le=36)] = 12,
) -> dict:
    """Serie de Forecast de 12 meses (3, 6 o 12 vistas)."""
    try:
        resultado = caso.ejecutar(
            periodo=_periodo(periodo),
            meses=meses,
            filtros=FiltrosProyeccion(owner_id=owner_id, sector_id=sector_id),
        )
    except ErrorDominio as error:
        raise HTTPException(status_code=error.status_sugerido, detail=error.a_dict()) from error
    cuerpo = resultado.a_dict()
    return {
        "periodo": cuerpo["periodo"],
        "meses": cuerpo["meses"],
        "serie": cuerpo["serie"],
        "totales": cuerpo["totales"],
        "version_motor": cuerpo["version_motor"],
    }


@router.get("/forecast/registros/{registro_id}", response_model=None)
def obtener_detalle_registro(
    registro_id: UUID,
    caso: CasoCalculo,
    periodo: PeriodoQuery = None,
    meses: Annotated[int, Query(ge=1, le=36)] = 12,
) -> dict:
    """Detalle de la cifra: componentes, P, C, días activos y bolsa por mes."""
    try:
        resultado = caso.calcular_registro(registro_id, _periodo(periodo), meses)
    except ErrorDominio as error:
        raise HTTPException(status_code=error.status_sugerido, detail=error.a_dict()) from error
    return {
        "registro_id": str(resultado.registro.id),
        "codigo": resultado.registro.codigo,
        "total_mab": resultado.total_mab(),
        "total_forecast": resultado.total_forecast(),
        "meses": [detalle.a_dict() for detalle in resultado.meses],
    }


__all__ = ["obtener_calculo", "router"]
