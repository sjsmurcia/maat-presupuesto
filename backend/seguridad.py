"""Contraseñas, JWT y refresh tokens, como en Maat (decisión 51): sin base de datos ni HTTP."""

import hashlib
import hmac
import secrets
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher

# Los parámetros de Maat (RFC 9106); los tests los bajan para no pagar 64 MiB por hash.
ARGON2_TIEMPO = 3
ARGON2_MEMORIA_KIB = 65536
ARGON2_PARALELISMO = 4
ALGORITMO_JWT = "HS256"


class TokenInvalidoError(Exception):
    """JWT ausente, vencido, manipulado o de otro tipo."""


def crear_hasher(
    tiempo: int = ARGON2_TIEMPO,
    memoria_kib: int = ARGON2_MEMORIA_KIB,
    paralelismo: int = ARGON2_PARALELISMO,
) -> PasswordHash:
    hasher = Argon2Hasher(time_cost=tiempo, memory_cost=memoria_kib, parallelism=paralelismo)
    return PasswordHash((hasher,))


def hashear_password(hasher: PasswordHash, password: str) -> str:
    return hasher.hash(password)


def verificar_password(
    hasher: PasswordHash, password: str, hash_almacenado: str
) -> tuple[bool, str | None]:
    """(es válida, hash nuevo si los parámetros subieron y conviene volver a guardarlo)."""
    return hasher.verify_and_update(password, hash_almacenado)


def emitir_jwt(secreto: str, *, usuario_id: uuid.UUID, tipo: str, ttl: timedelta) -> str:
    ahora = datetime.now(UTC)
    payload = {"sub": str(usuario_id), "tipo": tipo, "iat": ahora, "exp": ahora + ttl}
    return jwt.encode(payload, secreto, algorithm=ALGORITMO_JWT)


def verificar_jwt(secreto: str, token: str, *, tipo_esperado: str) -> dict[str, Any]:
    """Revisa la firma, el vencimiento y el tipo; si algo falla, TokenInvalidoError."""
    try:
        payload: dict[str, Any] = jwt.decode(
            token, secreto, algorithms=[ALGORITMO_JWT], options={"require": ["sub", "tipo", "exp"]}
        )
    except jwt.InvalidTokenError as error:
        raise TokenInvalidoError("token inválido o vencido") from error
    if payload["tipo"] != tipo_esperado:
        raise TokenInvalidoError(f"se esperaba un token de tipo {tipo_esperado}")
    return payload


def generar_refresh(sesion_id: uuid.UUID) -> tuple[str, str]:
    """(token para el cliente, hash del secreto para la base)."""
    secreto = secrets.token_urlsafe(32)
    return f"{sesion_id}.{secreto}", hash_refresh(secreto)


def hash_refresh(secreto: str) -> str:
    # SHA-256 y no Argon2: el secreto es al azar de 256 bits, nadie lo puede adivinar.
    return hashlib.sha256(secreto.encode()).hexdigest()


def partir_refresh(token: str) -> tuple[uuid.UUID, str] | None:
    """`<sesion_id>.<secreto>` → (sesion_id, secreto), o None si viene mal formado."""
    sesion_id, separador, secreto = token.partition(".")
    if not separador or not secreto:
        return None
    try:
        return uuid.UUID(sesion_id), secreto
    except ValueError:
        return None


def comparar_hash(a: str, b: str) -> bool:
    return hmac.compare_digest(a, b)
