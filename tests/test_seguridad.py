import uuid
from datetime import timedelta

import pytest

from backend.configuracion import leer_configuracion
from backend.seguridad import (
    TokenInvalidoError,
    comparar_hash,
    emitir_jwt,
    generar_refresh,
    hash_refresh,
    partir_refresh,
    verificar_jwt,
)

SECRETO = "s" * 32
USUARIO = uuid.UUID("00000000-0000-0000-0000-0000000000a1")
QUINCE_MINUTOS = timedelta(minutes=15)


def test_verificar_jwt_recien_emitido_devuelve_el_usuario_y_el_tipo() -> None:
    # Arrange
    token = emitir_jwt(SECRETO, usuario_id=USUARIO, tipo="access", ttl=QUINCE_MINUTOS)
    # Act
    payload = verificar_jwt(SECRETO, token, tipo_esperado="access")
    # Assert
    assert (payload["sub"], payload["tipo"]) == (str(USUARIO), "access")


@pytest.mark.parametrize(
    ("secreto_de_firma", "ttl", "tipo", "mensaje"),
    [
        (SECRETO, timedelta(seconds=-1), "access", "inválido o vencido"),
        ("otro" * 8, QUINCE_MINUTOS, "access", "inválido o vencido"),
        (SECRETO, QUINCE_MINUTOS, "reset", "tipo access"),
    ],
)
def test_verificar_jwt_vencido_ajeno_o_de_otro_tipo_lanza_error(
    secreto_de_firma: str, ttl: timedelta, tipo: str, mensaje: str
) -> None:
    # Arrange
    token = emitir_jwt(secreto_de_firma, usuario_id=USUARIO, tipo=tipo, ttl=ttl)
    # Act / Assert
    with pytest.raises(TokenInvalidoError, match=mensaje):
        verificar_jwt(SECRETO, token, tipo_esperado="access")


def test_partir_refresh_generado_devuelve_su_sesion_y_un_secreto_con_ese_hash() -> None:
    # Arrange
    token, token_hash = generar_refresh(USUARIO)
    # Act
    sesion_id, secreto = partir_refresh(token)
    # Assert
    assert sesion_id == USUARIO
    assert comparar_hash(hash_refresh(secreto), token_hash)


@pytest.mark.parametrize("token", ["sin-punto", "no-es-uuid.secreto", f"{USUARIO}."])
def test_partir_refresh_mal_formado_devuelve_none(token: str) -> None:
    assert partir_refresh(token) is None


@pytest.mark.parametrize("entorno", [{}, {"MP_JWT_SECRETO": "corto"}])
def test_leer_configuracion_sin_un_secreto_largo_lanza_error(entorno: dict[str, str]) -> None:
    with pytest.raises(RuntimeError, match="MP_JWT_SECRETO, de 32 caracteres"):
        leer_configuracion(entorno)


def test_leer_configuracion_con_secreto_usa_los_tiempos_de_maat() -> None:
    # Act
    configuracion = leer_configuracion({"MP_JWT_SECRETO": SECRETO})
    # Assert
    assert (configuracion.jwt_ttl_acceso_min, configuracion.refresh_ttl_dias) == (15, 30)
