"""Cada test de la base corre en una transacción que se deshace al final."""

from collections.abc import Iterator

import pytest
from sqlalchemy import Connection, Engine

from tests.db.base_de_pruebas import crear_rol_sin_bypass, sembrar_dos_empresas


@pytest.fixture
def conexion(motor: Engine) -> Iterator[Connection]:
    """Una transacción con dos empresas y un rol sin BYPASSRLS; al final se deshace todo."""
    with motor.connect() as conexion:
        transaccion = conexion.begin()
        sembrar_dos_empresas(conexion)
        crear_rol_sin_bypass(conexion)
        yield conexion
        transaccion.rollback()
