"""Ramas de validación y de error del dominio (T012–T017).

Estas pruebas cubren invariantes que el motor no ejercita en los escenarios
C-01…C-08: rangos de entidades, operaciones de value objects y ramas de error.
No modifican el motor ni los contratos; solo fijan el comportamiento esperado.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from proyecta.domain.entities import (
    AjusteHC,
    Bitacora,
    Catalogo,
    Contrato,
    EventoAuditoria,
    MetaComercial,
    Parametro,
    Perfil,
    Registro,
    ResumenMensual,
    SugerenciaIA,
    TarifaPerfil,
    Usuario,
    VigenciaEstadoCalculo,
)
from proyecta.domain.enums import (
    Estado,
    EstadoSugerencia,
    MotivoCierre,
    Rol,
    Tipo,
    TipoParametro,
    estado_excluido,
)
from proyecta.domain.errors import ErrorRango, ErrorValidacion
from proyecta.domain.value_objects import (
    DateRange,
    Money,
    Percentage,
    Period,
    redondear_clp,
)

# --- Entidades: invariantes de rango ----------------------------------------


def test_usuario_valida_intentos_y_expone_rol() -> None:
    with pytest.raises(ErrorRango, match="intentos_fallidos"):
        Usuario(nombre="Ana", intentos_fallidos=-1)

    assert Usuario(nombre="Ana", rol=Rol.OPERACIONES).es_operaciones is True
    assert Usuario(nombre="Ana", rol=Rol.EJECUTIVO).es_ejecutivo is True
    assert Usuario(nombre="Ana", rol=Rol.LIDER).es_operaciones is False


def test_registro_valida_version_y_orden_de_fechas() -> None:
    with pytest.raises(ErrorRango, match="versión"):
        Registro(version=0)

    with pytest.raises(ErrorValidacion, match="OPD-####"):
        Registro(codigo="OPD-12")

    assert Registro(codigo="OPD-0042").codigo == "OPD-0042"

    with pytest.raises(ErrorRango, match="fecha_fin_vigencia"):
        Registro(
            fecha_ingreso=date(2026, 3, 1), fecha_fin_vigencia=date(2026, 2, 1)
        )


def test_registro_terminal_y_exclusion_del_calculo() -> None:
    assert Registro(estado=Estado.EN_CURSO).es_terminal is False

    congelado = Registro(estado=Estado.STANDBY)
    assert congelado.excluido_del_calculo is True
    assert estado_excluido(Estado.STANDBY) is True

    perdido = Registro(estado=Estado.CERRADA, motivo_cierre=MotivoCierre.PERDIDA)
    assert perdido.excluido_del_calculo is True

    terminado = Registro(
        estado=Estado.CERRADA, motivo_cierre=MotivoCierre.TERMINO_SERVICIO
    )
    assert terminado.excluido_del_calculo is False


def test_perfil_tarifa_y_ajuste_validan_rangos() -> None:
    assert Perfil(hc=2, dedicacion_pct=50).dedicacion == 0.5

    with pytest.raises(ErrorRango, match="tarifa por hora"):
        TarifaPerfil(tarifa_hora_centavos=0)

    with pytest.raises(ErrorRango, match="vigencia de la tarifa"):
        TarifaPerfil(
            tarifa_hora_centavos=100,
            vigente_desde=date(2026, 2, 1),
            vigente_hasta=date(2026, 1, 1),
        )

    assert TarifaPerfil(tarifa_hora_centavos=150_000).tarifa_hora_clp == 1_500.0

    with pytest.raises(ErrorRango, match="cantidad del ajuste"):
        AjusteHC(cantidad=0)

    with pytest.raises(ErrorRango, match="primer día del mes"):
        AjusteHC(mes=date(2026, 1, 2))


def test_contrato_valida_indefinido_montos_y_hc() -> None:
    with pytest.raises(ErrorValidacion, match="indefinido no puede tener fecha_fin"):
        Contrato(
            fecha_inicio=date(2026, 1, 1),
            fecha_fin=date(2026, 12, 31),
            es_indefinido=True,
        )

    with pytest.raises(ErrorRango, match="monto mensual"):
        Contrato(
            fecha_inicio=date(2026, 1, 1),
            fecha_fin=date(2026, 12, 31),
            monto_mensual_clp=-1,
        )

    with pytest.raises(ErrorRango, match="HC comprometido"):
        Contrato(
            fecha_inicio=date(2026, 1, 1),
            fecha_fin=date(2026, 12, 31),
            hc_comprometido=-1,
        )


def test_vigencia_bitacora_evento_catalogo_meta_y_sugerencia_validan() -> None:
    with pytest.raises(ErrorRango, match="primer día del mes"):
        VigenciaEstadoCalculo(vigente_desde=date(2026, 1, 2))

    with pytest.raises(ErrorValidacion, match="requiere contenido"):
        Bitacora(contenido="   ")

    with pytest.raises(ErrorValidacion, match="fecha de compromiso"):
        Bitacora(contenido="Llamada", proxima_accion="Enviar propuesta")

    with pytest.raises(ErrorValidacion, match="campo auditado"):
        EventoAuditoria()

    with pytest.raises(ErrorValidacion, match="requiere código"):
        Catalogo()

    with pytest.raises(ErrorValidacion, match="requiere etiqueta"):
        Catalogo(codigo="S-01")

    with pytest.raises(ErrorRango, match="primer día del mes"):
        MetaComercial(mes=date(2026, 1, 2))

    with pytest.raises(ErrorRango, match="no puede ser negativa"):
        MetaComercial(mes=date(2026, 1, 1), monto_clp=-1)

    with pytest.raises(ErrorValidacion, match="requiere un campo"):
        SugerenciaIA()

    with pytest.raises(ErrorValidacion, match="revisor humano"):
        SugerenciaIA(campo="probabilidad", estado=EstadoSugerencia.ACEPTADA)


def test_parametro_valida_clave_vigencia_y_valor_entero() -> None:
    with pytest.raises(ErrorValidacion, match="requiere clave"):
        Parametro()

    with pytest.raises(ErrorRango, match="inicia el día 1"):
        Parametro(clave="horas_mensuales", vigente_desde=date(2026, 1, 2))

    with pytest.raises(ErrorRango, match="vigencia del parámetro"):
        Parametro(
            clave="horas_mensuales",
            vigente_desde=date(2026, 2, 1),
            vigente_hasta=date(2026, 1, 1),
        )

    assert (
        Parametro(
            clave="horas_mensuales", valor="180", vigente_desde=date(2026, 1, 1)
        ).valor_entero()
        == 180
    )

    with pytest.raises(ErrorValidacion, match="no es entero"):
        Parametro(
            clave="horas_mensuales",
            tipo=TipoParametro.TEXTO,
            vigente_desde=date(2026, 1, 1),
        ).valor_entero()

    with pytest.raises(ErrorValidacion, match="no es un entero"):
        Parametro(
            clave="horas_mensuales", valor="muchas", vigente_desde=date(2026, 1, 1)
        ).valor_entero()


def test_resumen_mensual_recalcula_su_id() -> None:
    resumen = ResumenMensual(periodo=date(2026, 3, 1), tipo=Tipo.DEMANDA)
    assert resumen.recalcular_id().startswith("2026-03:")


# --- Value objects -----------------------------------------------------------


def test_money_operaciones_y_redondeo() -> None:
    with pytest.raises(TypeError):
        redondear_clp("100")  # type: ignore[arg-type]

    assert Money.cero() == Money(0)
    assert Money(1_000).a_decimal() == Decimal(1_000)
    assert Money(1_000) - Money(300) == Money(700)
    assert Money(1_000) * 2 == Decimal(2_000)

    assert Money.desde_decimal(Decimal("10.5")) == Money(11)
    assert Money.desde_decimal(1_000.4) == Money(1_000)


def test_percentage_validaciones_y_conversiones() -> None:
    with pytest.raises(ErrorValidacion, match="puntos base"):
        Percentage(True)  # type: ignore[arg-type]

    with pytest.raises(ErrorValidacion, match="entre 0 y 100"):
        Percentage.desde_porcentaje(150)

    assert Percentage.cien().bp == 10_000
    assert Percentage(9_000).a_porcentaje() == Decimal(90)
    assert Percentage(5_000).aplicar(1_000) == Decimal(500)


def test_period_validaciones_y_comparaciones() -> None:
    with pytest.raises(ErrorValidacion, match="año"):
        Period(1899, 1)

    with pytest.raises(ErrorValidacion, match="debe ser YYYY-MM"):
        Period.desde_texto("2026")

    with pytest.raises(ErrorValidacion, match="no es válido"):
        Period.desde_texto("2026-xx")

    assert Period(2026, 1).anterior() == Period(2025, 12)

    with pytest.raises(ErrorValidacion, match="al menos un mes"):
        Period.serie(Period(2026, 1), 0)

    assert Period(2026, 1) < Period(2026, 2)
    assert Period(2026, 1) <= Period(2026, 1)


def test_daterange_sin_solape_devuelve_cero() -> None:
    rango = DateRange(date(2026, 3, 1), date(2026, 3, 31))
    assert rango.dias_solapados(Period(2026, 1)) == 0
