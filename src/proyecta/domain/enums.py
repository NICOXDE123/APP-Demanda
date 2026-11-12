"""Enumeraciones del dominio de Proyecta (T012).

Los valores persistidos son los códigos en mayúsculas definidos en
``specs/001-proyecta-mvp/data-model.md`` y en ``docs/fuentes/requerimientos.md`` §8.
Los catálogos abiertos (sectores, clientes, perfiles, tecnologías) no viven aquí:
se administran en la entidad ``Catalogo``.
"""

from __future__ import annotations

from enum import Enum


class Tipo(str, Enum):
    """Tipo de negocio registrado (§8.1)."""

    OPORTUNIDAD = "OPORTUNIDAD"
    DEMANDA = "DEMANDA"
    CONTINUIDAD = "CONTINUIDAD"


class Estado(str, Enum):
    """Estado del ciclo de vida de un registro (§8.2)."""

    PENDIENTE = "PENDIENTE"
    ADJUDICADA = "ADJUDICADA"
    EN_CURSO = "EN_CURSO"
    STANDBY = "STANDBY"
    CERRADA = "CERRADA"
    CANCELADA = "CANCELADA"


class Flujo(str, Enum):
    """Etapa comercial del registro (§8.3)."""

    PENDIENTE_RFP = "PENDIENTE_RFP"
    PROPUESTA_EN_CURSO = "PROPUESTA_EN_CURSO"
    PROPUESTA_ENTREGADA = "PROPUESTA_ENTREGADA"
    PENDIENTE_CANDIDATOS = "PENDIENTE_CANDIDATOS"
    VALIDANDO_CANDIDATOS = "VALIDANDO_CANDIDATOS"
    PERFILES_SELECCIONADOS = "PERFILES_SELECCIONADOS"

    @property
    def orden(self) -> int:
        """Orden 1–6 usado por las reglas de estados y probabilidad."""
        return _ORDEN_FLUJO[self]


_ORDEN_FLUJO: dict[Flujo, int] = {
    Flujo.PENDIENTE_RFP: 1,
    Flujo.PROPUESTA_EN_CURSO: 2,
    Flujo.PROPUESTA_ENTREGADA: 3,
    Flujo.PENDIENTE_CANDIDATOS: 4,
    Flujo.VALIDANDO_CANDIDATOS: 5,
    Flujo.PERFILES_SELECCIONADOS: 6,
}


class Rol(str, Enum):
    LIDER = "LIDER"
    OPERACIONES = "OPERACIONES"
    EJECUTIVO = "EJECUTIVO"


class Modalidad(str, Enum):
    NTT = "NTT"
    SUBCONTRATACION = "SUBCONTRATACION"


class Origen(str, Enum):
    """Origen de un cambio auditado (§7.7)."""

    INTERFAZ = "INTERFAZ"
    CARGA = "CARGA"
    IA = "IA"
    MIGRACION = "MIGRACION"
    OTRA_INTEGRACION = "OTRA_INTEGRACION"


class Bucket(str, Enum):
    """Bolsa exclusiva de un registro-mes (§10.4, RN-83)."""

    BACKLOG_CONTRACTUAL = "BACKLOG_CONTRACTUAL"
    MAB = "MAB"


class EntidadAuditoria(str, Enum):
    REGISTRO = "REGISTRO"
    PERFIL = "PERFIL"
    TARIFA = "TARIFA"
    CONTRATO = "CONTRATO"
    META = "META"
    PARAMETRO = "PARAMETRO"
    USUARIO = "USUARIO"


class CampoVigencia(str, Enum):
    PROBABILIDAD = "PROBABILIDAD"
    CONFIABILIDAD = "CONFIABILIDAD"


class TipoAjuste(str, Enum):
    ALTA = "ALTA"
    BAJA = "BAJA"


class TipoEventoBitacora(str, Enum):
    SEGUIMIENTO = "SEGUIMIENTO"
    DECISION = "DECISION"
    REUNION = "REUNION"
    ESTADO = "ESTADO"
    INCIDENCIA = "INCIDENCIA"
    MIGRACION = "MIGRACION"


class TipoParametro(str, Enum):
    ENTERO = "ENTERO"
    DECIMAL = "DECIMAL"
    TEXTO = "TEXTO"


class TipoCatalogo(str, Enum):
    SECTOR = "SECTOR"
    CLIENTE = "CLIENTE"
    MANAGER = "MANAGER"
    PERFIL = "PERFIL"
    TECNOLOGIA = "TECNOLOGIA"
    STUDIO_PRACTICA = "STUDIO_PRACTICA"
    MOTIVO_CIERRE = "MOTIVO_CIERRE"
    ALIAS = "ALIAS"


