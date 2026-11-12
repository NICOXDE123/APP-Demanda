"""Value objects monetarios y temporales del dominio (T013).

Reglas de representación (``data-model.md`` y §10.8):

- Dinero CLP: entero de pesos, redondeo *half-up* al final del registro-mes.
- Tarifas: entero de centavos por hora; se convierten a ``Decimal`` al calcular.
- Porcentajes: entero en puntos base (0–10.000), donde 10.000 = 100 %.
- Fechas de negocio: ``date``; un mes se representa por su primer día.
"""

from __future__ import annotations

import calendar
from dataclasses import dataclass
from datetime import date
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

from proyecta.domain.errors import ErrorValidacion

BP_TOTAL = Decimal(10_000)
CENTAVOS_POR_CLP = Decimal(100)


def redondear_clp(valor: Decimal | int) -> int:
    """Redondea a CLP entero con la regla half-up (RN-86)."""
    if isinstance(valor, int):
        return valor
    if not isinstance(valor, Decimal):
        raise TypeError("redondear_clp espera Decimal o int")
    return int(valor.quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def _decimal(valor: Decimal | int | float | str) -> Decimal:
    if isinstance(valor, Decimal):
        return valor
    if isinstance(valor, float):
        return Decimal(str(valor))
    try:
        return Decimal(valor)
    except (InvalidOperation, TypeError, ValueError) as exc:  # pragma: no cover - defensivo
        raise ErrorValidacion("VALOR_NUMERICO_INVALIDO", f"Valor no numérico: {valor!r}") from exc


@dataclass(frozen=True, slots=True)
class Money:
    """Monto en pesos chilenos enteros. Nunca usa ``float``."""

    clp: int

    def __post_init__(self) -> None:
        if isinstance(self.clp, bool) or not isinstance(self.clp, int):
            raise ErrorValidacion(
                "MONTO_INVALIDO", "Money.clp debe ser un entero de pesos chilenos"
            )

    @classmethod
    def desde_decimal(cls, valor: Decimal | int | float | str) -> "Money":
        """Crea un monto redondeando half-up al peso."""
        return cls(redondear_clp(_decimal(valor)))

    @classmethod
    def cero(cls) -> "Money":
        return cls(0)

    def a_decimal(self) -> Decimal:
        return Decimal(self.clp)

    def __add__(self, otro: "Money") -> "Money":
        return Money(self.clp + otro.clp)

    def __sub__(self, otro: "Money") -> "Money":
        return Money(self.clp - otro.clp)

    def __mul__(self, factor: Decimal | int) -> Decimal:
        return self.a_decimal() * _decimal(factor)


@dataclass(frozen=True, slots=True)
class Percentage:
    """Porcentaje en puntos base: 10.000 = 100 %."""

    bp: int

    def __post_init__(self) -> None:
        if isinstance(self.bp, bool) or not isinstance(self.bp, int):
            raise ErrorValidacion("PORCENTAJE_INVALIDO", "El porcentaje debe estar en puntos base")
        if not 0 <= self.bp <= 10_000:
            raise ErrorValidacion(
                "PORCENTAJE_FUERA_DE_RANGO",
                f"El porcentaje {self.bp} bp está fuera del rango 0–10.000",
            )

    @classmethod
    def desde_decimal(cls, valor: Decimal | int | float | str) -> "Percentage":
        """Convierte una fracción 0–1 (``0.9``) a puntos base."""
        fraccion = _decimal(valor)
        if not Decimal(0) <= fraccion <= Decimal(1):
            raise ErrorValidacion(
                "PORCENTAJE_FUERA_DE_RANGO", f"La fracción {fraccion} debe estar entre 0 y 1"
            )
        return cls(int((fraccion * BP_TOTAL).quantize(Decimal("1"), rounding=ROUND_HALF_UP)))

    @classmethod
    def desde_porcentaje(cls, valor: Decimal | int | float | str) -> "Percentage":
        """Convierte un porcentaje expresado como ``90`` o ``"88,2%"``."""
        texto = str(valor).replace("%", "").replace(",", ".").strip()
        numero = _decimal(texto)
        if not Decimal(0) <= numero <= Decimal(100):
            raise ErrorValidacion(
                "PORCENTAJE_FUERA_DE_RANGO", f"El porcentaje {numero} debe estar entre 0 y 100"
            )
        return cls(int((numero * Decimal(100)).quantize(Decimal("1"), rounding=ROUND_HALF_UP)))

    @classmethod
    def cien(cls) -> "Percentage":
        return cls(10_000)

    def a_decimal(self) -> Decimal:
        """Fracción 0–1 lista para multiplicar."""
        return Decimal(self.bp) / BP_TOTAL

    def a_porcentaje(self) -> Decimal:
        return Decimal(self.bp) / Decimal(100)

    def aplicar(self, monto: Decimal | int) -> Decimal:
        return _decimal(monto) * self.a_decimal()

    def __str__(self) -> str:  # pragma: no cover - presentación
        return f"{self.a_porcentaje()}%"


@dataclass(frozen=True, slots=True)
class Period:
    """Mes calendario identificado como ``YYYY-MM``."""

    anio: int
    mes: int

    def __post_init__(self) -> None:
        if not 1 <= self.mes <= 12:
            raise ErrorValidacion("MES_INVALIDO", f"El mes {self.mes} debe estar entre 1 y 12")
        if not 1900 <= self.anio <= 9999:
            raise ErrorValidacion("ANIO_INVALIDO", f"El año {self.anio} no es válido")

    @classmethod
    def desde_fecha(cls, valor: date) -> "Period":
        return cls(valor.year, valor.month)

    @classmethod
    def desde_texto(cls, valor: str) -> "Period":
        texto = valor.strip()
        partes = texto.split("-")
        if len(partes) != 2:
            raise ErrorValidacion("PERIODO_INVALIDO", f"El período {valor!r} debe ser YYYY-MM")
        try:
            return cls(int(partes[0]), int(partes[1]))
        except ValueError as exc:
            raise ErrorValidacion("PERIODO_INVALIDO", f"El período {valor!r} no es válido") from exc

    @property
    def inicio(self) -> date:
        return date(self.anio, self.mes, 1)

    @property
    def fin(self) -> date:
        return date(self.anio, self.mes, calendar.monthrange(self.anio, self.mes)[1])

    @property
    def dias(self) -> int:
        return calendar.monthrange(self.anio, self.mes)[1]

    def siguiente(self) -> "Period":
        if self.mes == 12:
            return Period(self.anio + 1, 1)
        return Period(self.anio, self.mes + 1)

    def anterior(self) -> "Period":
        if self.mes == 1:
            return Period(self.anio - 1, 12)
        return Period(self.anio, self.mes - 1)

    @classmethod
    def serie(cls, desde: "Period", cantidad: int) -> list["Period"]:
        if cantidad < 1:
            raise ErrorValidacion("CANTIDAD_INVALIDA", "La serie debe tener al menos un mes")
        resultado = [desde]
        for _ in range(cantidad - 1):
            resultado.append(resultado[-1].siguiente())
        return resultado

    def __str__(self) -> str:
        return f"{self.anio:04d}-{self.mes:02d}"

    def __lt__(self, otro: "Period") -> bool:
        return (self.anio, self.mes) < (otro.anio, otro.mes)

    def __le__(self, otro: "Period") -> bool:
        return (self.anio, self.mes) <= (otro.anio, otro.mes)


@dataclass(frozen=True, slots=True)
class DateRange:
    """Rango de fechas inclusivo; ``hasta`` nulo significa abierto."""

    desde: date
    hasta: date | None = None

    def __post_init__(self) -> None:
        if self.hasta is not None and self.hasta < self.desde:
            raise ErrorValidacion(
                "RANGO_INVALIDO", "La fecha final no puede ser anterior a la inicial"
            )

    def contiene(self, valor: date) -> bool:
        return self.desde <= valor and (self.hasta is None or valor <= self.hasta)

    def dias_solapados(self, periodo: Period) -> int:
        inicio = max(self.desde, periodo.inicio)
        fin = min(self.hasta or periodo.fin, periodo.fin)
        if fin < inicio:
            return 0
        return (fin - inicio).days + 1

    def fraccion_activa(self, periodo: Period) -> Decimal:
        return Decimal(self.dias_solapados(periodo)) / Decimal(periodo.dias)
