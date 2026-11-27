import uuid
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from backend.app import app
from backend.cuentas import cuenta_a_json
from backend.db.modelos import Cuenta
from backend.db.sesion import sesion_de_la_api
from tests.api.datos_de_prueba import (
    ANALISTA,
    EMPRESA_C,
    EMPRESA_D,
    RESPONSABLE,
    encabezado_de,
)


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


def test_listar_cuentas_con_id_que_no_es_uuid_devuelve_422(cliente_sin_base: TestClient) -> None:
    # Act
    respuesta = cliente_sin_base.get(
        "/api/empresas/no-es-un-uuid/cuentas", headers=encabezado_de(ANALISTA)
    )
    # Assert
    assert respuesta.status_code == 422


def test_listar_cuentas_sin_token_devuelve_401(cliente_sin_base: TestClient) -> None:
    # Act
    respuesta = cliente_sin_base.get(f"/api/empresas/{EMPRESA_C}/cuentas")
    # Assert
    assert respuesta.status_code == 401


def test_listar_cuentas_de_la_empresa_devuelve_sus_cuentas_con_recibe_presupuesto(
    cliente: TestClient,
) -> None:
    # Act
    respuesta = cliente.get(f"/api/empresas/{EMPRESA_C}/cuentas", headers=encabezado_de(ANALISTA))
    # Assert
    assert respuesta.status_code == 200
    assert [(c["codigo"], c["recibe_presupuesto"]) for c in respuesta.json()] == [
        ("5", False),
        ("5204", True),
        ("5299", False),
    ]


def test_listar_cuentas_de_otra_empresa_no_devuelve_las_de_la_primera(cliente: TestClient) -> None:
    # Act: el responsable solo tiene acceso a la empresa D
    respuesta = cliente.get(
        f"/api/empresas/{EMPRESA_D}/cuentas", headers=encabezado_de(RESPONSABLE)
    )
    # Assert
    assert [cuenta["codigo"] for cuenta in respuesta.json()] == ["4101"]


@pytest.mark.parametrize(
    "empresa", [EMPRESA_D, uuid.UUID("00000000-0000-0000-0000-0000000000ff")]
)
def test_listar_cuentas_de_empresa_sin_acceso_o_inexistente_devuelve_el_mismo_404(
    cliente: TestClient, empresa: uuid.UUID
) -> None:
    # Act: el analista no tiene acceso a D, y la otra no existe
    respuesta = cliente.get(f"/api/empresas/{empresa}/cuentas", headers=encabezado_de(ANALISTA))
    # Assert: no se revela si la empresa existe
    assert respuesta.status_code == 404
    assert respuesta.json() == {"mensaje": f"No existe la empresa {empresa}"}
