"""La API de Maat Presupuesto: traduce HTTP; las reglas las decide el dominio."""

from fastapi import APIRouter, FastAPI

from backend.cuentas import rutas_de_cuentas

app = FastAPI(title="Maat Presupuesto")
api = APIRouter(prefix="/api")


@api.get("/salud")
def ver_salud() -> dict[str, str]:
    """No toca la base: el healthcheck responde aunque la base esté dormida."""
    return {"estado": "ok"}


api.include_router(rutas_de_cuentas)
app.include_router(api)
