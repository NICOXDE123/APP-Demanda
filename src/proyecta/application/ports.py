"""Puertos de la capa de aplicación (T017).

El dominio y los casos de uso dependen de estos ``Protocol``, nunca de
Datastore, FastAPI ni Vertex AI. Los adaptadores concretos viven en
``infrastructure/`` y se inyectan en el arranque (T034).

Regla de contrato: un cambio de firma aquí se acuerda con todas las capas y se
refleja en ``contracts/openapi.yaml`` cuando afecta la API.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any, Protocol, Sequence, runtime_checkable
from uuid import UUID

from proyecta.domain.entities import (
    AjusteHC,
    Bitacora,
    Catalogo,
    Contrato,
    Corte,
    EventoAuditoria,
    MetaComercial,
    Parametro,
    Perfil,
    Registro,
    Sesion,
    SugerenciaIA,
    TarifaPerfil,
    Usuario,
    VigenciaEstadoCalculo,
)
from proyecta.domain.enums import CampoVigencia, EtiquetaIA, Origen


class Reloj(Protocol):
    """Fuente de tiempo inyectable para pruebas deterministas."""

    def ahora(self) -> datetime: ...

    def hoy(self) -> date: ...


class RepositorioRegistros(Protocol):
    def obtener(self, registro_id: UUID) -> Registro | None: ...

    def listar(
        self,
        *,
        owner_id: UUID | None = None,
        sector_id: UUID | None = None,
        tipos: Sequence[Any] | None = None,
        estados: Sequence[Any] | None = None,
        codigos: Sequence[str] | None = None,
        limite: int | None = None,
    ) -> Sequence[Registro]: ...

    def guardar(self, registro: Registro) -> Registro: ...


class RepositorioPerfiles(Protocol):
    def listar_por_registro(self, registro_id: UUID) -> Sequence[Perfil]: ...

    def tarifas_de(self, perfil_id: UUID) -> Sequence[TarifaPerfil]: ...

    def ajustes_de(self, registro_id: UUID) -> Sequence[AjusteHC]: ...

    def guardar(self, perfil: Perfil) -> Perfil: ...


class RepositorioContratos(Protocol):
    def obtener_por_registro(self, registro_id: UUID) -> Contrato | None: ...

    def listar(self) -> Sequence[Contrato]: ...


class RepositorioParametros(Protocol):
    def listar(self, clave: str | None = None) -> Sequence[Parametro]: ...

    def vigente(self, clave: str, mes: date) -> Parametro | None: ...


class RepositorioVigencias(Protocol):
    def listar(self, registro_id: UUID, campo: CampoVigencia | None = None) -> Sequence[
        VigenciaEstadoCalculo
    ]: ...

    def listar_todas(self) -> Sequence[VigenciaEstadoCalculo]: ...


class RepositorioMetas(Protocol):
    def obtener(self, sector_id: UUID, mes: date) -> MetaComercial | None: ...

    def listar(self, *, sector_id: UUID | None = None) -> Sequence[MetaComercial]: ...


class RepositorioBitacora(Protocol):
    """Bitácora de solo inserción: no expone actualización ni borrado."""

    def listar_por_registro(self, registro_id: UUID) -> Sequence[Bitacora]: ...

    def registrar(self, entrada: Bitacora) -> Bitacora: ...


class RepositorioAuditoria(Protocol):
    """Auditoría de solo inserción (RN-78)."""

    def listar_por_registro(self, registro_id: UUID) -> Sequence[EventoAuditoria]: ...

    def registrar(self, evento: EventoAuditoria) -> EventoAuditoria: ...


class RepositorioSugerencias(Protocol):
    def listar_pendientes(self) -> Sequence[SugerenciaIA]: ...

    def obtener(self, sugerencia_id: UUID) -> SugerenciaIA | None: ...

    def guardar(self, sugerencia: SugerenciaIA) -> SugerenciaIA: ...


class RepositorioCortes(Protocol):
    def obtener(self, corte_id: UUID) -> Corte | None: ...

    def listar(self) -> Sequence[Corte]: ...


class RepositorioUsuarios(Protocol):
    def obtener(self, usuario_id: UUID) -> Usuario | None: ...

    def por_email(self, email: str) -> Usuario | None: ...


class RepositorioSesiones(Protocol):
    def obtener(self, sesion_id: str) -> Sesion | None: ...

    def guardar(self, sesion: Sesion) -> Sesion: ...


class RepositorioCatalogos(Protocol):
    def listar(self, tipo: Any | None = None, *, activos: bool = True) -> Sequence[Catalogo]: ...


class Exportador(Protocol):
    def exportar(self, nombre: str, filas: Sequence[dict[str, Any]]) -> bytes: ...


@dataclass(frozen=True, slots=True)
class ContextoSugerencia:
    """Contexto mínimo y ya sanitizado que puede enviarse a un modelo externo.

    No contiene nombres de clientes, tarifas ni montos reales (FR-086).
    """

    registro_id: UUID
    codigo: str
    estado: str
    flujo: str
    tipo: str
    campos: dict[str, Any] = field(default_factory=dict)
    fragmentos_bitacora: tuple[str, ...] = ()
    evidencias: tuple[tuple[UUID, str], ...] = ()


@dataclass(frozen=True, slots=True)
class PropuestaIA:
    """Respuesta normalizada de un proveedor de IA."""

    campo: str
    valor_sugerido: Any
    justificacion: str
    etiqueta: EtiquetaIA = EtiquetaIA.ESTIMACION
    confianza_bp: int = 5_000
    cita_id: UUID | None = None
    version_prompt: str = ""
    proveedor: str = ""


class ProveedorIA(Protocol):
    """Adaptador opcional; su ausencia nunca bloquea el MVP (FR-084)."""

    def disponible(self) -> bool: ...

    def sugerir(self, contexto: ContextoSugerencia) -> PropuestaIA | None: ...


class PublicadorEventos(Protocol):
    """Notificación opcional para reconstruir proyecciones de lectura."""

    def publicar(self, evento: str, payload: dict[str, Any]) -> None: ...


@dataclass(frozen=True, slots=True)
class CambioAuditado:
    """Descripción de un cambio que debe auditarse con impacto en MAB/Forecast."""

    entidad: str
    entidad_id: UUID
    campo: str
    valor_anterior: Any
    valor_nuevo: Any
    usuario_id: UUID
    motivo: str | None = None
    fecha_efectiva: date | None = None
    registro_id: UUID | None = None
    origen: Origen = Origen.INTERFAZ


__all__ = [
    "CambioAuditado",
    "ContextoSugerencia",
    "Exportador",
    "PropuestaIA",
    "ProveedorIA",
    "PublicadorEventos",
    "Reloj",
    "RepositorioAuditoria",
    "RepositorioBitacora",
    "RepositorioCatalogos",
    "RepositorioContratos",
    "RepositorioCortes",
    "RepositorioMetas",
    "RepositorioParametros",
    "RepositorioPerfiles",
    "RepositorioRegistros",
    "RepositorioSesiones",
    "RepositorioSugerencias",
    "RepositorioUsuarios",
    "RepositorioVigencias",
]
