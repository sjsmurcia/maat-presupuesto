"""La sesión de la base que recibe cada petición de la API."""

import os
from collections.abc import Iterator
from functools import cache

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import NullPool

from backend.db.conexion import leer_url_de_la_base


@cache
def motor_de_la_api() -> Engine:
    """Se crea en la primera petición que lo usa, así /api/salud responde sin base.

    Sin pool de conexiones: en Vercel cada invocación es efímera (ADR-1).
    """
    return create_engine(leer_url_de_la_base(os.environ), poolclass=NullPool)


def sesion_de_la_api() -> Iterator[Session]:
    with Session(motor_de_la_api()) as sesion:
        yield sesion
