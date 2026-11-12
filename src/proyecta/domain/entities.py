"""Entidades del dominio de Proyecta (T014 y T015).

Son contenedores de datos puros: no importan FastAPI, Datastore ni Jinja2 y no
contienen lógica de persistencia. Las reglas de transición viven en
``domain/states.py`` (Felipe) y las validaciones de negocio en
``domain/rules.py``; aquí solo se protegen invariantes de rango elementales.

Los montos se guardan como enteros CLP, las tarifas como enteros de centavos y
los porcentajes como puntos base (0–10.000), según ``data-model.md``.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from proyecta.domain.enums import (
    CampoVigencia,
    EntidadAuditoria,
    Estado,
    EstadoContrato,
    EstadoCorte,
    EstadoSugerencia,
    EtiquetaIA,
    Flujo,
    Modalidad,
    MotivoCierre,
    Origen,
    Rol,
    Tipo,
    TipoAjuste,
    TipoCatalogo,
    TipoEventoBitacora,
    TipoParametro,
)
from proyecta.domain.errors import ErrorRango, ErrorValidacion


def utcnow() -> datetime:
    """Marca de tiempo UTC con zona explícita."""
    return datetime.now(timezone.utc)


def _validar_bp(valor: int, campo: str) -> None:
    if isinstance(valor, bool) or not isinstance(valor, int) or not 0 <= valor <= 10_000:
        raise ErrorRango(
            "PORCENTAJE_FUERA_DE_RANGO",
            f"{campo} debe ser un entero entre 0 y 10.000 puntos base",
            detalle={"campo": campo, "valor": valor},
        )


@dataclass(slots=True)
class Usuario:
    """Persona con rol dentro del sistema."""

    id: UUID = field(default_factory=uuid4)
    nombre: str = ""
    email: str = ""
    rol: Rol = Rol.LIDER
    sectores: list[str] = field(default_factory=list)
    activo: bool = True
    password_hash: str = ""
    intentos_fallidos: int = 0
    bloqueado_hasta: datetime | None = None
    ultimo_acceso: datetime | None = None
    creado_en: datetime = field(default_factory=utcnow)
    actualizado_en: datetime = field(default_factory=utcnow)

    def __post_init__(self) -> None:
        self.email = self.email.strip().lower()
        if not self.nombre:
            raise ErrorValidacion("CAMPO_OBLIGATORIO", "El usuario requiere nombre")
        if self.intentos_fallidos < 0:
            raise ErrorRango("RANGO_INVALIDO", "intentos_fallidos no puede ser negativo")

    @property
    def es_operaciones(self) -> bool:
        return self.rol is Rol.OPERACIONES

    @property
    def es_ejecutivo(self) -> bool:
        return self.rol is Rol.EJECUTIVO


@dataclass(slots=True)
class Registro:
    """Raíz del pipeline: oportunidad, demanda o continuidad."""

    id: UUID = field(default_factory=uuid4)
    codigo: str = ""
    id_externo: str | None = None
    tipo: Tipo = Tipo.OPORTUNIDAD
    estado: Estado = Estado.PENDIENTE
    estado_previo: Estado | None = None
    flujo: Flujo = Flujo.PENDIENTE_RFP
    probabilidad_bp: int = 1_000
    confiabilidad_bp: int = 9_000
    motivo_confiabilidad: str | None = None
    manager_id: UUID | None = None
    owner_id: UUID | None = None
    sector_id: UUID | None = None
    cliente_id: UUID | None = None
    servicio_proyecto: str = ""
    modalidad: Modalidad = Modalidad.NTT
    studio: bool = False
    studio_practica_id: UUID | None = None
    cuenta: str = "No Aplica"
    tecnologia_back: list[UUID] = field(default_factory=list)
    tecnologia_front: list[UUID] = field(default_factory=list)
    fecha_creacion: date = field(default_factory=date.today)
    fecha_adjudicacion: date | None = None
    fecha_cancelacion: date | None = None
    fecha_ingreso: date | None = None
    fecha_fin_vigencia: date | None = None
    en_staffing: bool = False
    en_invoicing: bool = False
    observaciones: str | None = None
    motivo_cierre_id: UUID | None = None
    motivo_cierre: MotivoCierre | None = None
    fecha_cierre: date | None = None
    version: int = 1
    creado_por: UUID | None = None
    creado_en: datetime = field(default_factory=utcnow)
    actualizado_por: UUID | None = None
    actualizado_en: datetime = field(default_factory=utcnow)

    def __post_init__(self) -> None:
        _validar_bp(self.probabilidad_bp, "probabilidad_bp")
        _validar_bp(self.confiabilidad_bp, "confiabilidad_bp")
        if self.codigo and re.fullmatch(r"OPD-\d{4}", self.codigo) is None:
            raise ErrorValidacion(
                "VALIDACION", "El código del registro debe tener el formato OPD-####"
            )
        if self.version < 1:
            raise ErrorRango("RANGO_INVALIDO", "La versión del registro debe ser >= 1")
        if self.fecha_fin_vigencia and self.fecha_ingreso:
            if self.fecha_fin_vigencia < self.fecha_ingreso:
                raise ErrorRango(
                    "RANGO_INVALIDO", "fecha_fin_vigencia no puede ser anterior a fecha_ingreso"
                )

    @property
    def es_terminal(self) -> bool:
        return self.estado in (Estado.CERRADA, Estado.CANCELADA)

    @property
    def excluido_del_calculo(self) -> bool:
        """``StandBy`` siempre sale; los terminales dependen del motivo (FR-005)."""
        if self.estado is Estado.STANDBY:
            return True
        if not self.es_terminal:
            return False
        return self.motivo_cierre not in (
            MotivoCierre.CANCELADA_CLIENTE,
            MotivoCierre.TERMINO_SERVICIO,
        )


@dataclass(slots=True)
class Perfil:
    """Rol técnico requerido por un registro."""

    id: UUID = field(default_factory=uuid4)
    registro_id: UUID | None = None
    nombre_perfil_id: UUID | None = None
    hc: int = 1
    dedicacion_pct: int = 100
    fecha_ingreso: date = field(default_factory=date.today)
    fecha_fin: date | None = None
    orden: int = 1
    creado_en: datetime = field(default_factory=utcnow)

    def __post_init__(self) -> None:
        if not 1 <= self.hc <= 999:
            raise ErrorRango("RANGO_INVALIDO", "hc debe estar entre 1 y 999")
        if not 1 <= self.dedicacion_pct <= 100:
            raise ErrorRango("RANGO_INVALIDO", "dedicacion_pct debe estar entre 1 y 100")
        if self.fecha_fin is not None and self.fecha_fin < self.fecha_ingreso:
            raise ErrorRango("RANGO_INVALIDO", "fecha_fin no puede ser anterior a fecha_ingreso")

    @property
    def dedicacion(self) -> float:
        """Fracción de dedicación (0–1) lista para el motor."""
        return self.dedicacion_pct / 100


@dataclass(slots=True)
class TarifaPerfil:
    """Tarifa por hora de un perfil, con vigencia mensual."""

    id: UUID = field(default_factory=uuid4)
    perfil_id: UUID | None = None
    tarifa_hora_centavos: int = 0
    vigente_desde: date = field(default_factory=date.today)
    vigente_hasta: date | None = None
    motivo_cambio: str | None = None
    creado_en: datetime = field(default_factory=utcnow)

    def __post_init__(self) -> None:
        if self.tarifa_hora_centavos <= 0:
            raise ErrorRango("RANGO_INVALIDO", "La tarifa por hora debe ser mayor que cero")
        if self.vigente_hasta is not None and self.vigente_hasta < self.vigente_desde:
            raise ErrorRango("RANGO_INVALIDO", "La vigencia de la tarifa está invertida")

    @property
    def tarifa_hora_clp(self) -> float:
        """Valor en pesos para presentación; el cálculo usa centavos."""
        return self.tarifa_hora_centavos / 100


@dataclass(slots=True)
class AjusteHC:
    """Corrección manual de altas o bajas de HC."""

    id: UUID = field(default_factory=uuid4)
    registro_id: UUID | None = None
    mes: date = field(default_factory=date.today)
    tipo: TipoAjuste = TipoAjuste.ALTA
    cantidad: int = 1
    motivo: str = ""
    usuario_id: UUID | None = None
    creado_en: datetime = field(default_factory=utcnow)

    def __post_init__(self) -> None:
        if self.cantidad <= 0:
            raise ErrorRango("RANGO_INVALIDO", "La cantidad del ajuste debe ser positiva")
        if self.mes.day != 1:
            raise ErrorRango("MES_INVALIDO", "El ajuste debe usar el primer día del mes")


@dataclass(slots=True)
class Contrato:
    """Ficha 1:1 de una continuidad."""

    registro_id: UUID | None = None
    codigo_contrato: str = ""
    fecha_inicio: date = field(default_factory=date.today)
    fecha_fin: date | None = None
    es_indefinido: bool = False
    monto_mensual_clp: int | None = None
    hc_comprometido: int = 0
    renovacion_automatica: bool = False
    aviso_termino_dias: int = 90
    estado_contrato: EstadoContrato = EstadoContrato.VIGENTE
    observaciones: str | None = None

    def __post_init__(self) -> None:
        if self.fecha_fin is not None and self.fecha_fin < self.fecha_inicio:
            raise ErrorRango("RANGO_INVALIDO", "fecha_fin del contrato es anterior a fecha_inicio")
        if not self.es_indefinido and self.fecha_fin is None:
            raise ErrorValidacion(
                "CAMPO_OBLIGATORIO", "Un contrato no indefinido requiere fecha_fin"
            )
        if self.es_indefinido and self.fecha_fin is not None:
            raise ErrorValidacion(
                "RANGO_INVALIDO", "Un contrato indefinido no puede tener fecha_fin"
            )
        if self.monto_mensual_clp is not None and self.monto_mensual_clp < 0:
            raise ErrorRango("RANGO_INVALIDO", "El monto mensual no puede ser negativo")
        if self.hc_comprometido < 0:
            raise ErrorRango("RANGO_INVALIDO", "El HC comprometido no puede ser negativo")


@dataclass(slots=True)
class VigenciaEstadoCalculo:
    """Historia mensual de probabilidad o confiabilidad (RN-37)."""

    id: UUID = field(default_factory=uuid4)
    registro_id: UUID | None = None
    campo: CampoVigencia = CampoVigencia.PROBABILIDAD
    valor_bp: int = 0
    vigente_desde: date = field(default_factory=date.today)
    motivo: str = ""
    usuario_id: UUID | None = None
    creado_en: datetime = field(default_factory=utcnow)

    def __post_init__(self) -> None:
        _validar_bp(self.valor_bp, "valor_bp")
        if self.vigente_desde.day != 1:
            raise ErrorRango("MES_INVALIDO", "La vigencia debe comenzar el primer día del mes")


@dataclass(slots=True)
class Bitacora:
    """Entrada cronológica inmutable."""

    id: UUID = field(default_factory=uuid4)
    registro_id: UUID | None = None
    tipo_evento: TipoEventoBitacora = TipoEventoBitacora.SEGUIMIENTO
    contenido: str = ""
    proxima_accion: str | None = None
    fecha_compromiso: date | None = None
    referencia_id: UUID | None = None
    autor_id: UUID | None = None
    creado_en: datetime = field(default_factory=utcnow)

    def __post_init__(self) -> None:
        if not self.contenido.strip():
            raise ErrorValidacion("CAMPO_OBLIGATORIO", "La bitácora requiere contenido")
        if self.proxima_accion and self.fecha_compromiso is None:
            raise ErrorValidacion(
                "CAMPO_OBLIGATORIO", "Una próxima acción requiere fecha de compromiso"
            )


@dataclass(slots=True)
class EventoAuditoria:
    """Cambio trazable por campo; solo inserción."""

    id: UUID = field(default_factory=uuid4)
    entidad: EntidadAuditoria = EntidadAuditoria.REGISTRO
    entidad_id: UUID | None = None
    registro_id: UUID | None = None
    campo: str = ""
    valor_anterior: Any = None
    valor_nuevo: Any = None
    usuario_id: UUID | None = None
    fecha_hora: datetime = field(default_factory=utcnow)
    motivo: str | None = None
    fecha_efectiva: date | None = None
    mab_antes: int | None = None
    mab_despues: int | None = None
    forecast_antes: int | None = None
    forecast_despues: int | None = None
    origen: Origen = Origen.INTERFAZ

    def __post_init__(self) -> None:
        if not self.campo:
            raise ErrorValidacion("CAMPO_OBLIGATORIO", "El evento debe indicar el campo auditado")


@dataclass(slots=True)
class Parametro:
    """Valor configurable con vigencia (horas, confiabilidad inicial, umbrales)."""

    id: UUID = field(default_factory=uuid4)
    clave: str = ""
    valor: Any = None
    tipo: TipoParametro = TipoParametro.ENTERO
    vigente_desde: date = field(default_factory=date.today)
    vigente_hasta: date | None = None
    usuario_id: UUID | None = None
    creado_en: datetime = field(default_factory=utcnow)

    def __post_init__(self) -> None:
        if not self.clave:
            raise ErrorValidacion("CAMPO_OBLIGATORIO", "El parámetro requiere clave")
        if self.vigente_desde.day != 1:
            raise ErrorRango("MES_INVALIDO", "La vigencia del parámetro inicia el día 1")
        if self.vigente_hasta is not None and self.vigente_hasta < self.vigente_desde:
            raise ErrorRango("RANGO_INVALIDO", "La vigencia del parámetro está invertida")

    def valor_entero(self) -> int:
        if self.tipo is not TipoParametro.ENTERO:
            raise ErrorValidacion("VALOR_NUMERICO_INVALIDO", "El parámetro no es entero")
        try:
            return int(self.valor)
        except (TypeError, ValueError) as exc:
            raise ErrorValidacion(
                "VALOR_NUMERICO_INVALIDO", f"El parámetro {self.clave} no es un entero"
            ) from exc


@dataclass(slots=True)
class Catalogo:
    """Catálogo normalizado; se desactiva, nunca se borra."""

    id: UUID = field(default_factory=uuid4)
    tipo: TipoCatalogo = TipoCatalogo.SECTOR
    codigo: str = ""
    etiqueta: str = ""
    orden: int = 0
    activo: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)
    padre_id: UUID | None = None

    def __post_init__(self) -> None:
        if not self.codigo:
            raise ErrorValidacion("CAMPO_OBLIGATORIO", "El catálogo requiere código")
        if not self.etiqueta:
            raise ErrorValidacion("CAMPO_OBLIGATORIO", "El catálogo requiere etiqueta")


@dataclass(slots=True)
class MetaComercial:
    """Objetivo comercial por sector y mes (único por sector-mes)."""

    id: UUID = field(default_factory=uuid4)
    sector_id: UUID | None = None
    mes: date = field(default_factory=date.today)
    monto_clp: int = 0
    usuario_id: UUID | None = None
    creado_en: datetime = field(default_factory=utcnow)
    actualizado_en: datetime = field(default_factory=utcnow)

    def __post_init__(self) -> None:
        if self.mes.day != 1:
            raise ErrorRango("MES_INVALIDO", "La meta debe usar el primer día del mes")
        if self.monto_clp < 0:
            raise ErrorRango("RANGO_INVALIDO", "La meta no puede ser negativa")


@dataclass(slots=True)
class Corte:
    """Cierre mensual congelado."""

    id: UUID = field(default_factory=uuid4)
    fecha_corte: datetime = field(default_factory=utcnow)
    periodo_referencia: date = field(default_factory=date.today)
    responsable_id: UUID | None = None
    estado: EstadoCorte = EstadoCorte.CREANDO
    version: int = 1
    creado_en: datetime = field(default_factory=utcnow)
    cerrado_en: datetime | None = None


@dataclass(slots=True)
class CorteDetalle:
    """Valores congelados de un registro-mes dentro de un corte."""

    id: UUID = field(default_factory=uuid4)
    corte_id: UUID | None = None
    registro_id: UUID | None = None
    mes: date = field(default_factory=date.today)
    bucket: str = ""
    base_clp: int = 0
    probabilidad_bp: int = 0
    confiabilidad_bp: int = 0
    mab_clp: int = 0
    backlog_clp: int = 0
    hc: int = 0


@dataclass(slots=True)
class SugerenciaIA:
    """Sugerencia asistida, nunca aplicada automáticamente."""

    id: UUID = field(default_factory=uuid4)
    registro_id: UUID | None = None
    campo: str = ""
    valor_sugerido: Any = None
    cita_bitacora_id: UUID | None = None
    estado: EstadoSugerencia = EstadoSugerencia.PENDIENTE
    revisor_id: UUID | None = None
    version_prompt: str = ""
    creado_en: datetime = field(default_factory=utcnow)
    resuelto_en: datetime | None = None
    etiqueta: EtiquetaIA = EtiquetaIA.ESTIMACION
    justificacion: str = ""

    def __post_init__(self) -> None:
        if not self.campo:
            raise ErrorValidacion("CAMPO_OBLIGATORIO", "La sugerencia requiere un campo")
        if self.estado is EstadoSugerencia.ACEPTADA and self.revisor_id is None:
            raise ErrorValidacion(
                "CAMPO_OBLIGATORIO", "Una sugerencia aceptada requiere revisor humano"
            )


@dataclass(slots=True)
class Sesion:
    """Sesión de servidor con token CSRF."""

    id: str = ""
    usuario_id: UUID | None = None
    csrf_token: str = ""
    creado_en: datetime = field(default_factory=utcnow)
    expira_en: datetime = field(default_factory=utcnow)
    ip: str | None = None
    user_agent: str | None = None
    activa: bool = True


@dataclass(slots=True)
class ResumenMensual:
    """Proyección de lectura para el dashboard; no es fuente de verdad."""

    id: str = ""
    periodo: date = field(default_factory=date.today)
    sector_id: UUID | None = None
    owner_id: UUID | None = None
    tipo: Tipo = Tipo.OPORTUNIDAD
    estado: Estado = Estado.PENDIENTE
    base_clp: int = 0
    mab_clp: int = 0
    backlog_clp: int = 0
    hc: int = 0
    registros: int = 0
    actualizado_en: datetime = field(default_factory=utcnow)

    def recalcular_id(self) -> str:
        return (
            f"{self.periodo:%Y-%m}:{self.sector_id}:{self.owner_id}:"
            f"{self.tipo.value}:{self.estado.value}"
        )


@dataclass(slots=True)
class EntradaCalculo:
    """Agregado de cálculo: registro con sus hijas y vigencias.

    No es una entidad persistida; es el contrato de entrada del motor y del
    caso de uso de cálculo.
    """

    registro: Registro
    perfiles: list[Perfil] = field(default_factory=list)
    tarifas: dict[UUID, list[TarifaPerfil]] = field(default_factory=dict)
    contrato: Contrato | None = None
    ajustes: list[AjusteHC] = field(default_factory=list)
    vigencias: list[VigenciaEstadoCalculo] = field(default_factory=list)


__all__ = [
    "AjusteHC",
    "Bitacora",
    "Catalogo",
    "Contrato",
    "Corte",
    "CorteDetalle",
    "EntradaCalculo",
    "Estado",
    "EventoAuditoria",
    "MetaComercial",
    "Parametro",
    "Perfil",
    "Registro",
    "ResumenMensual",
    "Sesion",
    "SugerenciaIA",
    "TarifaPerfil",
    "Usuario",
    "VigenciaEstadoCalculo",
    "utcnow",
]
