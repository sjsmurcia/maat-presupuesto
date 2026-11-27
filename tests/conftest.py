"""Los tests de la base y de la API corren contra un PostgreSQL de verdad, que se migra.

Sin DATABASE_URL_PRUEBAS se saltan: los tests del dominio no necesitan base.
"""

import os
from collections.abc import Iterator

import pytest
from sqlalchemy import Engine, create_engine

from backend.db.conexion import leer_url_de_la_base
from tests.db.base_de_pruebas import correr_alembic


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
