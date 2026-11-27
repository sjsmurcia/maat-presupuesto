import pytest
from fastapi.testclient import TestClient
from httpx import Response
from sqlalchemy import Engine

from backend.auth import CREDENCIALES_INVALIDAS, SESION_VENCIDA
from backend.seguridad import verificar_jwt
from tests.api.datos_de_prueba import (
    ANALISTA,
    CONFIGURACION,
    INACTIVO,
    PASSWORD,
    encabezado_de,
    ejecutar_sql,
)


def _entrar(
    cliente: TestClient, email: str = "analista@ejemplo.edu", password: str = PASSWORD
) -> Response:
    return cliente.post("/api/auth/login", json={"email": email, "password": password})


def _refrescar(cliente: TestClient, refresh: str) -> Response:
    return cliente.post("/api/auth/refresh", json={"refresh_token": refresh})


def test_login_con_credenciales_buenas_devuelve_los_tokens_del_usuario(cliente: TestClient) -> None:
    # Act
    respuesta = _entrar(cliente, email="  Analista@Ejemplo.edu ")
    # Assert
    cuerpo = respuesta.json()
    assert respuesta.status_code == 200
    assert (cuerpo["token_type"], cuerpo["expires_in"]) == ("bearer", 900)
    acceso = verificar_jwt(CONFIGURACION.jwt_secreto, cuerpo["access_token"], tipo_esperado="access")
    assert acceso["sub"] == str(ANALISTA)


@pytest.mark.parametrize(
    ("email", "password"),
    [
        ("analista@ejemplo.edu", "otra-contraseña"),
        ("nadie@ejemplo.edu", PASSWORD),
        ("inactivo@ejemplo.edu", PASSWORD),
    ],
)
def test_login_con_credenciales_malas_o_inactivo_devuelve_401_con_el_mismo_mensaje(
    cliente: TestClient, email: str, password: str
) -> None:
    # Act
    respuesta = _entrar(cliente, email, password)
    # Assert
    assert respuesta.status_code == 401
    assert respuesta.json() == {"mensaje": CREDENCIALES_INVALIDAS}


def test_refresh_devuelve_tokens_nuevos_y_el_viejo_ya_no_vale(cliente: TestClient) -> None:
    # Arrange
    viejo = _entrar(cliente).json()["refresh_token"]
    # Act
    nuevo = _refrescar(cliente, viejo)
    # Assert
    assert nuevo.status_code == 200
    assert nuevo.json()["refresh_token"] != viejo
    assert _refrescar(cliente, nuevo.json()["refresh_token"]).status_code == 200


def test_refresh_reusado_cierra_todas_las_sesiones_del_usuario(cliente: TestClient) -> None:
    # Arrange: el viejo se rota y alguien lo vuelve a usar
    viejo = _entrar(cliente).json()["refresh_token"]
    nuevo = _refrescar(cliente, viejo).json()["refresh_token"]
    # Act
    reuso = _refrescar(cliente, viejo)
    # Assert: el reuso falla y también el nuevo, que quedó revocado
    assert reuso.status_code == 401
    assert reuso.json() == {"mensaje": SESION_VENCIDA}
    assert _refrescar(cliente, nuevo).status_code == 401


@pytest.mark.parametrize("refresh", ["mal-formado", "00000000-0000-0000-0000-000000000000.x"])
def test_refresh_inexistente_o_mal_formado_devuelve_401(cliente: TestClient, refresh: str) -> None:
    assert _refrescar(cliente, refresh).status_code == 401


def test_logout_revoca_el_refresh(cliente: TestClient) -> None:
    # Arrange
    refresh = _entrar(cliente).json()["refresh_token"]
    # Act
    respuesta = cliente.post(
        "/api/auth/logout", json={"refresh_token": refresh}, headers=encabezado_de(ANALISTA)
    )
    # Assert
    assert respuesta.status_code == 204
    assert _refrescar(cliente, refresh).status_code == 401


def test_logout_sin_token_de_acceso_devuelve_401(cliente: TestClient) -> None:
    # Act
    respuesta = cliente.post("/api/auth/logout", json={"refresh_token": "x.y"})
    # Assert
    assert respuesta.status_code == 401
    assert respuesta.json() == {"mensaje": "Inicia sesión para continuar."}
    assert respuesta.headers["WWW-Authenticate"] == "Bearer"


def test_refresh_vencido_devuelve_401(cliente: TestClient, motor: Engine) -> None:
    # Arrange: la sesión venció ayer
    refresh = _entrar(cliente).json()["refresh_token"]
    ejecutar_sql(
        motor, "UPDATE sesiones SET expira_en = now() - interval '1 day' WHERE usuario_id = :u",
        u=ANALISTA,
    )
    # Act
    respuesta = _refrescar(cliente, refresh)
    # Assert
    assert respuesta.status_code == 401
    assert respuesta.json() == {"mensaje": SESION_VENCIDA}


def test_refresh_de_un_usuario_desactivado_devuelve_401(cliente: TestClient, motor: Engine) -> None:
    # Arrange: entró, y después lo desactivaron
    refresh = _entrar(cliente).json()["refresh_token"]
    ejecutar_sql(motor, "UPDATE usuarios SET activo = false WHERE id = :u", u=ANALISTA)
    # Act
    respuesta = _refrescar(cliente, refresh)
    # Assert
    assert respuesta.status_code == 401
    assert respuesta.json() == {"mensaje": SESION_VENCIDA}


def test_refresh_con_la_sesion_buena_y_el_secreto_cambiado_devuelve_401(cliente: TestClient) -> None:
    # Arrange: la sesión existe, pero el secreto no es el suyo
    sesion_id, _, _ = _entrar(cliente).json()["refresh_token"].partition(".")
    # Act
    respuesta = _refrescar(cliente, f"{sesion_id}.un-secreto-adivinado")
    # Assert
    assert respuesta.status_code == 401
    assert respuesta.json() == {"mensaje": SESION_VENCIDA}


def test_logout_con_el_refresh_de_otro_usuario_no_lo_revoca(cliente: TestClient) -> None:
    # Arrange: el refresh es del analista y el logout lo pide otro usuario
    refresh = _entrar(cliente).json()["refresh_token"]
    # Act
    respuesta = cliente.post(
        "/api/auth/logout", json={"refresh_token": refresh}, headers=encabezado_de(INACTIVO)
    )
    # Assert: responde igual, sin revelar nada, y el refresh del analista sigue valiendo
    assert respuesta.status_code == 204
    assert _refrescar(cliente, refresh).status_code == 200
