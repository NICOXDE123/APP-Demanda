"""Rutas API de IA y simulación (T146, US10).

- ``GET /sugerencias``: sugerencias pendientes con su etiqueta y cita.
- ``POST /sugerencias/{id}/aceptar``: aprobación humana, auditada con origen IA.
- ``POST /sugerencias/{id}/descartar``: descarte humano.
- ``POST /simulaciones``: escenario aislado y rotulado como ``simulado``.

Ninguna ruta escribe cambios autónomos de IA ni persiste simulaciones.
"""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from proyecta.application.use_cases.ia import (
    AceptarSugerencia,
    DescartarSugerencia,
    GenerarSugerencias,
)
from proyecta.application.use_cases.simulacion import EscenarioSimulacion, SimularEscenario
from proyecta.domain.entities import SugerenciaIA
from proyecta.domain.errors import ErrorDominio
from proyecta.domain.value_objects import Period

router = APIRouter(tags=["IA", "Simulacion"])


def obtener_generador() -> GenerarSugerencias:  # pragma: no cover - wiring
    raise RuntimeError("GenerarSugerencias no configurado (wiring T034)")


def obtener_aceptador() -> AceptarSugerencia:  # pragma: no cover - wiring
    raise RuntimeError("AceptarSugerencia no configurado (wiring T034)")


def obtener_descartador() -> DescartarSugerencia:  # pragma: no cover - wiring
    raise RuntimeError("DescartarSugerencia no configurado (wiring T034)")


def obtener_simulador() -> SimularEscenario:  # pragma: no cover - wiring
    raise RuntimeError("SimularEscenario no configurado (wiring T034)")


Generador = Annotated[GenerarSugerencias, Depends(obtener_generador)]
Aceptador = Annotated[AceptarSugerencia, Depends(obtener_aceptador)]
Descartador = Annotated[DescartarSugerencia, Depends(obtener_descartador)]
Simulador = Annotated[SimularEscenario, Depends(obtener_simulador)]


class AprobacionRequest(BaseModel):
    revisor_id: UUID


class SimulacionRequest(BaseModel):
    """Esquema de ``contracts/openapi.yaml`` para ``/simulaciones``."""

    periodo: str = Field(pattern=r"^[0-9]{4}-(0[1-9]|1[0-2])$")
    probabilidad: float | None = Field(default=None, ge=0, le=1)
    confiabilidad: float | None = Field(default=None, ge=0, le=1)
    horas_mensuales: int | None = Field(default=None, ge=1)
    excluir_registro_ids: list[UUID] = Field(default_factory=list)


def serializar_sugerencia(sugerencia: SugerenciaIA) -> dict:
    return {
        "id": str(sugerencia.id),
        "registro_id": str(sugerencia.registro_id) if sugerencia.registro_id else None,
        "campo": sugerencia.campo,
        "valor_sugerido": {sugerencia.campo: sugerencia.valor_sugerido},
        "cita_bitacora_id": (
            str(sugerencia.cita_bitacora_id) if sugerencia.cita_bitacora_id else None
        ),
        "estado": sugerencia.estado.value,
        "revisor_id": str(sugerencia.revisor_id) if sugerencia.revisor_id else None,
        "version_prompt": sugerencia.version_prompt,
        "etiqueta": sugerencia.etiqueta.value,
        "justificacion": sugerencia.justificacion,
    }


@router.get("/sugerencias", response_model=None)
def listar_sugerencias(generador: Generador, registro_id: UUID | None = None) -> list[dict]:
    """Sugerencias pendientes; con ``registro_id`` genera las que falten."""
    if registro_id is not None:
        try:
            return [serializar_sugerencia(item) for item in generador.ejecutar(registro_id)]
        except ErrorDominio as error:
            raise HTTPException(
                status_code=error.status_sugerido, detail=error.a_dict()
            ) from error
    repositorio = getattr(generador, "sugerencias", None)
    if repositorio is None:  # pragma: no cover - wiring incompleto
        return []
    return [serializar_sugerencia(item) for item in repositorio.listar_pendientes()]


@router.post("/sugerencias/{sugerencia_id}/aceptar", response_model=None)
def aceptar_sugerencia(
    sugerencia_id: UUID, cuerpo: AprobacionRequest, aceptador: Aceptador
) -> dict:
    try:
        sugerencia = aceptador.ejecutar(sugerencia_id, cuerpo.revisor_id)
    except ErrorDominio as error:
        raise HTTPException(status_code=error.status_sugerido, detail=error.a_dict()) from error
    return serializar_sugerencia(sugerencia)


@router.post("/sugerencias/{sugerencia_id}/descartar", response_model=None)
def descartar_sugerencia(
    sugerencia_id: UUID, cuerpo: AprobacionRequest, descartador: Descartador
) -> dict:
    try:
        sugerencia = descartador.ejecutar(sugerencia_id, cuerpo.revisor_id)
    except ErrorDominio as error:
        raise HTTPException(status_code=error.status_sugerido, detail=error.a_dict()) from error
    return serializar_sugerencia(sugerencia)


@router.post("/simulaciones", response_model=None)
def simular(cuerpo: SimulacionRequest, simulador: Simulador) -> dict:
    escenario = EscenarioSimulacion(
        periodo=Period.desde_texto(cuerpo.periodo),
        probabilidad=cuerpo.probabilidad,
        confiabilidad=cuerpo.confiabilidad,
        horas_mensuales=cuerpo.horas_mensuales,
        excluir_registro_ids=frozenset(cuerpo.excluir_registro_ids),
    )
    try:
        resultado = simulador.ejecutar(escenario)
    except ErrorDominio as error:
        raise HTTPException(status_code=error.status_sugerido, detail=error.a_dict()) from error
    cuerpo_resultado = resultado.a_dict()
    return {
        "etiqueta": "simulado",
        "periodo": cuerpo_resultado["periodo"],
        "meses": cuerpo_resultado["serie"],
        "totales": cuerpo_resultado["totales"],
        "simulado": True,
    }


__all__ = ["router", "serializar_sugerencia"]
