"""Un error de la API: la pantalla muestra su mensaje tal cual (handoff)."""

from fastapi import Request
from fastapi.responses import JSONResponse


class ErrorDeLaApi(Exception):
    def __init__(self, codigo: int, mensaje: str, encabezados: dict[str, str] | None = None):
        super().__init__(mensaje)
        self.codigo = codigo
        self.mensaje = mensaje
        self.encabezados = encabezados


def responder_error(_peticion: Request, error: Exception) -> JSONResponse:
    assert isinstance(error, ErrorDeLaApi)
    return JSONResponse(
        status_code=error.codigo, content={"mensaje": error.mensaje}, headers=error.encabezados
    )
