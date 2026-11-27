"""Las tablas de la base como modelos de SQLAlchemy, igual que en Maat.

El dominio (`presupuesto/`) no los conoce: un adaptador los traduce a sus datos.
La migración 0001 crea estas mismas tablas, y un test revisa que no se separen.
"""

import uuid
from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    String,
    Text,
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
        UniqueConstraint("empresa_id", "codigo"),
        UniqueConstraint("empresa_id", "nombre"),
        UniqueConstraint("empresa_id", "id"),
        ForeignKeyConstraint(
            ["empresa_id", "area_superior_id"], ["areas.empresa_id", "areas.id"]
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, server_default=UUID_NUEVO)
    empresa_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("empresas.id"))
    codigo: Mapped[str] = mapped_column(String(30))
    nombre: Mapped[str] = mapped_column(String(200))
    area_superior_id: Mapped[uuid.UUID | None]
    activa: Mapped[bool] = mapped_column(server_default=text("true"))


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
    activo: Mapped[bool] = mapped_column(server_default=text("true"))


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, server_default=UUID_NUEVO)
    # la API lo guarda en minúsculas: CITEXT pediría habilitar la extensión en Azure
    email: Mapped[str] = mapped_column(String(320), unique=True)
    hash_password: Mapped[str] = mapped_column(Text)  # Argon2id, nunca la contraseña
    activo: Mapped[bool] = mapped_column(server_default=text("true"))


class Rol(Base):
    __tablename__ = "roles"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, server_default=UUID_NUEVO)
    codigo: Mapped[str] = mapped_column(String(50), unique=True)
    nombre: Mapped[str] = mapped_column(String(200))
    es_sistema: Mapped[bool] = mapped_column(server_default=text("false"))
    activo: Mapped[bool] = mapped_column(server_default=text("true"))


class Permiso(Base):
    __tablename__ = "permisos"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, server_default=UUID_NUEVO)
    codigo: Mapped[str] = mapped_column(String(50), unique=True)
    nombre: Mapped[str] = mapped_column(String(200))
    descripcion: Mapped[str | None] = mapped_column(Text)


class RolPermiso(Base):
    __tablename__ = "roles_permisos"
    __table_args__ = (UniqueConstraint("rol_id", "permiso_id"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, server_default=UUID_NUEVO)
    rol_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("roles.id"))
    permiso_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("permisos.id"))


class Acceso(Base):
    """El rol de un usuario en una empresa: uno por usuario y empresa."""

    __tablename__ = "accesos"
    # (id, empresa_id) es único para que las áreas de un acceso sean de su misma empresa
    __table_args__ = (
        UniqueConstraint("usuario_id", "empresa_id"),
        UniqueConstraint("id", "empresa_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, server_default=UUID_NUEVO)
    usuario_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("usuarios.id"), index=True)
    empresa_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("empresas.id"), index=True)
    rol_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("roles.id"))
    activo: Mapped[bool] = mapped_column(server_default=text("true"))


class AccesoArea(Base):
    """Las áreas que ve un acceso; un acceso sin áreas ve todas (decisión 52)."""

    __tablename__ = "accesos_areas"
    __table_args__ = (
        UniqueConstraint("acceso_id", "area_id"),
        ForeignKeyConstraint(["acceso_id", "empresa_id"], ["accesos.id", "accesos.empresa_id"]),
        ForeignKeyConstraint(["empresa_id", "area_id"], ["areas.empresa_id", "areas.id"]),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, server_default=UUID_NUEVO)
    acceso_id: Mapped[uuid.UUID]
    empresa_id: Mapped[uuid.UUID]
    area_id: Mapped[uuid.UUID]


class Sesion(Base):
    """Un refresh token revocable; el access token es un JWT que no se guarda."""

    __tablename__ = "sesiones"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, server_default=UUID_NUEVO)
    usuario_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("usuarios.id"), index=True)
    refresh_token_hash: Mapped[str] = mapped_column(Text)  # solo el hash, nunca el token
    emitido_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()")
    )
    expira_en: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    revocado_en: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
