"""Excepciones y códigos de error del dominio (T016).

El contrato de serialización es el del ``openapi.yaml`` (``components.schemas.Error``):
``{"code": ..., "message": ..., "details": {...}}``. Por eso los atributos canónicos
son ``code`` y ``message``; ``codigo`` y ``mensaje`` se conservan como alias de
compatibilidad para el código escrito antes de acordar el contrato con T028.

El dominio nunca conoce códigos HTTP de FastAPI; solo declara ``status_sugerido``
para que la capa de interfaz decida (tarea T031).
"""

from __future__ import annotations

from typing import Any

# Catálogo de códigos de error del MVP.
CODIGOS = {
    "VALIDACION": "Solicitud inválida",
    "CAMPO_OBLIGATORIO": "Falta un campo obligatorio",
    "MOTIVO_OBLIGATORIO": "El motivo es obligatorio",
    "RANGO_INVALIDO": "Valor fuera de rango",
    "VALOR_NUMERICO_INVALIDO": "Valor numérico inválido",
    "MONTO_INVALIDO": "Monto inválido",
    "PORCENTAJE_INVALIDO": "Porcentaje inválido",
    "PORCENTAJE_FUERA_DE_RANGO": "Porcentaje fuera de rango",
    "PERIODO_INVALIDO": "Período inválido",
    "MES_INVALIDO": "Mes inválido",
    "ANIO_INVALIDO": "Año inválido",
    "CANTIDAD_INVALIDA": "Cantidad inválida",
    "NO_ENCONTRADO": "Recurso no encontrado",
    "CONFLICTO_VERSION": "El registro fue modificado por otro usuario",
    "ESTADO_INVALIDO": "Transición de estado no permitida",
    "TRANSICION_INVALIDA": "Transición de estado o flujo no permitida",
    "CALCULO_INVALIDO": "No fue posible calcular la proyección",
    "HC_NEGATIVO": "El cierre de HC no puede ser negativo",
    "TARIFA_NO_VIGENTE": "El perfil no tiene tarifa vigente para el mes",
    "IA_NO_DISPONIBLE": "El asistente de IA no está disponible",
    "IA_SIN_EVIDENCIA": "La sugerencia de IA requiere una cita de bitácora",
    "PERMISO_DENEGADO": "Operación no autorizada",
    "OPERACION_NO_PERMITIDA": "La operación no está permitida sobre este recurso",
    "AUTENTICACION_REQUERIDA": "Se requiere autenticación",
    "CONFIGURACION_INVALIDA": "Configuración inválida",
}


class ErrorDominio(Exception):
    """Error base del dominio, serializable a la respuesta de la API."""

    code = "VALIDACION"
    status_sugerido = 400

    def __init__(
        self,
        code: str | None = None,
        message: str | None = None,
        *,
        codigo: str | None = None,
        mensaje: str | None = None,
        detalle: dict[str, Any] | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.code = code or codigo or type(self).code
        self.message = (
            message or mensaje or CODIGOS.get(self.code, "Error de dominio")
        )
        self.detalle = detalle if detalle is not None else (details or {})
        super().__init__(self.message)

    # --- Alias en español, conservados para no romper llamadas previas ---------
    @property
    def codigo(self) -> str:
        return self.code

    @codigo.setter
    def codigo(self, valor: str) -> None:
        self.code = valor

    @property
    def mensaje(self) -> str:
        return self.message

    @mensaje.setter
    def mensaje(self, valor: str) -> None:
        self.message = valor

    def a_dict(self) -> dict[str, Any]:
        cuerpo: dict[str, Any] = {"code": self.code, "message": self.message}
        if self.detalle:
            cuerpo["details"] = self.detalle
        return cuerpo

    def __str__(self) -> str:
        return f"{self.code}: {self.message}"


class ErrorValidacion(ErrorDominio):
    code = "VALIDACION"
    status_sugerido = 422


class ErrorCampoObligatorio(ErrorValidacion):
    code = "CAMPO_OBLIGATORIO"


class ErrorMotivoObligatorio(ErrorCampoObligatorio):
    code = "MOTIVO_OBLIGATORIO"


class ErrorRango(ErrorValidacion):
    code = "RANGO_INVALIDO"


class ErrorNoEncontrado(ErrorDominio):
    code = "NO_ENCONTRADO"
    status_sugerido = 404


class ErrorConflicto(ErrorDominio):
    code = "CONFLICTO_VERSION"
    status_sugerido = 409


class ErrorTransicionInvalida(ErrorDominio):
    code = "TRANSICION_INVALIDA"
    status_sugerido = 409


class ErrorEstadoInvalido(ErrorTransicionInvalida):
    """Alias de compatibilidad con el código previo (``ESTADO_INVALIDO``)."""

    code = "ESTADO_INVALIDO"


class ErrorAutorizacion(ErrorDominio):
    """Base de los errores de autorización; expone la acción denegada (T028)."""

    code = "PERMISO_DENEGADO"
    status_sugerido = 403

    def __init__(
        self,
        code: str | None = None,
        message: str | None = None,
        *,
        accion: str = "",
        codigo: str | None = None,
        mensaje: str | None = None,
        detalle: dict[str, Any] | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.accion = accion
        if accion and detalle is None and details is None:
            detalle = {"accion": accion}
        super().__init__(
            code,
            message,
            codigo=codigo,
            mensaje=mensaje,
            detalle=detalle,
            details=details,
        )


class PermisoDenegado(ErrorAutorizacion):
    """El rol o la propiedad del recurso no alcanzan para la acción solicitada."""

    code = "PERMISO_DENEGADO"
    status_sugerido = 403


class OperacionNoPermitida(ErrorAutorizacion):
    """La operación no existe para el recurso (p. ej. editar bitácora o auditoría)."""

    code = "OPERACION_NO_PERMITIDA"
    status_sugerido = 405


class ErrorPermiso(PermisoDenegado):
    """Alias de compatibilidad con el nombre previo a T028."""


class ErrorAutenticacion(ErrorDominio):
    code = "AUTENTICACION_REQUERIDA"
    status_sugerido = 401


class ErrorCalculo(ErrorDominio):
    code = "CALCULO_INVALIDO"
    status_sugerido = 422


class ErrorHCNegativo(ErrorCalculo):
    code = "HC_NEGATIVO"


class ErrorTarifaNoVigente(ErrorCalculo):
    code = "TARIFA_NO_VIGENTE"


class ErrorIA(ErrorDominio):
    code = "IA_NO_DISPONIBLE"
    status_sugerido = 503


class ErrorConfiguracion(ErrorDominio):
    code = "CONFIGURACION_INVALIDA"
    status_sugerido = 500


__all__ = [
    "CODIGOS",
    "ErrorAutenticacion",
    "ErrorAutorizacion",
    "ErrorCalculo",
    "ErrorCampoObligatorio",
    "ErrorConflicto",
    "ErrorConfiguracion",
    "ErrorDominio",
    "ErrorEstadoInvalido",
    "ErrorHCNegativo",
    "ErrorIA",
    "ErrorMotivoObligatorio",
    "ErrorNoEncontrado",
    "ErrorPermiso",
    "ErrorRango",
    "ErrorTarifaNoVigente",
    "ErrorTransicionInvalida",
    "ErrorValidacion",
    "OperacionNoPermitida",
    "PermisoDenegado",
]