class EstadoCorte(str, Enum):
    CREANDO = "CREANDO"
    CERRADO = "CERRADO"
    ERROR = "ERROR"


class EstadoSugerencia(str, Enum):
    PENDIENTE = "PENDIENTE"
    ACEPTADA = "ACEPTADA"
    DESCARTADA = "DESCARTADA"


class EstadoContrato(str, Enum):
    VIGENTE = "VIGENTE"
    POR_VENCER = "POR_VENCER"
    VENCIDO = "VENCIDO"


class MotivoCierre(str, Enum):
    """Motivos de cierre y su efecto en el cálculo (§8.5)."""

    PERDIDA = "PERDIDA"
    DESESTIMADA = "DESESTIMADA"
    CANCELADA_CLIENTE = "CANCELADA_CLIENTE"
    TERMINO_SERVICIO = "TERMINO_SERVICIO"
    DUPLICADO = "DUPLICADO"


class EtiquetaIA(str, Enum):
    """Clasificación obligatoria de toda salida asistida por IA (FR-083)."""

    DATO_VERIFICADO = "DATO_VERIFICADO"
    CALCULO_SISTEMA = "CALCULO_SISTEMA"
    ESTIMACION = "ESTIMACION"
    DATOS_INSUFICIENTES = "DATOS_INSUFICIENTES"


# --- Constantes de negocio reutilizables -------------------------------------

BP_TOTAL = 10_000
"""Puntos base que representan el 100 %."""

HORAS_MENSUALES_DEFECTO = 180
"""Horas mensuales iniciales; es un parámetro con vigencia (S-01)."""

CONFIABILIDAD_INICIAL_BP = 9_000
CONFIABILIDAD_CONTINUIDAD_BP = 10_000

MAX_INTENTOS_AUTENTICACION = 5
DIAS_AVISO_CONTRATO = (90, 60, 30)

PROBABILIDADES_VALIDAS_BP = frozenset(
    {500, 1_000, 1_200, 2_000, 2_500, 3_000, 5_000, 7_500, 8_000, 9_000, 9_500, 10_000}
)
"""Valores del catálogo de probabilidad; los históricos se conservan (RN-14)."""

PROBABILIDAD_SUGERIDA_POR_FLUJO_BP: dict[Flujo, int] = {
    Flujo.PENDIENTE_RFP: 1_000,
    Flujo.PROPUESTA_EN_CURSO: 2_500,
    Flujo.PROPUESTA_ENTREGADA: 5_000,
    Flujo.PENDIENTE_CANDIDATOS: 5_000,
    Flujo.VALIDANDO_CANDIDATOS: 7_500,
    Flujo.PERFILES_SELECCIONADOS: 10_000,
}

ESTADOS_POR_TIPO: dict[Tipo, frozenset[Estado]] = {
    Tipo.OPORTUNIDAD: frozenset(
        {Estado.PENDIENTE, Estado.STANDBY, Estado.CERRADA, Estado.CANCELADA}
    ),
    Tipo.DEMANDA: frozenset(
        {
            Estado.ADJUDICADA,
            Estado.EN_CURSO,
            Estado.STANDBY,
            Estado.CERRADA,
            Estado.CANCELADA,
        }
    ),
    Tipo.CONTINUIDAD: frozenset(
        {Estado.EN_CURSO, Estado.STANDBY, Estado.CERRADA, Estado.CANCELADA}
    ),
}

FLUJOS_POR_TIPO: dict[Tipo, frozenset[Flujo]] = {
    Tipo.OPORTUNIDAD: frozenset(
        {
            Flujo.PENDIENTE_RFP,
            Flujo.PROPUESTA_EN_CURSO,
            Flujo.PROPUESTA_ENTREGADA,
            Flujo.PENDIENTE_CANDIDATOS,
            Flujo.VALIDANDO_CANDIDATOS,
        }
    ),
    Tipo.DEMANDA: frozenset(Flujo),
    Tipo.CONTINUIDAD: frozenset({Flujo.PERFILES_SELECCIONADOS}),
}

MOTIVOS_QUE_PRORRATEAN: frozenset[MotivoCierre] = frozenset(
    {MotivoCierre.CANCELADA_CLIENTE, MotivoCierre.TERMINO_SERVICIO}
)
"""Motivos que mantienen el registro en cálculo hasta su fecha efectiva (FR-005)."""


def estado_excluido(estado: Estado) -> bool:
    """``StandBy`` no participa del cálculo; ``Cerrada`` y ``Cancelada`` dependen del motivo."""
    return estado is Estado.STANDBY
