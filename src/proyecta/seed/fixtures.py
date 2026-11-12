"""Fixture de cuatro registros con inconsistencias deliberadas (T152, AC-14).

La plantilla real no se migra en el MVP (``H-05``, ``S-11``): estos cuatro
registros son sintéticos y cada uno expone un caso que el cargador debe
**reportar sin corregir en silencio** (FR-088).

Los códigos de inconsistencia son estables y los consume
``tests/integration/test_seed.py``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any
from uuid import NAMESPACE_DNS, UUID, uuid5

from proyecta.domain.entities import (
    AjusteHC,
    EntradaCalculo,
    Perfil,
    Registro,
    TarifaPerfil,
)
from proyecta.domain.enums import (
    Estado,
    Flujo,
    Modalidad,
    MotivoCierre,
    Rol,
    Tipo,
    TipoAjuste,
)
from proyecta.domain.value_objects import Period
from proyecta.seed.synthetic import DatosSemilla, datos_base, serializar_semilla

PERIODO_FIXTURE = Period(2026, 1)
"""Mes con el que se recalculan los cuatro registros."""

HORAS_MENSUALES = 180
"""Valor vigente usado por el recálculo (``S-01``)."""

# Códigos estables que el cargador debe reportar por fila.
PROBABILIDAD_FUERA_CATALOGO = "PROBABILIDAD_FUERA_CATALOGO"
ESTADO_TIPO_INCOHERENTE = "ESTADO_TIPO_INCOHERENTE"
REGISTRO_CERRADO_CON_HC = "REGISTRO_CERRADO_CON_HC"
FECHA_FUTURA = "FECHA_FUTURA"


def _id(*partes: object) -> UUID:
    return uuid5(NAMESPACE_DNS, "proyecta/fixture/" + "/".join(map(str, partes)))


@dataclass(frozen=True, slots=True)
class InconsistenciaEsperada:
    """Inconsistencia que el fixture provoca a propósito."""

    fila: int
    codigo: str
    campo: str
    descripcion: str


@dataclass(slots=True)
class FixtureCarga:
    """Cuatro registros sintéticos con sus hijas y el resultado esperado."""

    datos: DatosSemilla
    inconsistencias_esperadas: tuple[InconsistenciaEsperada, ...] = field(
        default_factory=tuple
    )
    periodo: Period = PERIODO_FIXTURE
    horas_mensuales: int = HORAS_MENSUALES

    def entradas(self) -> list[EntradaCalculo]:
        return list(self.datos.entradas())

    @property
    def codigos(self) -> tuple[str, ...]:
        return tuple(registro.codigo for registro in self.datos.registros)


def cargar_fixture() -> FixtureCarga:
    """Construye los cuatro registros y sus dependencias de forma determinista."""
    base = datos_base()
    operaciones = next(
        usuario for usuario in base.usuarios if usuario.rol is Rol.OPERACIONES
    )
    ingresos = date(2025, 11, 3)

    registros = [
        # Fila 1: cerrada por pérdida, pero con HC todavía activo.
        Registro(
            id=_id("registro", 1),
            codigo="OPD-9001",
            id_externo="MANA-09001",
            tipo=Tipo.DEMANDA,
            estado=Estado.CERRADA,
            flujo=Flujo.PROPUESTA_ENTREGADA,
            probabilidad_bp=5_000,
            confiabilidad_bp=9_000,
            motivo_cierre=MotivoCierre.PERDIDA,
            fecha_creacion=ingresos,
            fecha_adjudicacion=date(2025, 12, 1),
            fecha_ingreso=ingresos,
            fecha_cierre=date(2026, 1, 10),
            owner_id=operaciones.id,
            servicio_proyecto="Fábrica de software",
            modalidad=Modalidad.NTT,
        ),
        # Fila 2: probabilidad que no pertenece al catálogo vigente.
        Registro(
            id=_id("registro", 2),
            codigo="OPD-9002",
            id_externo="MANA-09002",
            tipo=Tipo.DEMANDA,
            estado=Estado.ADJUDICADA,
            flujo=Flujo.VALIDANDO_CANDIDATOS,
            probabilidad_bp=3_333,
            confiabilidad_bp=9_000,
            fecha_creacion=ingresos,
            fecha_adjudicacion=date(2026, 1, 2),
            fecha_ingreso=ingresos,
            owner_id=operaciones.id,
            servicio_proyecto="Data platform",
            modalidad=Modalidad.NTT,
        ),
        # Fila 3: fecha de ingreso en el futuro respecto del período cargado.
        Registro(
            id=_id("registro", 3),
            codigo="OPD-9003",
            id_externo="MANA-09003",
            tipo=Tipo.OPORTUNIDAD,
            estado=Estado.PENDIENTE,
            flujo=Flujo.PENDIENTE_RFP,
            probabilidad_bp=1_000,
            confiabilidad_bp=9_000,
            fecha_creacion=ingresos,
            fecha_ingreso=date(2027, 6, 1),
            owner_id=operaciones.id,
            servicio_proyecto="Cloud migration",
            modalidad=Modalidad.SUBCONTRATACION,
        ),
        # Fila 4: estado que no existe para el tipo Oportunidad.
        Registro(
            id=_id("registro", 4),
            codigo="OPD-9004",
            id_externo="MANA-09004",
            tipo=Tipo.OPORTUNIDAD,
            estado=Estado.ADJUDICADA,
            flujo=Flujo.PROPUESTA_ENTREGADA,
            probabilidad_bp=5_000,
            confiabilidad_bp=9_000,
            fecha_creacion=ingresos,
            fecha_adjudicacion=date(2026, 1, 5),
            fecha_ingreso=ingresos,
            owner_id=operaciones.id,
            servicio_proyecto="QA continuo",
            modalidad=Modalidad.NTT,
        ),
    ]

    perfiles: list[Perfil] = []
    tarifas: list[TarifaPerfil] = []
    for registro in registros:
        perfil = Perfil(
            id=_id("perfil", registro.codigo),
            registro_id=registro.id,
            hc=2,
            dedicacion_pct=100,
            fecha_ingreso=registro.fecha_ingreso or ingresos,
            orden=1,
        )
        perfiles.append(perfil)
        tarifas.append(
            TarifaPerfil(
                id=_id("tarifa", registro.codigo),
                perfil_id=perfil.id,
                tarifa_hora_centavos=250_000,
                vigente_desde=date(2026, 1, 1),
                motivo_cambio="Tarifa sintética del fixture",
            )
        )

    ajustes = [
        AjusteHC(
            id=_id("ajuste", 1),
            registro_id=registros[1].id,
            mes=PERIODO_FIXTURE.inicio,
            tipo=TipoAjuste.ALTA,
            cantidad=1,
            motivo="Alta sintética de dotación",
            usuario_id=operaciones.id,
        )
    ]

    datos = DatosSemilla(
        usuarios=base.usuarios,
        catalogos=base.catalogos,
        parametros=base.parametros,
        registros=registros,
        perfiles=perfiles,
        tarifas=tarifas,
        ajustes=ajustes,
    )

    esperadas = (
        InconsistenciaEsperada(
            fila=1,
            codigo=REGISTRO_CERRADO_CON_HC,
            campo="estado",
            descripcion="Registro cerrado con HC activo; se marca para revisión",
        ),
        InconsistenciaEsperada(
            fila=2,
            codigo=PROBABILIDAD_FUERA_CATALOGO,
            campo="probabilidad_bp",
            descripcion="Probabilidad fuera del catálogo; se conserva y se reporta",
        ),
        InconsistenciaEsperada(
            fila=3,
            codigo=FECHA_FUTURA,
            campo="fecha_ingreso",
            descripcion="Fecha de ingreso posterior al período cargado",
        ),
        InconsistenciaEsperada(
            fila=4,
            codigo=ESTADO_TIPO_INCOHERENTE,
            campo="estado",
            descripcion="Estado que no pertenece al tipo Oportunidad",
        ),
    )

    return FixtureCarga(datos=datos, inconsistencias_esperadas=esperadas)


def serializar_fixture(fixture: FixtureCarga) -> dict[str, Any]:
    """JSON serializable del fixture, con las inconsistencias esperadas."""
    cuerpo = serializar_semilla(fixture.datos)
    cuerpo["fixture"] = "four-records"
    cuerpo["periodo"] = str(fixture.periodo)
    cuerpo["horas_mensuales"] = fixture.horas_mensuales
    cuerpo["inconsistencias_esperadas"] = [
        {
            "fila": esperada.fila,
            "codigo": esperada.codigo,
            "campo": esperada.campo,
            "descripcion": esperada.descripcion,
        }
        for esperada in fixture.inconsistencias_esperadas
    ]
    return cuerpo


__all__ = [
    "ESTADO_TIPO_INCOHERENTE",
    "FECHA_FUTURA",
    "FixtureCarga",
    "HORAS_MENSUALES",
    "InconsistenciaEsperada",
    "PERIODO_FIXTURE",
    "PROBABILIDAD_FUERA_CATALOGO",
    "REGISTRO_CERRADO_CON_HC",
    "cargar_fixture",
    "serializar_fixture",
]
