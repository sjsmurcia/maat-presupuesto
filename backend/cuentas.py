"""Las rutas del catálogo de cuentas: leen la base y el dominio dice qué recibe presupuesto."""

import uuid
from typing import Annotated, Any

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from backend.db.modelos import Cuenta, Empresa
from backend.db.sesion import sesion_de_la_api
from presupuesto.cuentas import Naturaleza, recibe_presupuesto

rutas_de_cuentas = APIRouter()


def cuenta_a_json(cuenta: Cuenta) -> dict[str, Any]:
    return {
        "codigo": cuenta.codigo,
        "nombre": cuenta.nombre,
        "codigo_superior": cuenta.codigo_superior,
        "naturaleza": cuenta.naturaleza,
        "es_detalle": cuenta.es_detalle,
        "activa": cuenta.activa,
        "recibe_presupuesto": recibe_presupuesto(
            Naturaleza(cuenta.naturaleza), cuenta.es_detalle, cuenta.activa
        ),
    }


def leer_cuentas(sesion: Session, empresa_id: uuid.UUID) -> list[dict[str, Any]] | None:
    """Las cuentas de la empresa en JSON, o None si la empresa no existe o no se ve.

    Se traducen dentro de la transacción: al cerrarla, la RLS ya no deja releer las filas.
    """
    with sesion.begin():
        sesion.execute(
            text("SELECT set_config('app.empresa_id', :id, true)"), {"id": str(empresa_id)}
        )
        if sesion.get(Empresa, empresa_id) is None:
            return None
        consulta = (
            select(Cuenta).where(Cuenta.empresa_id == empresa_id).order_by(Cuenta.codigo)
        )
        return [cuenta_a_json(cuenta) for cuenta in sesion.scalars(consulta)]


@rutas_de_cuentas.get("/empresas/{empresa_id}/cuentas")
def listar_cuentas(
    empresa_id: uuid.UUID, sesion: Annotated[Session, Depends(sesion_de_la_api)]
) -> Any:
    cuentas = leer_cuentas(sesion, empresa_id)
    if cuentas is None:
        mensaje = f"No existe la empresa {empresa_id}"
        return JSONResponse(status_code=404, content={"mensaje": mensaje})
    return cuentas
