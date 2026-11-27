"""Empresas, áreas, cuentas y centros, separados por empresa con RLS.

Revision ID: 0001
Revises:
Create Date: 2026-11-26
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

UUID_NUEVO = sa.text("gen_random_uuid()")
TABLAS_POR_EMPRESA = ("areas", "cuentas", "centros")
# La API hace SET LOCAL app.empresa_id en cada transacción. Sin ese dato no se ve nada;
# NULLIF evita el error de convertir '' a uuid cuando el dato quedó vacío en la sesión.
EMPRESA_DE_LA_SESION = "NULLIF(current_setting('app.empresa_id', true), '')::uuid"


def upgrade() -> None:
    _crear_empresas_y_areas()
    _crear_cuentas()
    _crear_centros()
    _activar_rls()


def downgrade() -> None:
    for tabla in ("centros", "cuentas", "areas", "empresas"):
        op.drop_table(tabla)


def _crear_empresas_y_areas() -> None:
    op.create_table(
        "empresas",
        sa.Column("id", sa.Uuid(), primary_key=True, server_default=UUID_NUEVO),
        sa.Column("nombre", sa.String(200), nullable=False),
    )
    op.create_table(
        "areas",
        sa.Column("id", sa.Uuid(), primary_key=True, server_default=UUID_NUEVO),
        sa.Column("empresa_id", sa.Uuid(), sa.ForeignKey("empresas.id"), nullable=False),
        sa.Column("nombre", sa.String(200), nullable=False),
        sa.Column("area_superior_id", sa.Uuid(), nullable=True),
        sa.UniqueConstraint("empresa_id", "nombre"),
        sa.UniqueConstraint("empresa_id", "id"),
        sa.ForeignKeyConstraint(
            ["empresa_id", "area_superior_id"], ["areas.empresa_id", "areas.id"]
        ),
    )


def _crear_cuentas() -> None:
    op.create_table(
        "cuentas",
        sa.Column("empresa_id", sa.Uuid(), sa.ForeignKey("empresas.id"), primary_key=True),
        sa.Column("codigo", sa.String(30), primary_key=True),
        sa.Column("nombre", sa.String(200), nullable=False),
        sa.Column("codigo_superior", sa.String(30), nullable=True),
        sa.Column("naturaleza", sa.String(12), nullable=False),
        sa.Column("es_detalle", sa.Boolean(), nullable=False),
        sa.Column("activa", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.ForeignKeyConstraint(
            ["empresa_id", "codigo_superior"], ["cuentas.empresa_id", "cuentas.codigo"]
        ),
        sa.CheckConstraint(
            "naturaleza IN ('ACTIVO', 'PASIVO', 'PATRIMONIO', 'INGRESO', 'COSTO', 'GASTO')",
            name="ck_cuentas_naturaleza",
        ),
    )
    op.create_index(
        "ix_cuentas_empresa_id_codigo_superior", "cuentas", ["empresa_id", "codigo_superior"]
    )


def _crear_centros() -> None:
    op.create_table(
        "centros",
        sa.Column("empresa_id", sa.Uuid(), sa.ForeignKey("empresas.id"), primary_key=True),
        sa.Column("codigo", sa.String(30), primary_key=True),
        sa.Column("nombre", sa.String(200), nullable=False),
        sa.Column("codigo_superior", sa.String(30), nullable=True),
        sa.Column("tipo", sa.String(15), nullable=False),
        sa.Column("area_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(
            ["empresa_id", "codigo_superior"], ["centros.empresa_id", "centros.codigo"]
        ),
        sa.ForeignKeyConstraint(["empresa_id", "area_id"], ["areas.empresa_id", "areas.id"]),
        sa.CheckConstraint(
            "tipo IN ('ESPECIFICO', 'GENERICO', 'INSTITUCIONAL', 'CEBE')", name="ck_centros_tipo"
        ),
    )
    op.create_index("ix_centros_empresa_id_area_id", "centros", ["empresa_id", "area_id"])


def _activar_rls() -> None:
    # FORCE hace que la regla valga también para el dueño de las tablas: si la API se
    # conecta con ese usuario, igual queda filtrada por empresa.
    politicas = {tabla: "empresa_id" for tabla in TABLAS_POR_EMPRESA} | {"empresas": "id"}
    for tabla, columna in politicas.items():
        condicion = f"{columna} = {EMPRESA_DE_LA_SESION}"
        op.execute(f"ALTER TABLE {tabla} ENABLE ROW LEVEL SECURITY")
        op.execute(f"ALTER TABLE {tabla} FORCE ROW LEVEL SECURITY")
        op.execute(
            f"CREATE POLICY por_empresa ON {tabla} USING ({condicion}) WITH CHECK ({condicion})"
        )
