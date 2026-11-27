from fastapi.testclient import TestClient

from backend.app import app


def test_salud_sin_base_responde_ok() -> None:
    # Act
    respuesta = TestClient(app).get("/api/salud")
    # Assert
    assert respuesta.status_code == 200
    assert respuesta.json() == {"estado": "ok"}
