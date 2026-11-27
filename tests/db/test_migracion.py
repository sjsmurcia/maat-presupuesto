import pytest
from sqlalchemy import Connection, Engine, inspect, text
from sqlalchemy.exc import IntegrityError

from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from backend.db.modelos import Base
from tests.db.base_de_pruebas import EMPRESA_A, correr_alembic

TABLAS = {"empresas", "areas", "cuentas", "centros"}


def _tablas(motor: Engine) -> set[str]:
    return set(inspect(motor).get_table_names()) - {"alembic_version"}


def test_migracion_upgrade_head_crea_las_cuatro_tablas(motor: Engine) -> None:
    # Act
    tablas = _tablas(motor)
    # Assert
    assert tablas == TABLAS


def test_migracion_comparada_con_los_modelos_no_tiene_diferencias(motor: Engine) -> None:
    # Act
    with motor.connect() as conexion:
        diferencias = compare_metadata(MigrationContext.configure(conexion), Base.metadata)
    # Assert
    assert diferencias == []


def test_migracion_cuenta_con_naturaleza_invalida_lanza_error(conexion: Connection) -> None:
    # Arrange: ORDEN no es una de las 6 naturalezas
    insertar = text(
        "INSERT INTO cuentas (empresa_id, codigo, nombre, naturaleza, es_detalle) "
        "VALUES (:a, '9101', 'Cuentas de orden', 'ORDEN', true)"
    )
    # Act / Assert
    with pytest.raises(IntegrityError, match="ck_cuentas_naturaleza"):
        conexion.execute(insertar, {"a": EMPRESA_A})


def test_migracion_downgrade_base_deja_la_base_sin_tablas(motor: Engine, url_de_pruebas: str) -> None:
    # Act
    correr_alembic(url_de_pruebas, "downgrade", "base")
    try:
        tablas = _tablas(motor)
    finally:
        correr_alembic(url_de_pruebas, "upgrade", "head")
    # Assert
    assert tablas == set()
