from collections.abc import Iterator

import pytest
from sqlalchemy import Connection, Engine, text

from backend.seguridad import crear_hasher, verificar_password
from scripts.semilla_demo import EMPRESA_DEMO, sembrar

# Argon2 barato: los parámetros de verdad pagan 64 MiB por hash.
HASHER = crear_hasher(tiempo=1, memoria_kib=8, paralelismo=1)
PASSWORD = "contraseña-de-prueba-larga"  # noqa: S105
CONTEOS = {
    "empresas": "SELECT count(*) FROM empresas WHERE id = :e",
    "areas": "SELECT count(*) FROM areas WHERE empresa_id = :e",
    "cuentas": "SELECT count(*) FROM cuentas WHERE empresa_id = :e",
    "centros": "SELECT count(*) FROM centros WHERE empresa_id = :e",
    "usuarios": "SELECT count(*) FROM usuarios WHERE email LIKE '%@ejemplo.edu'",
    "accesos": "SELECT count(*) FROM accesos WHERE empresa_id = :e",
    "accesos_areas": "SELECT count(*) FROM accesos_areas WHERE empresa_id = :e",
}


@pytest.fixture
def transaccion(motor: Engine) -> Iterator[Connection]:
    with motor.connect() as conexion:
        transaccion = conexion.begin()
        yield conexion
        transaccion.rollback()


def test_semilla_corrida_dos_veces_deja_una_sola_empresa_demo(transaccion: Connection) -> None:
    # Act
    sembrar(transaccion, PASSWORD, HASHER)
    sembrar(transaccion, PASSWORD, HASHER)
    # Assert
    conteos = {
        tabla: transaccion.scalar(text(sql), {"e": EMPRESA_DEMO}) for tabla, sql in CONTEOS.items()
    }
    assert conteos == {
        "empresas": 1, "areas": 5, "cuentas": 15, "centros": 7,
        "usuarios": 2, "accesos": 2, "accesos_areas": 1,
    }


def test_semilla_el_usuario_demo_entra_con_la_contraseña_sembrada(transaccion: Connection) -> None:
    # Arrange
    sembrar(transaccion, PASSWORD, HASHER)
    consulta = text("SELECT hash_password FROM usuarios WHERE email = 'analista@ejemplo.edu'")
    # Act
    valida, _ = verificar_password(HASHER, PASSWORD, transaccion.scalar(consulta))
    # Assert
    assert valida is True
