from typing import Annotated, Any

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app import app
from backend.errores import ErrorDeLaApi, responder_error
from backend.permisos import requiere_permiso
from tests.api.datos_de_prueba import (
    ANALISTA,
    AREA_D,
    EMPRESA_C,
    EMPRESA_D,
    RESPONSABLE,
    encabezado_de,
)

SIN_EJERCICIOS = {"ejercicio_actual": None, "mes_abierto": None, "estado_presupuesto": None}

# Ninguna ruta pide todavía un permiso: esta app chica prueba la dependencia sola.
app_de_prueba = FastAPI()
app_de_prueba.add_exception_handler(ErrorDeLaApi, responder_error)


@app_de_prueba.get("/empresas/{empresa_id}/editar")
def editar(_sesion: Annotated[Session, Depends(requiere_permiso("catalogo.editar"))]) -> Any:
    return {"editado": True}


@pytest.fixture
def cliente_de_prueba(cliente: TestClient) -> TestClient:
    app_de_prueba.dependency_overrides = app.dependency_overrides  # la misma base y el mismo rol
    return TestClient(app_de_prueba)


def test_listar_empresas_del_analista_trae_su_rol_y_los_nueve_permisos(cliente: TestClient) -> None:
    # Act
    respuesta = cliente.get("/api/empresas", headers=encabezado_de(ANALISTA))
    # Assert
    assert respuesta.json() == [
        {
            "id": str(EMPRESA_C),
            "nombre": "Empresa C",
            "rol": {"codigo": "analista", "nombre": "Analista de presupuesto"},
            "permisos": [
                "catalogo.editar", "cierre.ejecutar", "presupuesto.ajustar",
                "presupuesto.aprobar", "presupuesto.editar", "presupuesto.ver",
                "real.cargar", "reglas.editar", "tablero.ver",
            ],
            "areas": None,
            **SIN_EJERCICIOS,
        }
    ]


def test_listar_empresas_del_responsable_trae_sus_areas_y_solo_ver(cliente: TestClient) -> None:
    # Act
    empresas = cliente.get("/api/empresas", headers=encabezado_de(RESPONSABLE)).json()
    # Assert
    assert [(e["id"], e["permisos"], e["areas"]) for e in empresas] == [
        (str(EMPRESA_D), ["presupuesto.ver", "tablero.ver"], [str(AREA_D)])
    ]


def test_listar_empresas_sin_token_devuelve_401(cliente: TestClient) -> None:
    assert cliente.get("/api/empresas").status_code == 401


def test_requiere_permiso_con_el_permiso_deja_pasar(cliente_de_prueba: TestClient) -> None:
    # Act
    respuesta = cliente_de_prueba.get(
        f"/empresas/{EMPRESA_C}/editar", headers=encabezado_de(ANALISTA)
    )
    # Assert
    assert respuesta.json() == {"editado": True}


def test_requiere_permiso_sin_el_permiso_devuelve_403(cliente_de_prueba: TestClient) -> None:
    # Act: el responsable entra a su empresa, pero no puede editar el catálogo
    respuesta = cliente_de_prueba.get(
        f"/empresas/{EMPRESA_D}/editar", headers=encabezado_de(RESPONSABLE)
    )
    # Assert
    assert respuesta.status_code == 403
    assert respuesta.json() == {"mensaje": "Te falta el permiso catalogo.editar en esta empresa"}
