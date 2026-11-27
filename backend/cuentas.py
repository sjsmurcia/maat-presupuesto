"""Las rutas del catálogo de cuentas: leen la base y el dominio dice qué recibe presupuesto."""

import uuid
from typing import Annotated, Any

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.db.modelos import Cuenta
from backend.permisos import requiere_permiso
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


@rutas_de_cuentas.get("/empresas/{empresa_id}/cuentas")
def listar_cuentas(
    empresa_id: uuid.UUID, sesion: Annotated[Session, Depends(requiere_permiso())]
) -> list[dict[str, Any]]:
    """Leer el catálogo solo pide acceso a la empresa (decisión 52).

    Se traducen dentro de la transacción: al cerrarla, la RLS ya no deja releer las filas.
    """
    consulta = select(Cuenta).where(Cuenta.empresa_id == empresa_id).order_by(Cuenta.codigo)
    return [cuenta_a_json(cuenta) for cuenta in sesion.scalars(consulta)]
