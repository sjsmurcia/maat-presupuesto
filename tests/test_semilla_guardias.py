"""Las guardias de la semilla demo: sin base de datos (la siembra se reemplaza por un espía)."""

import secrets

import pytest

import scripts.semilla_demo as semilla
from scripts.semilla_demo import (
    LARGO_MIN_FUERA_DE_DEV,
    PASSWORD_DEFAULT,
    SALIDA_ABORTADA,
    VARIABLE_PASSWORD,
    SemillaAbortada,
    password_de_semilla,
    verificar_entorno,
)

PROPIA = secrets.token_hex(LARGO_MIN_FUERA_DE_DEV)  # 32 letras y números, ningún literal
EN_AZURE = {"MP_ENTORNO": "azure", "MP_SEMILLA_PERMITIR": "azure", "DATABASE_URL": "postgresql://x@h/db"}


@pytest.mark.parametrize(
    ("entorno", "variables"),
    [("dev", {}), ("azure", {"MP_SEMILLA_PERMITIR": "azure"})],
)
def test_verificar_entorno_en_dev_o_con_permiso_del_entorno_no_lanza(
    entorno: str, variables: dict[str, str]
) -> None:
    verificar_entorno(entorno, variables)


@pytest.mark.parametrize("variables", [{}, {"MP_SEMILLA_PERMITIR": "staging"}])
def test_verificar_entorno_fuera_de_dev_sin_su_permiso_lanza_error(variables: dict[str, str]) -> None:
    with pytest.raises(SemillaAbortada, match="MP_SEMILLA_PERMITIR=azure"):
        verificar_entorno("azure", variables)


@pytest.mark.parametrize(
    ("argv", "esperada"), [(["semilla"], PASSWORD_DEFAULT), (["semilla", PROPIA], PROPIA)]
)
def test_password_de_semilla_en_dev_usa_el_argumento_o_la_del_repo(
    argv: list[str], esperada: str
) -> None:
    assert password_de_semilla("dev", argv, {}) == esperada


@pytest.mark.parametrize(
    ("argv", "variables", "mensaje"),
    [
        (["semilla"], {}, f"sale de {VARIABLE_PASSWORD}"),
        (["semilla", PROPIA], {VARIABLE_PASSWORD: PROPIA}, "línea de comandos"),
        (["semilla"], {VARIABLE_PASSWORD: PASSWORD_DEFAULT}, "está en el repo"),
        (["semilla"], {VARIABLE_PASSWORD: PROPIA[:15]}, f"pide {LARGO_MIN_FUERA_DE_DEV} o más"),
    ],
)
def test_password_de_semilla_fuera_de_dev_sin_una_propia_y_larga_lanza_error(
    argv: list[str], variables: dict[str, str], mensaje: str
) -> None:
    with pytest.raises(SemillaAbortada, match=mensaje):
        password_de_semilla("azure", argv, variables)


def test_password_de_semilla_fuera_de_dev_usa_la_variable() -> None:
    assert password_de_semilla("azure", ["semilla"], {VARIABLE_PASSWORD: PROPIA}) == PROPIA


@pytest.fixture
def sembradas(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    """Espía de la siembra: anota con qué contraseña se habría sembrado."""
    anotadas: list[str] = []
    monkeypatch.setattr(semilla, "sembrar_en_la_base", lambda _url, password: anotadas.append(password))
    return anotadas


def test_main_fuera_de_dev_siembra_con_la_variable_y_no_la_imprime(
    sembradas: list[str], capsys: pytest.CaptureFixture[str]
) -> None:
    # Act
    semilla.main(["semilla"], {**EN_AZURE, VARIABLE_PASSWORD: PROPIA})
    # Assert: primero que el resumen se imprimió, después que no trae la contraseña
    salida = capsys.readouterr()
    assert "Semilla creada" in salida.out
    assert PROPIA not in salida.out + salida.err
    assert sembradas == [PROPIA]


def test_main_sin_permiso_sale_con_codigo_2_y_no_siembra(
    sembradas: list[str], capsys: pytest.CaptureFixture[str]
) -> None:
    # Arrange
    sin_permiso = {"MP_ENTORNO": "azure", VARIABLE_PASSWORD: PROPIA}
    # Act
    with pytest.raises(SystemExit) as salida:
        semilla.main(["semilla"], sin_permiso)
    # Assert
    assert salida.value.code == SALIDA_ABORTADA
    assert "ABORTADO" in capsys.readouterr().out
    assert sembradas == []
