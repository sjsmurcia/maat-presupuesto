"""Usuarios, roles, permisos, accesos y sesiones, con la forma de los de Maat (50 a 52).

Revision ID: 0002
Revises: 0001
Create Date: 2026-11-27
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

UUID_NUEVO = sa.text("gen_random_uuid()")
VERDADERO = sa.text("true")
PERMISOS = (
    ("catalogo.editar", "Editar los catálogos"),
    ("reglas.editar", "Editar las reglas y las bases"),
    ("presupuesto.ver", "Ver el presupuesto"),
    ("presupuesto.editar", "Capturar el presupuesto"),
    ("presupuesto.aprobar", "Aprobar el presupuesto"),
    ("presupuesto.ajustar", "Ajustar el presupuesto aprobado"),
    ("real.cargar", "Cargar lo real"),
    ("cierre.ejecutar", "Cerrar el mes"),
    ("tablero.ver", "Ver el tablero"),
)
DEL_RESPONSABLE = ("presupuesto.ver", "tablero.ver")
# El login no elige empresa todavía: la API dice quién es el usuario y la base le deja
# ver solo las empresas donde tiene un acceso activo, además de la de la sesión (0001).
EMPRESAS_DEL_USUARIO = (
    "id IN (SELECT empresa_id FROM accesos WHERE activo"
    " AND usuario_id = NULLIF(current_setting('app.usuario_id', true), '')::uuid)"
)


def upgrade() -> None:
    _crear_usuarios_roles_y_permisos()
    _crear_accesos()
    _crear_sesiones()
    _sembrar_permisos_y_roles()
    op.execute(f"CREATE POLICY por_usuario ON empresas FOR SELECT USING ({EMPRESAS_DEL_USUARIO})")


def downgrade() -> None:
    op.execute("DROP POLICY por_usuario ON empresas")
    for tabla in (
        "sesiones", "accesos_areas", "accesos", "roles_permisos", "permisos", "roles", "usuarios"
    ):
        op.drop_table(tabla)


def _id() -> sa.Column:
    return sa.Column("id", sa.Uuid(), primary_key=True, server_default=UUID_NUEVO)


def _crear_usuarios_roles_y_permisos() -> None:
    op.create_table(
        "usuarios",
        _id(),
        sa.Column("email", sa.String(320), nullable=False, unique=True),
        sa.Column("hash_password", sa.Text(), nullable=False),
        sa.Column("activo", sa.Boolean(), nullable=False, server_default=VERDADERO),
    )
    op.create_table(
        "roles",
        _id(),
        sa.Column("codigo", sa.String(50), nullable=False, unique=True),
        sa.Column("nombre", sa.String(200), nullable=False),
        sa.Column("es_sistema", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("activo", sa.Boolean(), nullable=False, server_default=VERDADERO),
    )
    op.create_table(
        "permisos",
        _id(),
        sa.Column("codigo", sa.String(50), nullable=False, unique=True),
        sa.Column("nombre", sa.String(200), nullable=False),
        sa.Column("descripcion", sa.Text(), nullable=True),
    )
    op.create_table(
        "roles_permisos",
        _id(),
        sa.Column("rol_id", sa.Uuid(), sa.ForeignKey("roles.id"), nullable=False),
        sa.Column("permiso_id", sa.Uuid(), sa.ForeignKey("permisos.id"), nullable=False),
        sa.UniqueConstraint("rol_id", "permiso_id"),
    )


def _crear_accesos() -> None:
    op.create_table(
        "accesos",
        _id(),
        sa.Column("usuario_id", sa.Uuid(), sa.ForeignKey("usuarios.id"), nullable=False),
        sa.Column("empresa_id", sa.Uuid(), sa.ForeignKey("empresas.id"), nullable=False),
        sa.Column("rol_id", sa.Uuid(), sa.ForeignKey("roles.id"), nullable=False),
        sa.Column("activo", sa.Boolean(), nullable=False, server_default=VERDADERO),
        sa.UniqueConstraint("usuario_id", "empresa_id"),
        sa.UniqueConstraint("id", "empresa_id"),
    )
    op.create_index("ix_accesos_usuario_id", "accesos", ["usuario_id"])
    op.create_index("ix_accesos_empresa_id", "accesos", ["empresa_id"])
    op.create_table(
        "accesos_areas",
        _id(),
        sa.Column("acceso_id", sa.Uuid(), nullable=False),
        sa.Column("empresa_id", sa.Uuid(), nullable=False),
        sa.Column("area_id", sa.Uuid(), nullable=False),
        sa.UniqueConstraint("acceso_id", "area_id"),
        sa.ForeignKeyConstraint(["acceso_id", "empresa_id"], ["accesos.id", "accesos.empresa_id"]),
        sa.ForeignKeyConstraint(["empresa_id", "area_id"], ["areas.empresa_id", "areas.id"]),
    )


def _crear_sesiones() -> None:
    op.create_table(
        "sesiones",
        _id(),
        sa.Column("usuario_id", sa.Uuid(), sa.ForeignKey("usuarios.id"), nullable=False),
        sa.Column("refresh_token_hash", sa.Text(), nullable=False),
        sa.Column(
            "emitido_en", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")
        ),
        sa.Column("expira_en", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revocado_en", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_sesiones_usuario_id", "sesiones", ["usuario_id"])


def _sembrar_permisos_y_roles() -> None:
    permisos = ", ".join(f"('{codigo}', '{nombre}')" for codigo, nombre in PERMISOS)
    op.execute(f"INSERT INTO permisos (codigo, nombre) VALUES {permisos}")
    op.execute(
        "INSERT INTO roles (codigo, nombre, es_sistema) VALUES"
        " ('analista', 'Analista de presupuesto', true),"
        " ('responsable', 'Responsable de área', true)"
    )
    del_responsable = ", ".join(f"'{codigo}'" for codigo in DEL_RESPONSABLE)
    op.execute(
        "INSERT INTO roles_permisos (rol_id, permiso_id)"
        " SELECT r.id, p.id FROM roles r CROSS JOIN permisos p"
        " WHERE r.codigo = 'analista'"
        f" OR (r.codigo = 'responsable' AND p.codigo IN ({del_responsable}))"
    )
