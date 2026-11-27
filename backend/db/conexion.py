"""De dónde sale la URL de la base: siempre del entorno, nunca del repo."""

from collections.abc import Mapping

_ESQUEMAS_SIN_DRIVER = ("postgresql://", "postgres://")
_ESQUEMA_CON_PSYCOPG = "postgresql+psycopg://"


def leer_url_de_la_base(entorno: Mapping[str, str], variable: str = "DATABASE_URL") -> str:
    """Devuelve la URL de `variable` lista para SQLAlchemy con psycopg 3.

    Azure y Vercel la dan como `postgresql://…`, y SQLAlchemy usaría psycopg2 con ese esquema.
    """
    url = entorno.get(variable, "").strip()
    if not url:
        raise RuntimeError(f"Falta la variable de entorno {variable} con la URL de la base")
    for esquema in _ESQUEMAS_SIN_DRIVER:
        if url.startswith(esquema):
            return _ESQUEMA_CON_PSYCOPG + url.removeprefix(esquema)
    return url
