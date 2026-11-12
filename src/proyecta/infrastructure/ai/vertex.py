"""Adaptador opcional de Vertex AI (T143, US10).

Principios que respeta este adaptador:

- **Opt-in**: si ``PROYECTA_AI_ENABLED`` no está activo o falta el SDK, el
  adaptador se declara no disponible y el MVP sigue funcionando (FR-084).
- **Sin datos reales**: solo se envía el contexto sanitizado; nunca clientes,
  tarifas, montos ni datos personales (FR-086, RNF-15).
- **Con cita**: toda propuesta debe referenciar una evidencia de bitácora.
- **Sin escritura**: el adaptador solo devuelve una propuesta; nunca persiste.
"""

from __future__ import annotations

import importlib.util
import json
import logging
from dataclasses import dataclass, field
from typing import Any

from proyecta.application.ports import ContextoSugerencia, PropuestaIA
from proyecta.domain.enums import EtiquetaIA

logger = logging.getLogger(__name__)

VERSION_PROMPT = "vertex-proyecta-1.0.0"

CAMPOS_PERMITIDOS = frozenset({"estado", "flujo", "tipo", "campos", "fragmentos_bitacora"})
CLAVES_SENSIBLES = frozenset(
    {
        "cliente",
        "cliente_id",
        "sector",
        "sector_id",
        "manager",
        "manager_id",
        "owner",
        "owner_id",
        "email",
        "tarifa",
        "tarifa_hora_centavos",
        "monto",
        "monto_mensual_clp",
        "ingreso",
        "ingreso_potencial_clp",
        "mab",
        "mab_clp",
        "observaciones",
    }
)


@dataclass(frozen=True, slots=True)
class ConfiguracionVertex:
    habilitado: bool = False
    proyecto: str | None = None
    ubicacion: str = "us-central1"
    modelo: str = "gemini-1.5-flash"
    timeout_segundos: float = 10.0
    temperatura: float = 0.0


@dataclass(frozen=True, slots=True)
class ContextoSanitizado:
    """Representación mínima enviada al modelo."""

    codigo: str
    estado: str
    flujo: str
    tipo: str
    campos: dict[str, Any] = field(default_factory=dict)
    evidencias: tuple[tuple[str, str], ...] = ()

    def a_dict(self) -> dict[str, Any]:
        return {
            "codigo": self.codigo,
            "estado": self.estado,
            "flujo": self.flujo,
            "tipo": self.tipo,
            "campos": self.campos,
            "evidencias": [{"id": str(ident), "texto": texto} for ident, texto in self.evidencias],
        }


def _limpiar_campos(campos: dict[str, Any]) -> dict[str, Any]:
    limpio: dict[str, Any] = {}
    for clave, valor in campos.items():
        if clave.lower() in CLAVES_SENSIBLES:
            continue
        if isinstance(valor, dict):
            limpio[clave] = _limpiar_campos(valor)
        elif isinstance(valor, (str, int, float, bool)) or valor is None:
            limpio[clave] = valor
    return limpio


def sanitizar_contexto(contexto: ContextoSugerencia) -> ContextoSanitizado:
    """Elimina cualquier dato de cliente, tarifa o ingreso antes de enviar."""
    return ContextoSanitizado(
        codigo=contexto.codigo,
        estado=contexto.estado,
        flujo=contexto.flujo,
        tipo=contexto.tipo,
        campos=_limpiar_campos(dict(contexto.campos)),
        evidencias=tuple((str(ident), texto[:400]) for ident, texto in contexto.evidencias),
    )


def construir_prompt(contexto: ContextoSugerencia) -> str:
    """Prompt determinista con el contexto sanitizado y la exigencia de cita."""
    sanitizado = sanitizar_contexto(contexto)
    return (
        "Eres un asistente de calidad de datos del sistema Proyecta.\n"
        "Recibes un registro y fragmentos de bitácora. Debes detectar una única\n"
        "contradicción entre la bitácora y los campos, proponer un ajuste y citar\n"
        "el id de la evidencia que lo respalda.\n"
        "No inventes datos, no calcules montos y no escribas en el sistema.\n"
        "Responde solo JSON con las claves: campo, valor_sugerido, justificacion,\n"
        "etiqueta (DATO_VERIFICADO, CALCULO_SISTEMA, ESTIMACION,\n"
        "DATOS_INSUFICIENTES) y cita_id.\n\n"
        f"CONTEXTO:\n{json.dumps(sanitizado.a_dict(), ensure_ascii=False, sort_keys=True)}"
    )


class ProveedorVertexIA:
    """Implementación perezosa del puerto ``ProveedorIA``."""

    def __init__(self, configuracion: ConfiguracionVertex | None = None) -> None:
        self.configuracion = configuracion or ConfiguracionVertex()

    def disponible(self) -> bool:
        if not self.configuracion.habilitado:
            return False
        return importlib.util.find_spec("vertexai") is not None

    def sugerir(self, contexto: ContextoSugerencia) -> PropuestaIA | None:
        if not self.disponible():
            return None
        if not contexto.evidencias:
            return None
        try:
            return self._invocar(contexto)
        except Exception:  # pragma: no cover - el fallo de IA nunca bloquea
            logger.warning("Fallo del proveedor de IA; se continúa sin sugerencia")
            return None

    def _invocar(self, contexto: ContextoSugerencia) -> PropuestaIA | None:  # pragma: no cover
        from vertexai.generative_models import GenerativeModel  # import perezoso

        modelo = GenerativeModel(self.configuracion.modelo)
        respuesta = modelo.generate_content(
            construir_prompt(contexto),
            generation_config={
                "temperature": self.configuracion.temperatura,
                "response_mime_type": "application/json",
            },
        )
        texto = getattr(respuesta, "text", "") or ""
        datos = json.loads(texto)
        campo = str(datos.get("campo", "")).strip()
        if not campo:
            return None
        try:
            etiqueta = EtiquetaIA(str(datos.get("etiqueta", "ESTIMACION")))
        except ValueError:
            etiqueta = EtiquetaIA.ESTIMACION
        cita = datos.get("cita_id") or contexto.evidencias[0][0]
        return PropuestaIA(
            campo=campo,
            valor_sugerido=datos.get("valor_sugerido"),
            justificacion=str(datos.get("justificacion", ""))[:400],
            etiqueta=etiqueta,
            cita_id=cita,
            version_prompt=VERSION_PROMPT,
            proveedor="vertex",
        )


class ProveedorIANulo:
    """Proveedor de respaldo: nunca sugiere y nunca falla."""

    def disponible(self) -> bool:
        return False

    def sugerir(self, contexto: ContextoSugerencia) -> PropuestaIA | None:
        return None


__all__ = [
    "CLAVES_SENSIBLES",
    "ConfiguracionVertex",
    "ContextoSanitizado",
    "ProveedorIANulo",
    "ProveedorVertexIA",
    "VERSION_PROMPT",
    "construir_prompt",
    "sanitizar_contexto",
]
