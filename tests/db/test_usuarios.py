import uuid

import pytest
from sqlalchemy import Connection, text
from sqlalchemy.exc import IntegrityError

from tests.db.base_de_pruebas import EMPRESA_A, EMPRESA_B, ROL_SIN_BYPASS

USUARIO = uuid.UUID("00000000-0000-0000-0000-0000000000a1")
AREA_DE_B = uuid.UUID("00000000-0000-0000-0000-0000000000b1")


def _permisos_del_rol(conexion: Connection, rol: str) -> list[str]:
    consulta = text(
        "SELECT p.codigo FROM roles r JOIN roles_permisos rp ON rp.rol_id = r.id"
        " JOIN permisos p ON p.id = rp.permiso_id WHERE r.codigo = :rol ORDER BY p.codigo"
    )
    return list(conexion.scalars(consulta, {"rol": rol}))


def _dar_acceso(conexion: Connection, empresa_id: uuid.UUID) -> uuid.UUID:
    conexion.execute(
        text("INSERT INTO usuarios (id, email, hash_password) VALUES (:u, 'a@ejemplo.edu', 'x')"),
        {"u": USUARIO},
    )
    return conexion.scalar(
        text(
            "INSERT INTO accesos (usuario_id, empresa_id, rol_id)"
            " SELECT :u, :e, id FROM roles WHERE codigo = 'responsable' RETURNING id"
        ),
        {"u": USUARIO, "e": empresa_id},
    )


def test_usuarios_el_analista_tiene_los_nueve_permisos(conexion: Connection) -> None:
    # Act
    permisos = _permisos_del_rol(conexion, "analista")
    # Assert
    assert permisos == [
        "catalogo.editar", "cierre.ejecutar", "presupuesto.ajustar", "presupuesto.aprobar",
        "presupuesto.editar", "presupuesto.ver", "real.cargar", "reglas.editar", "tablero.ver",
    ]


def test_usuarios_el_responsable_solo_ve_presupuesto_y_tablero(conexion: Connection) -> None:
    # Act
    permisos = _permisos_del_rol(conexion, "responsable")
    # Assert
    assert permisos == ["presupuesto.ver", "tablero.ver"]


def test_usuarios_area_de_otra_empresa_en_un_acceso_lanza_error(conexion: Connection) -> None:
    # Arrange: el acceso es de la empresa A y el área es de la B
    acceso = _dar_acceso(conexion, EMPRESA_A)
    conexion.execute(
        text("INSERT INTO areas (id, empresa_id, codigo, nombre) VALUES (:a, :b, 'TI', 'TI')"),
        {"a": AREA_DE_B, "b": EMPRESA_B},
    )
    insertar = text(
        "INSERT INTO accesos_areas (acceso_id, empresa_id, area_id) VALUES (:acc, :a, :area)"
    )
    # Act / Assert
    with pytest.raises(IntegrityError, match="accesos_areas"):
        conexion.execute(insertar, {"acc": acceso, "a": EMPRESA_A, "area": AREA_DE_B})


def test_usuarios_con_el_usuario_en_la_sesion_solo_ve_las_empresas_de_sus_accesos(
    conexion: Connection,
) -> None:
    # Arrange: tiene acceso a A y no a B, y todavía no eligió empresa
    _dar_acceso(conexion, EMPRESA_A)
    conexion.execute(text(f"SET LOCAL ROLE {ROL_SIN_BYPASS}"))
    conexion.execute(text("SELECT set_config('app.usuario_id', :u, true)"), {"u": str(USUARIO)})
    # Act
    empresas = list(conexion.scalars(text("SELECT id FROM empresas")))
    # Assert
    assert empresas == [EMPRESA_A]
