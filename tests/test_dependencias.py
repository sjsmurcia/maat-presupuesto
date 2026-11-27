import tomllib
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]


def _de_requirements() -> set[str]:
    lineas = (RAIZ / "requirements.txt").read_text(encoding="utf-8").splitlines()
    return {linea.strip() for linea in lineas if linea.strip() and not linea.startswith("#")}


def _de_pyproject() -> set[str]:
    with (RAIZ / "pyproject.toml").open("rb") as archivo:
        return set(tomllib.load(archivo)["project"]["dependencies"])


def test_dependencias_pyproject_y_requirements_son_las_mismas() -> None:
    # Vercel instala desde pyproject.toml y el CI desde requirements.txt
    assert _de_pyproject() == _de_requirements()
