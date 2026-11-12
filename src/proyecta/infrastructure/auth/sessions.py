"""Autenticación, sesiones y CSRF (T025–T027; RF-61, RNF-05, FR-066).

- Contraseñas con Argon2id (`argon2-cffi`).
- Sesión de servidor con identificador aleatorio en cookie HttpOnly + SameSite=Strict
  (+ Secure fuera de desarrollo) y expiración por inactividad.
- Bloqueo de 15 minutos tras 5 intentos fallidos, por cuenta y por IP.
- Token CSRF por sesión, exigido en todo POST (campo `csrf_token` o cabecera `X-CSRF-Token` para HTMX).
Un solo módulo para las tres tareas; se divide en `auth/` si crece.
"""

from __future__ import annotations

import hmac
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError

from proyecta.domain.entities import Sesion, Usuario, utcnow
from proyecta.domain.enums import MAX_INTENTOS_AUTENTICACION

_hasher = PasswordHasher()  # Argon2id con los parámetros por defecto recomendados (RFC 9106)
DURACION_SESION = timedelta(minutes=30)
DURACION_BLOQUEO = timedelta(minutes=15)
# Hash fijo para gastar el mismo tiempo cuando el correo no existe (no revela qué cuentas hay).
_HASH_SEÑUELO = _hasher.hash(secrets.token_urlsafe(16))


def hash_password(clave: str) -> str:
    return _hasher.hash(clave)


def verificar_password(hash_guardado: str, clave: str) -> bool:
    try:
        return _hasher.verify(hash_guardado, clave)
    except (VerificationError, InvalidHashError):
        return False


class AccesoDenegado(Exception):
    """Mensaje genérico para no revelar si el correo existe."""


@dataclass
class Autenticador:
    usuarios: object  # puerto RepositorioUsuarios (obtener, por_email)
    sesiones: object  # puerto RepositorioSesiones (obtener, guardar)
    fallos_ip: dict[str, list[datetime]] = field(default_factory=dict)

    def _ip_bloqueada(self, ip: str, ahora: datetime) -> bool:
        recientes = [t for t in self.fallos_ip.get(ip, []) if ahora - t < DURACION_BLOQUEO]
        self.fallos_ip[ip] = recientes
        return len(recientes) >= MAX_INTENTOS_AUTENTICACION

    def iniciar(self, email: str, clave: str, ip: str, user_agent: str | None = None) -> Sesion:
        ahora = utcnow()
        if self._ip_bloqueada(ip, ahora):
            raise AccesoDenegado("Demasiados intentos desde esta conexión. Espera 15 minutos.")
        usuario: Usuario | None = self.usuarios.por_email(email)
        if usuario and usuario.bloqueado_hasta and usuario.bloqueado_hasta > ahora:
            raise AccesoDenegado("La cuenta está bloqueada temporalmente. Espera 15 minutos.")
        valida = verificar_password(usuario.password_hash if usuario else _HASH_SEÑUELO, clave)
        if not (usuario and usuario.activo and valida):
            self.fallos_ip.setdefault(ip, []).append(ahora)
            if usuario:
                usuario.intentos_fallidos += 1
                if usuario.intentos_fallidos >= MAX_INTENTOS_AUTENTICACION:
                    usuario.bloqueado_hasta = ahora + DURACION_BLOQUEO
                    usuario.intentos_fallidos = 0
            raise AccesoDenegado("Correo o contraseña incorrectos.")
        usuario.intentos_fallidos = 0
        usuario.bloqueado_hasta = None
        usuario.ultimo_acceso = ahora
        return self.sesiones.guardar(Sesion(
            id=secrets.token_urlsafe(32), usuario_id=usuario.id, csrf_token=secrets.token_urlsafe(32),
            creado_en=ahora, expira_en=ahora + DURACION_SESION, ip=ip, user_agent=user_agent,
        ))

    def usuario_de(self, sesion_id: str | None) -> tuple[Usuario, Sesion] | None:
        """Valida la cookie y renueva la expiración por inactividad."""
        sesion = self.sesiones.obtener(sesion_id) if sesion_id else None
        ahora = utcnow()
        if not sesion or not sesion.activa or sesion.expira_en <= ahora:
            return None
        usuario = self.usuarios.obtener(sesion.usuario_id)
        if not usuario or not usuario.activo:
            return None
        sesion.expira_en = ahora + DURACION_SESION
        return usuario, sesion

    def cerrar(self, sesion_id: str | None) -> None:
        sesion = self.sesiones.obtener(sesion_id) if sesion_id else None
        if sesion:
            sesion.activa = False


def csrf_valido(sesion: Sesion, enviado: str | None) -> bool:
    return bool(enviado) and hmac.compare_digest(sesion.csrf_token, enviado)
