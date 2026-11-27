"""La configuración de la API sale del entorno: los secretos nunca están en el repo."""

import os
from collections.abc import Mapping
from dataclasses import dataclass
from functools import cache

from pwdlib import PasswordHash

from backend.seguridad import crear_hasher

LARGO_MIN_SECRETO = 32


@dataclass(frozen=True)
class Configuracion:
    jwt_secreto: str
    jwt_ttl_acceso_min: int = 15  # como Maat (decisión 51)
    refresh_ttl_dias: int = 30


def leer_configuracion(entorno: Mapping[str, str]) -> Configuracion:
    secreto = entorno.get("MP_JWT_SECRETO", "").strip()
    if len(secreto) < LARGO_MIN_SECRETO:
        raise RuntimeError(
            f"Falta la variable de entorno MP_JWT_SECRETO, de {LARGO_MIN_SECRETO} caracteres"
            " o más, para firmar los tokens"
        )
    return Configuracion(jwt_secreto=secreto)


@cache
def configuracion_de_la_api() -> Configuracion:
    return leer_configuracion(os.environ)


@cache
def hasher_de_la_api() -> PasswordHash:
    return crear_hasher()
