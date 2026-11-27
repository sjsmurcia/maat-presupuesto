"""La API contra la base de pruebas, conectada con un rol que no puede saltarse la RLS."""

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Connection, Engine, create_engine, make_url, text
from sqlalchemy.orm import Session
from sqlalchemy.pool import NullPool

from backend.app import app
from backend.configuracion import configuracion_de_la_api, hasher_de_la_api
from backend.db.sesion import sesion_de_la_api
from backend.seguridad import hashear_password
from tests.api.datos_de_prueba import (
    ANALISTA,
    AREA_D,
    CONFIGURACION,
    EMPRESA_C,
    EMPRESA_D,
    HASHER,
    INACTIVO,
    PASSWORD,
    RESPONSABLE,
    ROL_DE_LA_API,
)

IDS = {
    "c": EMPRESA_C, "d": EMPRESA_D, "area_d": AREA_D,
    "analista": ANALISTA, "inactivo": INACTIVO, "responsable": RESPONSABLE,
}
DE_LOS_USUARIOS = "IN (:analista, :inactivo, :responsable)"


def _sembrar(conexion: Connection) -> None:
    conexion.execute(
        text("INSERT INTO empresas (id, nombre) VALUES (:c, 'Empresa C'), (:d, 'Empresa D')"),
        IDS,
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
        IDS,
    )
    _sembrar_usuarios(conexion)


def _sembrar_usuarios(conexion: Connection) -> None:
    conexion.execute(
        text(
            "INSERT INTO usuarios (id, email, hash_password, activo) VALUES "
            "(:analista, 'analista@ejemplo.edu', :h, true), "
            "(:inactivo, 'inactivo@ejemplo.edu', :h, false), "
            "(:responsable, 'responsable@ejemplo.edu', :h, true)"
        ),
        {**IDS, "h": hashear_password(HASHER, PASSWORD)},
    )
    conexion.execute(
        text(
            "INSERT INTO accesos (usuario_id, empresa_id, rol_id)"
            " SELECT :analista, :c, id FROM roles WHERE codigo = 'analista'"
            " UNION ALL SELECT :responsable, :d, id FROM roles WHERE codigo = 'responsable'"
        ),
        IDS,
    )
    conexion.execute(
        text("INSERT INTO areas (id, empresa_id, codigo, nombre) VALUES (:area_d, :d, 'TI', 'TI')"),
        IDS,
    )
    conexion.execute(
        text(
            "INSERT INTO accesos_areas (acceso_id, empresa_id, area_id)"
            " SELECT id, :d, :area_d FROM accesos WHERE usuario_id = :responsable"
        ),
        IDS,
    )


def _crear_rol_de_la_api(conexion: Connection) -> None:
    # el superusuario se salta la RLS aun con FORCE; la API real tampoco entra como dueño
    conexion.execute(text(f"CREATE ROLE {ROL_DE_LA_API} LOGIN NOBYPASSRLS"))
    conexion.execute(
        text(f"GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO {ROL_DE_LA_API}")
    )


def _limpiar(conexion: Connection) -> None:
    conexion.execute(text("DELETE FROM accesos_areas WHERE empresa_id = :d"), IDS)
    conexion.execute(text(f"DELETE FROM sesiones WHERE usuario_id {DE_LOS_USUARIOS}"), IDS)
    conexion.execute(text(f"DELETE FROM accesos WHERE usuario_id {DE_LOS_USUARIOS}"), IDS)
    conexion.execute(text(f"DELETE FROM usuarios WHERE id {DE_LOS_USUARIOS}"), IDS)
    conexion.execute(text("DELETE FROM areas WHERE empresa_id = :d"), IDS)
    conexion.execute(text("DELETE FROM cuentas WHERE empresa_id IN (:c, :d)"), IDS)
    conexion.execute(text("DELETE FROM empresas WHERE id IN (:c, :d)"), IDS)
    conexion.execute(text(f"DROP OWNED BY {ROL_DE_LA_API}"))
    conexion.execute(text(f"DROP ROLE {ROL_DE_LA_API}"))


@pytest.fixture(autouse=True)
def configuracion_de_prueba() -> Iterator[None]:
    """El secreto y el Argon2 barato de los tests, sin variables de entorno."""
    app.dependency_overrides[configuracion_de_la_api] = lambda: CONFIGURACION
    app.dependency_overrides[hasher_de_la_api] = lambda: HASHER
    yield
    app.dependency_overrides.clear()


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
    motor_del_rol.dispose()
    with motor.begin() as conexion:
        _limpiar(conexion)
