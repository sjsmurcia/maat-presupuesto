"""Login, refresh y logout como los de Maat (decisión 51): JWT de acceso y refresh revocable."""

import uuid
from datetime import UTC, datetime, timedelta
from functools import cache
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pwdlib import PasswordHash
from pydantic import BaseModel, Field
from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from backend.configuracion import Configuracion, configuracion_de_la_api, hasher_de_la_api
from backend.db.modelos import Sesion, Usuario
from backend.db.sesion import sesion_de_la_api
from backend.errores import ErrorDeLaApi
from backend.seguridad import (
    TokenInvalidoError,
    es_el_mismo_hash,
    emitir_jwt,
    generar_refresh,
    hash_refresh,
    hashear_password,
    partir_refresh,
    verificar_jwt,
    verificar_password,
)

# Un solo mensaje para correo inexistente, contraseña mala o usuario inactivo:
# así nadie averigua qué cuentas existen.
CREDENCIALES_INVALIDAS = (
    "El correo o la contraseña no coinciden. Revisa los dos y vuelve a intentarlo."
)
SESION_VENCIDA = "La sesión venció. Vuelve a entrar."
BEARER = {"WWW-Authenticate": "Bearer"}

SesionApi = Annotated[Session, Depends(sesion_de_la_api)]
Config = Annotated[Configuracion, Depends(configuracion_de_la_api)]
Hasher = Annotated[PasswordHash, Depends(hasher_de_la_api)]
Credenciales = Annotated[
    HTTPAuthorizationCredentials | None, Depends(HTTPBearer(auto_error=False))
]

rutas_de_auth = APIRouter(prefix="/auth")


class LoginRequest(BaseModel):
    email: str = Field(min_length=3, max_length=320)
    password: str = Field(min_length=1, max_length=1024)


class RefreshRequest(BaseModel):
    refresh_token: str = Field(min_length=1, max_length=512)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # segundos de vida del access token
    refresh_token: str


def usuario_actual(config: Config, credenciales: Credenciales) -> uuid.UUID:
    """Quién hace la petición, según su JWT de acceso: firma, vencimiento y tipo."""
    if credenciales is None:
        raise ErrorDeLaApi(401, "Inicia sesión para continuar.", BEARER)
    try:
        payload = verificar_jwt(config.jwt_secreto, credenciales.credentials, tipo_esperado="access")
        return uuid.UUID(payload["sub"])
    except (TokenInvalidoError, ValueError) as error:
        raise ErrorDeLaApi(401, SESION_VENCIDA, BEARER) from error


UsuarioActual = Annotated[uuid.UUID, Depends(usuario_actual)]


@rutas_de_auth.post("/login")
def iniciar_sesion(
    datos: LoginRequest, sesion: SesionApi, config: Config, hasher: Hasher
) -> TokenResponse:
    usuario = sesion.scalar(select(Usuario).where(Usuario.email == datos.email.strip().lower()))
    if not _credenciales_validas(hasher, usuario, datos.password):
        raise ErrorDeLaApi(401, CREDENCIALES_INVALIDAS)
    respuesta = _emitir_tokens(sesion, config, usuario.id)
    sesion.commit()
    return respuesta


@rutas_de_auth.post("/refresh")
def refrescar(datos: RefreshRequest, sesion: SesionApi, config: Config) -> TokenResponse:
    """Rota el refresh: el viejo deja de valer, y si alguien lo vuelve a usar se presume
    robado y se cierran todas las sesiones de ese usuario."""
    fila = _sesion_del_refresh(sesion, datos.refresh_token, bloquear=True)
    if fila is None:
        raise ErrorDeLaApi(401, SESION_VENCIDA)
    if fila.revocado_en is not None:
        _revocar_todas(sesion, fila.usuario_id)
        sesion.commit()
        raise ErrorDeLaApi(401, SESION_VENCIDA)
    activo = sesion.scalar(select(Usuario.activo).where(Usuario.id == fila.usuario_id))
    if fila.expira_en <= datetime.now(UTC) or not activo:
        raise ErrorDeLaApi(401, SESION_VENCIDA)
    fila.revocado_en = datetime.now(UTC)
    respuesta = _emitir_tokens(sesion, config, fila.usuario_id)
    sesion.commit()
    return respuesta


@rutas_de_auth.post("/logout", status_code=204)
def cerrar_sesion(datos: RefreshRequest, sesion: SesionApi, usuario: UsuarioActual) -> None:
    """Si el refresh no es de este usuario o ya no vale, no pasa nada: no se revela."""
    fila = _sesion_del_refresh(sesion, datos.refresh_token, bloquear=False)
    if fila is not None and fila.usuario_id == usuario and fila.revocado_en is None:
        fila.revocado_en = datetime.now(UTC)
        sesion.commit()


@cache
def _hash_de_sacrificio(hasher: PasswordHash) -> str:
    """Se verifica cuando el correo no existe, para que el tiempo no delate qué cuentas hay."""
    return hashear_password(hasher, "de-sacrificio-para-un-tiempo-parejo")


def _credenciales_validas(hasher: PasswordHash, usuario: Usuario | None, password: str) -> bool:
    if usuario is None:
        verificar_password(hasher, password, _hash_de_sacrificio(hasher))
        return False
    valida, _ = verificar_password(hasher, password, usuario.hash_password)
    return valida and usuario.activo


def _emitir_tokens(sesion: Session, config: Configuracion, usuario_id: uuid.UUID) -> TokenResponse:
    sesion_id = uuid.uuid4()
    refresh, refresh_hash = generar_refresh(sesion_id)
    vence = datetime.now(UTC) + timedelta(days=config.refresh_ttl_dias)
    sesion.add(
        Sesion(id=sesion_id, usuario_id=usuario_id, refresh_token_hash=refresh_hash, expira_en=vence)
    )
    ttl = timedelta(minutes=config.jwt_ttl_acceso_min)
    acceso = emitir_jwt(config.jwt_secreto, usuario_id=usuario_id, tipo="access", ttl=ttl)
    return TokenResponse(
        access_token=acceso, expires_in=int(ttl.total_seconds()), refresh_token=refresh
    )


def _sesion_del_refresh(sesion: Session, token: str, *, bloquear: bool) -> Sesion | None:
    """La fila del refresh si el token está bien formado y su secreto coincide."""
    partes = partir_refresh(token)
    if partes is None:
        return None
    fila = sesion.get(Sesion, partes[0], with_for_update=bloquear)
    if fila is None or not es_el_mismo_hash(fila.refresh_token_hash, hash_refresh(partes[1])):
        return None
    return fila


def _revocar_todas(sesion: Session, usuario_id: uuid.UUID) -> None:
    sesion.execute(
        update(Sesion)
        .where(Sesion.usuario_id == usuario_id, Sesion.revocado_en.is_(None))
        .values(revocado_en=func.now())
    )
