"""Configuración local de pytest para el layout ``src/`` (temporal).

Mientras no exista el ``pyproject.toml`` del proyecto (T034, Matías) no hay
paquete instalado, así que agregamos ``src/`` al ``sys.path`` para que
``python -m pytest tests`` funcione sin exportar ``PYTHONPATH`` a mano.

Cuando el proyecto se instale con ``pyproject.toml`` (``pythonpath = ["src"]``),
este archivo puede eliminarse sin cambiar ninguna prueba.
"""

from __future__ import annotations

import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
