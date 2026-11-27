"""Las tablas de la base como modelos de SQLAlchemy, igual que en Maat.

El dominio (`presupuesto/`) no los conoce: un adaptador los traduce a sus datos.
La migración 0001 crea estas mismas tablas, y un test revisa que no se separen.
"""

import uuid

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    String,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

NATURALEZAS = ("ACTIVO", "PASIVO", "PATRIMONIO", "INGRESO", "COSTO", "GASTO")
TIPOS_DE_CENTRO = ("ESPECIFICO", "GENERICO", "INSTITUCIONAL", "CEBE")
UUID_NUEVO = text("gen_random_uuid()")


def _valores_sql(valores: tuple[str, ...]) -> str:
    return ", ".join(f"'{valor}'" for valor in valores)


class Base(DeclarativeBase):
    pass


class Empresa(Base):
    __tablename__ = "empresas"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, server_default=UUID_NUEVO)
    nombre: Mapped[str] = mapped_column(String(200))


class Area(Base):
    __tablename__ = "areas"
    # (empresa_id, id) es único para que el área superior y el área de un centro
    # se puedan amarrar a la misma empresa con una llave foránea compuesta.
    __table_args__ = (
        UniqueConstraint("empresa_id", "nombre"),
        UniqueConstraint("empresa_id", "id"),
        ForeignKeyConstraint(
            ["empresa_id", "area_superior_id"], ["areas.empresa_id", "areas.id"]
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, server_default=UUID_NUEVO)
    empresa_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("empresas.id"))
    nombre: Mapped[str] = mapped_column(String(200))
    area_superior_id: Mapped[uuid.UUID | None]


class Cuenta(Base):
    __tablename__ = "cuentas"
    __table_args__ = (
        ForeignKeyConstraint(
            ["empresa_id", "codigo_superior"], ["cuentas.empresa_id", "cuentas.codigo"]
        ),
        CheckConstraint(
            f"naturaleza IN ({_valores_sql(NATURALEZAS)})", name="ck_cuentas_naturaleza"
        ),
        Index("ix_cuentas_empresa_id_codigo_superior", "empresa_id", "codigo_superior"),
    )

    empresa_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("empresas.id"), primary_key=True)
    codigo: Mapped[str] = mapped_column(String(30), primary_key=True)
    nombre: Mapped[str] = mapped_column(String(200))
    codigo_superior: Mapped[str | None] = mapped_column(String(30))
    naturaleza: Mapped[str] = mapped_column(String(12))
    es_detalle: Mapped[bool]
    activa: Mapped[bool] = mapped_column(server_default=text("true"))


class Centro(Base):
    __tablename__ = "centros"
    __table_args__ = (
        ForeignKeyConstraint(
            ["empresa_id", "codigo_superior"], ["centros.empresa_id", "centros.codigo"]
        ),
        ForeignKeyConstraint(["empresa_id", "area_id"], ["areas.empresa_id", "areas.id"]),
        CheckConstraint(f"tipo IN ({_valores_sql(TIPOS_DE_CENTRO)})", name="ck_centros_tipo"),
        Index("ix_centros_empresa_id_area_id", "empresa_id", "area_id"),
    )

    empresa_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("empresas.id"), primary_key=True)
    codigo: Mapped[str] = mapped_column(String(30), primary_key=True)
    nombre: Mapped[str] = mapped_column(String(200))
    codigo_superior: Mapped[str | None] = mapped_column(String(30))
    tipo: Mapped[str] = mapped_column(String(15))
    area_id: Mapped[uuid.UUID]
