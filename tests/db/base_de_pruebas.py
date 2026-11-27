"""Lo que comparten los tests de la base: las dos empresas, el rol y cómo correr Alembic."""

import uuid
from pathlib import Path

import pytest
from sqlalchemy import Connection, text

from alembic import command
from alembic.config import Config

RAIZ = Path(__file__).resolve().parents[2]
EMPRESA_A = uuid.UUID("00000000-0000-0000-0000-00000000000a")
EMPRESA_B = uuid.UUID("00000000-0000-0000-0000-00000000000b")
ROL_SIN_BYPASS = "rol_prueba_rls"


def correr_alembic(url: str, comando: str, revision: str) -> None:
    with pytest.MonkeyPatch.context() as parche:
        parche.setenv("DATABASE_URL", url)
        getattr(command, comando)(Config(str(RAIZ / "alembic.ini")), revision)


def sembrar_dos_empresas(conexion: Connection) -> None:
    conexion.execute(
        text("INSERT INTO empresas (id, nombre) VALUES (:a, 'Empresa A'), (:b, 'Empresa B')"),
        {"a": EMPRESA_A, "b": EMPRESA_B},
    )
    conexion.execute(
        text(
            "INSERT INTO cuentas (empresa_id, codigo, nombre, naturaleza, es_detalle) VALUES "
            "(:a, '5204', 'Servicios en la nube', 'GASTO', true), "
            "(:b, '4101', 'Ventas de contado', 'INGRESO', true)"
        ),
        {"a": EMPRESA_A, "b": EMPRESA_B},
    )


def crear_rol_sin_bypass(conexion: Connection) -> None:
    conexion.execute(text(f"CREATE ROLE {ROL_SIN_BYPASS} NOLOGIN"))
    conexion.execute(text(f"GRANT SELECT, INSERT ON ALL TABLES IN SCHEMA public TO {ROL_SIN_BYPASS}"))


def entrar_como_la_api(conexion: Connection, empresa_id: uuid.UUID | None) -> None:
    """Como la API: un rol sin BYPASSRLS y, si hay, la empresa elegida en la transacción."""
    conexion.execute(text(f"SET LOCAL ROLE {ROL_SIN_BYPASS}"))
    if empresa_id is not None:
        conexion.execute(
            text("SELECT set_config('app.empresa_id', :id, true)"), {"id": str(empresa_id)}
        )
