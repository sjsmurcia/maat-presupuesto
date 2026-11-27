import pytest

from backend.db.conexion import leer_url_de_la_base


@pytest.mark.parametrize(
    "url",
    [
        "postgresql://maat@servidor:5432/presupuesto",
        "postgres://maat@servidor:5432/presupuesto",
        "postgresql+psycopg://maat@servidor:5432/presupuesto",
    ],
)
def test_leer_url_de_la_base_con_cualquier_esquema_usa_psycopg(url: str) -> None:
    # Act
    leida = leer_url_de_la_base({"DATABASE_URL": url})
    # Assert
    assert leida == "postgresql+psycopg://maat@servidor:5432/presupuesto"


@pytest.mark.parametrize("entorno", [{}, {"DATABASE_URL": "  "}])
def test_leer_url_de_la_base_sin_la_variable_lanza_error(entorno: dict[str, str]) -> None:
    with pytest.raises(RuntimeError, match="Falta la variable de entorno DATABASE_URL"):
        leer_url_de_la_base(entorno)
