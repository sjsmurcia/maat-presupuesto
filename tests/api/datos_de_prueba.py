"""Las empresas, los usuarios y el rol que usan los tests de la API."""

import uuid
from datetime import timedelta

from backend.configuracion import Configuracion
from backend.seguridad import crear_hasher, emitir_jwt

EMPRESA_C = uuid.UUID("00000000-0000-0000-0000-00000000000c")
EMPRESA_D = uuid.UUID("00000000-0000-0000-0000-00000000000d")
ROL_DE_LA_API = "rol_api_prueba"

ANALISTA = uuid.UUID("00000000-0000-0000-0000-0000000000a1")  # analista en la empresa C
INACTIVO = uuid.UUID("00000000-0000-0000-0000-0000000000a2")
RESPONSABLE = uuid.UUID("00000000-0000-0000-0000-0000000000a3")  # responsable en D, de un área
AREA_D = uuid.UUID("00000000-0000-0000-0000-0000000000d1")
PASSWORD = "una-contraseña-de-prueba"  # noqa: S105
CONFIGURACION = Configuracion(jwt_secreto="secreto-de-los-tests-de-la-api-0123456789")
# Argon2 barato: los parámetros de verdad pagan 64 MiB por hash.
HASHER = crear_hasher(tiempo=1, memoria_kib=8, paralelismo=1)


def encabezado_de(usuario_id: uuid.UUID) -> dict[str, str]:
    """El Bearer con el que entra un usuario, sin pasar por el login."""
    token = emitir_jwt(
        CONFIGURACION.jwt_secreto, usuario_id=usuario_id, tipo="access", ttl=timedelta(minutes=5)
    )
    return {"Authorization": f"Bearer {token}"}
