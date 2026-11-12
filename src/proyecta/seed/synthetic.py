"""Generador de datos sintéticos y fixtures base (T035, FR-087 a FR-090).

- Datos 100 % ficticios: clientes ``Cliente Sintético NN`` y correos
  ``@example.test``. Nunca se usan datos reales de NTT DATA (SC-012).
- Determinista: la misma semilla produce el mismo contenido, lo que permite
  reproducir demos y pruebas.
- No toca Datastore: devuelve entidades listas para que
  ``scripts/seed_synthetic.py`` o los fixtures las carguen.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Any, Iterator
from uuid import NAMESPACE_DNS, UUID, uuid5

from proyecta.domain.entities import (
    AjusteHC,
    Catalogo,
    Contrato,
    EntradaCalculo,
    MetaComercial,
    Parametro,
    Perfil,
    Registro,
    TarifaPerfil,
    Usuario,
    VigenciaEstadoCalculo,
)
from proyecta.domain.enums import (
    CampoVigencia,
    Estado,
    Flujo,
    MotivoCierre,
    Modalidad,
    Rol,
    Tipo,
    TipoAjuste,
    TipoCatalogo,
    TipoParametro,
)
from proyecta.domain.value_objects import Period

CLIENTES = tuple(f"Cliente Sintético {indice:02d}" for indice in range(1, 13))
SECTORES = (
    "Banca",
    "Seguros",
    "Sector Público",
    "Telecomunicaciones",
    "Utilities",
    "Minería y RRNN",
    "Industria",
    "Salud",
    "Producto",
    "OffShore",
    "USA",
    "Interno",
)
PERFILES = (
    "Desarrollador",
    "Desarrollador Senior",
    "QA",
    "QA Automation",
    "DevOps",
    "Data Engineer",
    "Arquitecto",
    "Analista",
    "Soporte",
    "Líder Técnico",
    "Otro",
)
TECNOLOGIAS = (
    "Java",
    "Angular",
    "React",
    "Python",
    "AWS",
    "Azure",
    "GCP",
    "DevOps",
    "Data",
    "QA",
    "SQL Server",
)
SERVICIOS = (
    "Modernización de core",
    "Fábrica de software",
    "Data platform",
    "Cloud migration",
    "QA continuo",
    "Soporte evolutivo",
    "Integración de canales",
)


def _id(*partes: object) -> UUID:
    return uuid5(NAMESPACE_DNS, "proyecta/sintetico/" + "/".join(map(str, partes)))


@dataclass(slots=True)
class DatosSemilla:
    """Conjunto coherente de entidades sintéticas."""

    usuarios: list[Usuario] = field(default_factory=list)
    catalogos: list[Catalogo] = field(default_factory=list)
    parametros: list[Parametro] = field(default_factory=list)
    registros: list[Registro] = field(default_factory=list)
    perfiles: list[Perfil] = field(default_factory=list)
    tarifas: list[TarifaPerfil] = field(default_factory=list)
    contratos: list[Contrato] = field(default_factory=list)
    ajustes: list[AjusteHC] = field(default_factory=list)
    vigencias: list[VigenciaEstadoCalculo] = field(default_factory=list)
    metas: list[MetaComercial] = field(default_factory=list)

    def por_registro(self) -> dict[UUID, list[Perfil]]:
        agrupados: dict[UUID, list[Perfil]] = {}
        for perfil in self.perfiles:
            agrupados.setdefault(perfil.registro_id, []).append(perfil)
        return agrupados

    def tarifas_por_perfil(self) -> dict[UUID, list[TarifaPerfil]]:
        agrupadas: dict[UUID, list[TarifaPerfil]] = {}
        for tarifa in self.tarifas:
            agrupadas.setdefault(tarifa.perfil_id, []).append(tarifa)
        return agrupadas

    def entradas(self) -> Iterator[EntradaCalculo]:
        perfiles = self.por_registro()
        tarifas = self.tarifas_por_perfil()
        contratos = {contrato.registro_id: contrato for contrato in self.contratos}
        ajustes: dict[UUID, list[AjusteHC]] = {}
        for ajuste in self.ajustes:
            ajustes.setdefault(ajuste.registro_id, []).append(ajuste)
        vigencias: dict[UUID, list[VigenciaEstadoCalculo]] = {}
        for vigencia in self.vigencias:
            vigencias.setdefault(vigencia.registro_id, []).append(vigencia)

        for registro in self.registros:
            propios = perfiles.get(registro.id, [])
            yield EntradaCalculo(
                registro=registro,
                perfiles=propios,
                tarifas={perfil.id: tarifas.get(perfil.id, []) for perfil in propios},
                contrato=contratos.get(registro.id),
                ajustes=ajustes.get(registro.id, []),
                vigencias=vigencias.get(registro.id, []),
            )


def datos_base() -> DatosSemilla:
    """Usuarios, catálogos y parámetros sintéticos sin registros.

    Permite que los fixtures de cuatro registros compartan el mismo catálogo
    normalizado sin generar registros aleatorios.
    """
    return DatosSemilla(
        usuarios=_usuarios(), catalogos=_catalogos(), parametros=_parametros()
    )


def _usuarios() -> list[Usuario]:
    usuarios = [
        Usuario(
            id=_id("usuario", 0),
            nombre="Operaciones Sintéticas",
            email="operaciones@example.test",
            rol=Rol.OPERACIONES,
        ),
        Usuario(
            id=_id("usuario", 1),
            nombre="Ejecutivo Sintético",
            email="ejecutivo@example.test",
            rol=Rol.EJECUTIVO,
        ),
    ]
    for indice in range(1, 4):
        usuarios.append(
            Usuario(
                id=_id("usuario", 10 + indice),
                nombre=f"Líder Sintético {indice}",
                email=f"lider{indice}@example.test",
                rol=Rol.LIDER,
                sectores=[SECTORES[indice % len(SECTORES)]],
            )
        )
    return usuarios


def _catalogos() -> list[Catalogo]:
    catalogo: list[Catalogo] = []
    for indice, etiqueta in enumerate(SECTORES):
        catalogo.append(
            Catalogo(
                id=_id("catalogo", "sector", indice),
                tipo=TipoCatalogo.SECTOR,
                codigo=f"SECTOR_{indice:02d}",
                etiqueta=etiqueta,
                orden=indice,
            )
        )
    for indice, etiqueta in enumerate(CLIENTES):
        catalogo.append(
            Catalogo(
                id=_id("catalogo", "cliente", indice),
                tipo=TipoCatalogo.CLIENTE,
                codigo=f"CLI_{indice:02d}",
                etiqueta=etiqueta,
                orden=indice,
            )
        )
    for indice in range(1, 7):
        catalogo.append(
            Catalogo(
                id=_id("catalogo", "manager", indice),
                tipo=TipoCatalogo.MANAGER,
                codigo=f"MGR_{indice:02d}",
                etiqueta=f"Manager Sintético {indice}",
                orden=indice,
            )
        )
    for indice, etiqueta in enumerate(PERFILES):
        catalogo.append(
            Catalogo(
                id=_id("catalogo", "perfil", indice),
                tipo=TipoCatalogo.PERFIL,
                codigo=f"PERFIL_{indice:02d}",
                etiqueta=etiqueta,
                orden=indice,
            )
        )
    for indice, etiqueta in enumerate(TECNOLOGIAS, start=1):
        catalogo.append(
            Catalogo(
                id=_id("catalogo", "tecnologia", indice),
                tipo=TipoCatalogo.TECNOLOGIA,
                codigo=f"TEC_{indice:02d}",
                etiqueta=etiqueta,
                orden=indice,
            )
        )
    for indice, motivo in enumerate(MotivoCierre):
        catalogo.append(
            Catalogo(
                id=_id("catalogo", "motivo", indice),
                tipo=TipoCatalogo.MOTIVO_CIERRE,
                codigo=motivo.value,
                etiqueta=motivo.value.title(),
                orden=indice,
            )
        )
    return catalogo


def _parametros() -> list[Parametro]:
    return [
        Parametro(
            id=_id("parametro", "horas"),
            clave="horas_mensuales",
            valor=180,
            tipo=TipoParametro.ENTERO,
            vigente_desde=date(2026, 1, 1),
            usuario_id=_id("usuario", 0),
        ),
        Parametro(
            id=_id("parametro", "confiabilidad"),
            clave="confiabilidad_inicial",
            valor=90,
            tipo=TipoParametro.ENTERO,
            vigente_desde=date(2026, 1, 1),
            usuario_id=_id("usuario", 0),
        ),
    ]


def _estado_y_flujo(rng: random.Random, tipo: Tipo) -> tuple[Estado, Flujo, int]:
    if tipo is Tipo.CONTINUIDAD:
        return Estado.EN_CURSO, Flujo.PERFILES_SELECCIONADOS, 10_000
    if tipo is Tipo.DEMANDA:
        flujo = rng.choice(
            (
                Flujo.PROPUESTA_ENTREGADA,
                Flujo.PENDIENTE_CANDIDATOS,
                Flujo.VALIDANDO_CANDIDATOS,
                Flujo.PERFILES_SELECCIONADOS,
            )
        )
        if flujo is Flujo.PERFILES_SELECCIONADOS:
            return Estado.EN_CURSO, flujo, 10_000
        return Estado.ADJUDICADA, flujo, 10_000
    flujo = rng.choice(
        (
            Flujo.PENDIENTE_RFP,
            Flujo.PROPUESTA_EN_CURSO,
            Flujo.PROPUESTA_ENTREGADA,
            Flujo.PENDIENTE_CANDIDATOS,
            Flujo.VALIDANDO_CANDIDATOS,
        )
    )
    probabilidades = {
        Flujo.PENDIENTE_RFP: 1_000,
        Flujo.PROPUESTA_EN_CURSO: 2_500,
        Flujo.PROPUESTA_ENTREGADA: 5_000,
        Flujo.PENDIENTE_CANDIDATOS: 5_000,
        Flujo.VALIDANDO_CANDIDATOS: 7_500,
    }
    return Estado.PENDIENTE, flujo, probabilidades[flujo]


def generar_semilla(
    cantidad_registros: int = 1_000,
    primer_mes: Period | None = None,
    meses: int = 12,
    semilla: int = 20260101,
) -> DatosSemilla:
    """Genera un conjunto determinista y coherente para demo y pruebas."""
    if cantidad_registros < 1:
        raise ValueError("cantidad_registros debe ser positiva")
    rng = random.Random(semilla)
    primer_mes = primer_mes or Period(2026, 1)
    datos = datos_base()
    sectores = [item for item in datos.catalogos if item.tipo is TipoCatalogo.SECTOR]
    clientes = [item for item in datos.catalogos if item.tipo is TipoCatalogo.CLIENTE]
    managers = [item for item in datos.catalogos if item.tipo is TipoCatalogo.MANAGER]
    perfiles_catalogo = [item for item in datos.catalogos if item.tipo is TipoCatalogo.PERFIL]
    tecnologias = [item for item in datos.catalogos if item.tipo is TipoCatalogo.TECNOLOGIA]
    lideres = [usuario for usuario in datos.usuarios if usuario.rol is Rol.LIDER]

    for indice in range(cantidad_registros):
        tipo = (
            Tipo.CONTINUIDAD
            if indice % 10 == 0
            else Tipo.DEMANDA
            if indice % 3 == 0
            else Tipo.OPORTUNIDAD
        )
        estado, flujo, probabilidad_bp = _estado_y_flujo(rng, tipo)
        sector = rng.choice(sectores)
        cliente = rng.choice(clientes)
        manager = rng.choice(managers)
        lider = rng.choice(lideres)
        creado = date(primer_mes.anio, primer_mes.mes, 1)
        ingreso = date(
            primer_mes.anio,
            primer_mes.mes,
            1 + rng.randrange(0, 20),
        )
        confiabilidad = 10_000 if tipo is Tipo.CONTINUIDAD else 9_000
        registro = Registro(
            id=_id("registro", indice),
            codigo=f"OPD-{indice + 1:04d}",
            id_externo=f"MANA-{indice + 1:05d}",
            tipo=tipo,
            estado=estado,
            flujo=flujo,
            probabilidad_bp=probabilidad_bp,
            confiabilidad_bp=confiabilidad,
            manager_id=manager.id,
            owner_id=lider.id,
            sector_id=sector.id,
            cliente_id=cliente.id,
            servicio_proyecto=rng.choice(SERVICIOS),
            modalidad=Modalidad.NTT if rng.random() < 0.8 else Modalidad.SUBCONTRATACION,
            studio=rng.random() < 0.3,
            tecnologia_back=[rng.choice(tecnologias).id],
            tecnologia_front=[rng.choice(tecnologias).id],
            fecha_creacion=creado,
            fecha_adjudicacion=(
                ingreso if estado in (Estado.ADJUDICADA, Estado.EN_CURSO) else None
            ),
            fecha_ingreso=ingreso,
            fecha_fin_vigencia=None,
            en_staffing=estado is Estado.EN_CURSO,
            en_invoicing=tipo is Tipo.CONTINUIDAD,
            creado_por=lider.id,
            actualizado_por=lider.id,
        )
        datos.registros.append(registro)

        cantidad_perfiles = (
            rng.randint(0, 3) if tipo is Tipo.OPORTUNIDAD else rng.randint(1, 3)
        )
        for orden in range(1, cantidad_perfiles + 1):
            perfil_catalogo = rng.choice(perfiles_catalogo)
            hc = rng.randint(1, 4)
            perfil = Perfil(
                id=_id("perfil", indice, orden),
                registro_id=registro.id,
                nombre_perfil_id=perfil_catalogo.id,
                hc=hc,
                dedicacion_pct=rng.choice((50, 100, 100, 100)),
                fecha_ingreso=ingreso,
                fecha_fin=None,
                orden=orden,
            )
            datos.perfiles.append(perfil)
            tarifa = TarifaPerfil(
                id=_id("tarifa", indice, orden),
                perfil_id=perfil.id,
                tarifa_hora_centavos=rng.randrange(1_800, 4_500) * 100,
                vigente_desde=ingreso,
            )
            datos.tarifas.append(tarifa)

        if tipo is Tipo.CONTINUIDAD:
            datos.contratos.append(
                Contrato(
                    registro_id=registro.id,
                    codigo_contrato=f"CTR-{indice + 1:04d}",
                    fecha_inicio=ingreso,
                    fecha_fin=date(primer_mes.anio + 1, 12, 31),
                    monto_mensual_clp=rng.randrange(20, 60) * 1_000_000,
                    hc_comprometido=sum(
                        perfil.hc for perfil in datos.perfiles if perfil.registro_id == registro.id
                    )
                    or rng.randint(2, 8),
                )
            )

        if tipo is not Tipo.CONTINUIDAD and rng.random() < 0.35:
            datos.vigencias.append(
                VigenciaEstadoCalculo(
                    id=_id("vigencia", indice),
                    registro_id=registro.id,
                    campo=CampoVigencia.CONFIABILIDAD,
                    valor_bp=8_000,
                    vigente_desde=Period(primer_mes.anio, min(12, primer_mes.mes + 3)).inicio,
                    motivo="Ajuste sintético de confiabilidad",
                    usuario_id=_id("usuario", 0),
                )
            )
        if tipo is not Tipo.CONTINUIDAD and rng.random() < 0.1:
            datos.ajustes.append(
                AjusteHC(
                    id=_id("ajuste", indice),
                    registro_id=registro.id,
                    mes=primer_mes.inicio,
                    tipo=TipoAjuste.ALTA,
                    cantidad=1,
                    motivo="Ajuste sintético de dotación",
                    usuario_id=_id("usuario", 0),
                )
            )

    for mes in Period.serie(primer_mes, meses):
        for sector in sectores:
            datos.metas.append(
                MetaComercial(
                    id=_id("meta", sector.id, mes),
                    sector_id=sector.id,
                    mes=mes.inicio,
                    monto_clp=rng.randrange(80, 220) * 1_000_000,
                    usuario_id=_id("usuario", 0),
                )
            )
    return datos


def _jsonable(valor: Any) -> Any:
    if isinstance(valor, UUID):
        return str(valor)
    if isinstance(valor, (date, datetime)):
        return valor.isoformat()
    if isinstance(valor, Decimal):
        return str(valor)
    if hasattr(valor, "value") and not isinstance(valor, (str, bytes)):
        return valor.value
    if isinstance(valor, dict):
        return {str(clave): _jsonable(item) for clave, item in valor.items()}
    if isinstance(valor, (list, tuple, set, frozenset)):
        return [_jsonable(item) for item in valor]
    return valor


def serializar_semilla(datos: DatosSemilla) -> dict[str, Any]:
    """Convierte la semilla a JSON serializable para el script de carga."""
    from dataclasses import asdict

    return {
        "generado_en": datetime.now(timezone.utc).isoformat(),
        "usuarios": _jsonable([asdict(item) for item in datos.usuarios]),
        "catalogos": _jsonable([asdict(item) for item in datos.catalogos]),
        "parametros": _jsonable([asdict(item) for item in datos.parametros]),
        "registros": _jsonable([asdict(item) for item in datos.registros]),
        "perfiles": _jsonable([asdict(item) for item in datos.perfiles]),
        "tarifas": _jsonable([asdict(item) for item in datos.tarifas]),
        "contratos": _jsonable([asdict(item) for item in datos.contratos]),
        "ajustes": _jsonable([asdict(item) for item in datos.ajustes]),
        "vigencias": _jsonable([asdict(item) for item in datos.vigencias]),
        "metas": _jsonable([asdict(item) for item in datos.metas]),
    }


__all__ = [
    "CLIENTES",
    "DatosSemilla",
    "PERFILES",
    "SECTORES",
    "TECNOLOGIAS",
    "datos_base",
    "generar_semilla",
    "serializar_semilla",
]
