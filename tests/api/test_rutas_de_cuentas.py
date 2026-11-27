import uuid
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from backend.app import app
from backend.cuentas import cuenta_a_json
from backend.db.modelos import Cuenta
from backend.db.sesion import sesion_de_la_api
from tests.api.datos_de_prueba import EMPRESA_C, EMPRESA_D


def _cuenta(es_detalle: bool, activa: bool, naturaleza: str = "GASTO") -> Cuenta:
    return Cuenta(
        empresa_id=EMPRESA_C,
        codigo="5204",
        nombre="Servicios en la nube",
        codigo_superior="5",
        naturaleza=naturaleza,
        es_detalle=es_detalle,
        activa=activa,
    )


@pytest.mark.parametrize(
    ("cuenta", "esperado"),
    [
        (_cuenta(es_detalle=True, activa=True), True),
        (_cuenta(es_detalle=False, activa=True), False),
        (_cuenta(es_detalle=True, activa=False), False),
        (_cuenta(es_detalle=True, activa=True, naturaleza="ACTIVO"), False),
    ],
)
def test_cuenta_a_json_recibe_presupuesto_lo_decide_el_dominio(
    cuenta: Cuenta, esperado: bool
) -> None:
    # Act
    json = cuenta_a_json(cuenta)
    # Assert
    assert json["recibe_presupuesto"] is esperado


def test_cuenta_a_json_trae_los_campos_del_handoff() -> None:
    # Act
    json = cuenta_a_json(_cuenta(es_detalle=True, activa=True))
    # Assert
    assert json == {
        "codigo": "5204",
        "nombre": "Servicios en la nube",
        "codigo_superior": "5",
        "naturaleza": "GASTO",
        "es_detalle": True,
        "activa": True,
        "recibe_presupuesto": True,
    }


@pytest.fixture
def cliente_sin_base() -> Iterator[TestClient]:
    app.dependency_overrides[sesion_de_la_api] = lambda: None
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_listar_cuentas_con_id_que_no_es_uuid_devuelve_422(cliente_sin_base: TestClient) -> None:
    # Act
    respuesta = cliente_sin_base.get("/api/empresas/no-es-un-uuid/cuentas")
    # Assert
    assert respuesta.status_code == 422


def test_listar_cuentas_de_la_empresa_devuelve_sus_cuentas_con_recibe_presupuesto(
    cliente: TestClient,
) -> None:
    # Act
    respuesta = cliente.get(f"/api/empresas/{EMPRESA_C}/cuentas")
    # Assert
    assert respuesta.status_code == 200
    assert [(c["codigo"], c["recibe_presupuesto"]) for c in respuesta.json()] == [
        ("5", False),
        ("5204", True),
        ("5299", False),
    ]


def test_listar_cuentas_de_otra_empresa_no_devuelve_las_de_la_primera(cliente: TestClient) -> None:
    # Act
    respuesta = cliente.get(f"/api/empresas/{EMPRESA_D}/cuentas")
    # Assert
    assert [cuenta["codigo"] for cuenta in respuesta.json()] == ["4101"]


def test_listar_cuentas_con_empresa_inexistente_devuelve_404(cliente: TestClient) -> None:
    # Arrange
    inexistente = uuid.UUID("00000000-0000-0000-0000-0000000000ff")
    # Act
    respuesta = cliente.get(f"/api/empresas/{inexistente}/cuentas")
    # Assert
    assert respuesta.status_code == 404
    assert respuesta.json() == {"mensaje": f"No existe la empresa {inexistente}"}
