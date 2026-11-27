"""La API contra la base de pruebas, conectada con un rol que no puede saltarse la RLS."""

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Connection, Engine, create_engine, make_url, text
from sqlalchemy.orm import Session
from sqlalchemy.pool import NullPool

from backend.app import app
from backend.db.sesion import sesion_de_la_api
from tests.api.datos_de_prueba import EMPRESA_C, EMPRESA_D, ROL_DE_LA_API


def _sembrar(conexion: Connection) -> None:
    conexion.execute(
        text("INSERT INTO empresas (id, nombre) VALUES (:c, 'Empresa C'), (:d, 'Empresa D')"),
        {"c": EMPRESA_C, "d": EMPRESA_D},
    )
    conexion.execute(
        text(
            "INSERT INTO cuentas (empresa_id, codigo, nombre, codigo_superior, naturaleza, "
            "es_detalle, activa) VALUES "
            "(:c, '5', 'Gastos', NULL, 'GASTO', false, true), "
            "(:c, '5204', 'Servicios en la nube', '5', 'GASTO', true, true), "
            "(:c, '5299', 'Fax', '5', 'GASTO', true, false), "
            "(:d, '4101', 'Ventas de contado', NULL, 'INGRESO', true, true)"
        ),
        {"c": EMPRESA_C, "d": EMPRESA_D},
    )


def _crear_rol_de_la_api(conexion: Connection) -> None:
    # el superusuario se salta la RLS aun con FORCE; la API real tampoco entra como dueño
    conexion.execute(text(f"CREATE ROLE {ROL_DE_LA_API} LOGIN NOBYPASSRLS"))
    conexion.execute(text(f"GRANT SELECT ON ALL TABLES IN SCHEMA public TO {ROL_DE_LA_API}"))


def _limpiar(conexion: Connection) -> None:
    ids = {"c": EMPRESA_C, "d": EMPRESA_D}
    conexion.execute(text("DELETE FROM cuentas WHERE empresa_id IN (:c, :d)"), ids)
    conexion.execute(text("DELETE FROM empresas WHERE id IN (:c, :d)"), ids)
    conexion.execute(text(f"DROP OWNED BY {ROL_DE_LA_API}"))
    conexion.execute(text(f"DROP ROLE {ROL_DE_LA_API}"))


@pytest.fixture
def cliente(motor: Engine, url_de_pruebas: str) -> Iterator[TestClient]:
    """La API con datos de dos empresas; al final se borran el rol y los datos."""
    with motor.begin() as conexion:
        _sembrar(conexion)
        _crear_rol_de_la_api(conexion)
    url_del_rol = make_url(url_de_pruebas).set(username=ROL_DE_LA_API, password=None)
    motor_del_rol = create_engine(url_del_rol, poolclass=NullPool)

    def sesion_del_rol() -> Iterator[Session]:
        with Session(motor_del_rol) as sesion:
            yield sesion

    app.dependency_overrides[sesion_de_la_api] = sesion_del_rol
    yield TestClient(app)
    app.dependency_overrides.clear()
    motor_del_rol.dispose()
    with motor.begin() as conexion:
        _limpiar(conexion)
