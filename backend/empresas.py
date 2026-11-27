"""Las empresas del usuario, con su rol, sus permisos y sus áreas (handoff, GET /empresas)."""

from typing import Any

from fastapi import APIRouter
from sqlalchemy import Row, select, text
from sqlalchemy.orm import Session

from backend.auth import SesionApi, UsuarioActual
from backend.db.modelos import Acceso, AccesoArea, Empresa, Permiso, Rol, RolPermiso

rutas_de_empresas = APIRouter()


@rutas_de_empresas.get("/empresas")
def listar_empresas(usuario: UsuarioActual, sesion: SesionApi) -> list[dict[str, Any]]:
    with sesion.begin():
        # La RLS deja ver solo las empresas de sus accesos activos (migración 0002).
        sesion.execute(text("SELECT set_config('app.usuario_id', :u, true)"), {"u": str(usuario)})
        filas = sesion.execute(
            select(
                Acceso.id.label("acceso_id"),
                Empresa.id,
                Empresa.nombre,
                Rol.id.label("rol_id"),
                Rol.codigo.label("rol_codigo"),
                Rol.nombre.label("rol_nombre"),
            )
            .join(Empresa, Empresa.id == Acceso.empresa_id)
            .join(Rol, Rol.id == Acceso.rol_id)
            .where(Acceso.usuario_id == usuario, Acceso.activo)
            .order_by(Empresa.nombre)
        ).all()
        return [_empresa_a_json(sesion, fila) for fila in filas]


def _empresa_a_json(sesion: Session, fila: Row[Any]) -> dict[str, Any]:
    permisos = sesion.scalars(
        select(Permiso.codigo)
        .join(RolPermiso, RolPermiso.permiso_id == Permiso.id)
        .where(RolPermiso.rol_id == fila.rol_id)
        .order_by(Permiso.codigo)
    )
    areas = sesion.scalars(
        select(AccesoArea.area_id).where(AccesoArea.acceso_id == fila.acceso_id)
    )
    return {
        "id": str(fila.id),
        "nombre": fila.nombre,
        "rol": {"codigo": fila.rol_codigo, "nombre": fila.rol_nombre},
        "permisos": list(permisos),
        "areas": sorted(str(area) for area in areas) or None,  # sin áreas: ve todas
        # Llegan con los ejercicios y el cierre; mientras no existan van vacíos.
        "ejercicio_actual": None,
        "mes_abierto": None,
        "estado_presupuesto": None,
    }
