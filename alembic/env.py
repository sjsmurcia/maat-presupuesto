import os
from logging.config import fileConfig

from sqlalchemy import create_engine, pool

from alembic import context
from backend.db.conexion import leer_url_de_la_base
from backend.db.modelos import Base

if context.config.config_file_name is not None:
    fileConfig(context.config.config_file_name)


def correr_sin_conexion() -> None:
    context.configure(
        url=leer_url_de_la_base(os.environ),
        target_metadata=Base.metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def correr_con_conexion() -> None:
    motor = create_engine(leer_url_de_la_base(os.environ), poolclass=pool.NullPool)
    with motor.connect() as conexion:
        context.configure(connection=conexion, target_metadata=Base.metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    correr_sin_conexion()
else:
    correr_con_conexion()
