"""Los tests de la base corren contra un PostgreSQL de verdad, que se borra y se migra.

Sin DATABASE_URL_PRUEBAS se saltan: los tests del dominio no necesitan base.
"""

import os
from collections.abc import Iterator

import pytest
from sqlalchemy import Connection, Engine, create_engine

from backend.db.conexion import leer_url_de_la_base
from tests.db.base_de_pruebas import correr_alembic, crear_rol_sin_bypass, sembrar_dos_empresas


@pytest.fixture(scope="session")
def url_de_pruebas() -> str:
    if not os.environ.get("DATABASE_URL_PRUEBAS"):
        pytest.skip("Falta DATABASE_URL_PRUEBAS: los tests de la base necesitan un PostgreSQL")
    return leer_url_de_la_base(os.environ, "DATABASE_URL_PRUEBAS")


@pytest.fixture(scope="session")
def motor(url_de_pruebas: str) -> Iterator[Engine]:
    correr_alembic(url_de_pruebas, "downgrade", "base")
    correr_alembic(url_de_pruebas, "upgrade", "head")
    motor = create_engine(url_de_pruebas)
    yield motor
    motor.dispose()
    correr_alembic(url_de_pruebas, "downgrade", "base")


@pytest.fixture
def conexion(motor: Engine) -> Iterator[Connection]:
    """Una transacción con dos empresas y un rol sin BYPASSRLS; al final se deshace todo."""
    with motor.connect() as conexion:
        transaccion = conexion.begin()
        sembrar_dos_empresas(conexion)
        crear_rol_sin_bypass(conexion)
        yield conexion
        transaccion.rollback()
