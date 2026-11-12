"""Carga la semilla sintética a JSON para demo o fixtures (T035, T154, T165).

Uso::

    python scripts/seed_synthetic.py --cantidad 1000 --salida datos_sinteticos.json
    python scripts/seed_synthetic.py --fixture four-records

Nunca escribe en Datastore ni usa datos reales. El cargador concreto lo
implementa el equipo de infraestructura cuando exista el emulador; este script
produce el artefacto reproducible que consumen la demo y las pruebas de US11.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from proyecta.domain.value_objects import Period  # noqa: E402
from proyecta.seed.fixtures import cargar_fixture, serializar_fixture  # noqa: E402
from proyecta.seed.synthetic import generar_semilla, serializar_semilla  # noqa: E402

CANTIDAD_DEFECTO = 1_000


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Genera la semilla sintética de Proyecta")
    parser.add_argument(
        "--cantidad", type=int, default=CANTIDAD_DEFECTO, help="Cantidad de registros"
    )
    parser.add_argument("--periodo", default="2026-01", help="Primer mes YYYY-MM")
    parser.add_argument("--meses", type=int, default=12, help="Meses de metas")
    parser.add_argument("--semilla", type=int, default=20260101, help="Semilla aleatoria")
    parser.add_argument("--salida", type=Path, default=None, help="Archivo JSON de salida")
    parser.add_argument(
        "--fixture",
        choices=("four-records",),
        default=None,
        help="Genera el fixture de cuatro registros con inconsistencias (AC-14)",
    )
    return parser


def _escribir(contenido: str, salida: Path | None, resumen: str) -> None:
    if salida is None:
        print(contenido)
    else:
        salida.write_text(contenido, encoding="utf-8")
        print(f"{resumen} -> {salida}")


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)

    if args.fixture == "four-records":
        fixture = cargar_fixture()
        contenido = json.dumps(
            serializar_fixture(fixture), ensure_ascii=False, indent=2
        )
        _escribir(
            contenido,
            args.salida,
            f"Fixture de {len(fixture.datos.registros)} registros "
            f"({len(fixture.inconsistencias_esperadas)} inconsistencias esperadas)",
        )
        return 0

    datos = generar_semilla(
        cantidad_registros=args.cantidad,
        primer_mes=Period.desde_texto(args.periodo),
        meses=args.meses,
        semilla=args.semilla,
    )
    contenido = json.dumps(serializar_semilla(datos), ensure_ascii=False, indent=2)
    _escribir(
        contenido,
        args.salida,
        f"Semilla de {len(datos.registros)} registros y {len(datos.perfiles)} perfiles",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
