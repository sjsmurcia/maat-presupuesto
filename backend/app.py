"""La API de Maat Presupuesto: traduce HTTP; las reglas las decide el dominio."""

from fastapi import APIRouter, FastAPI

from backend.auth import rutas_de_auth
from backend.cuentas import rutas_de_cuentas
from backend.empresas import rutas_de_empresas
from backend.errores import ErrorDeLaApi, responder_error

app = FastAPI(title="Maat Presupuesto")
app.add_exception_handler(ErrorDeLaApi, responder_error)
api = APIRouter(prefix="/api")


@api.get("/salud")
def ver_salud() -> dict[str, str]:
    """No toca la base: el healthcheck responde aunque la base esté dormida."""
    return {"estado": "ok"}


api.include_router(rutas_de_auth)
api.include_router(rutas_de_empresas)
api.include_router(rutas_de_cuentas)
app.include_router(api)
