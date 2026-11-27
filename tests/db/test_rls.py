import pytest
from sqlalchemy import Connection, text
from sqlalchemy.exc import DBAPIError

from tests.db.base_de_pruebas import EMPRESA_A, EMPRESA_B, entrar_como_la_api


def _codigos_de_cuentas(conexion: Connection) -> list[str]:
    return list(conexion.scalars(text("SELECT codigo FROM cuentas ORDER BY codigo")))


def test_rls_con_la_empresa_a_en_la_sesion_solo_ve_las_cuentas_de_a(conexion: Connection) -> None:
    # Arrange: la empresa A tiene la 5204 y la B la 4101
    entrar_como_la_api(conexion, EMPRESA_A)
    # Act
    codigos = _codigos_de_cuentas(conexion)
    # Assert
    assert codigos == ["5204"]


def test_rls_con_la_empresa_a_en_la_sesion_solo_ve_su_empresa(conexion: Connection) -> None:
    # Arrange
    entrar_como_la_api(conexion, EMPRESA_A)
    # Act
    nombres = list(conexion.scalars(text("SELECT nombre FROM empresas")))
    # Assert
    assert nombres == ["Empresa A"]


def test_rls_sin_empresa_en_la_sesion_no_ve_ninguna_cuenta(conexion: Connection) -> None:
    # Arrange
    entrar_como_la_api(conexion, None)
    # Act
    codigos = _codigos_de_cuentas(conexion)
    # Assert
    assert codigos == []


def test_rls_insertar_una_cuenta_de_otra_empresa_lanza_error(conexion: Connection) -> None:
    # Arrange: la sesión es de A y la cuenta dice que es de B
    entrar_como_la_api(conexion, EMPRESA_A)
    insertar = text(
        "INSERT INTO cuentas (empresa_id, codigo, nombre, naturaleza, es_detalle) "
        "VALUES (:b, '5301', 'Vigilancia', 'GASTO', true)"
    )
    # Act / Assert
    with pytest.raises(DBAPIError, match="row-level security"):
        conexion.execute(insertar, {"b": EMPRESA_B})
