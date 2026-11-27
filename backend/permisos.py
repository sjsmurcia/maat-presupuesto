"""Quién puede qué en cada empresa (D30, decisión 52): sin acceso 404, sin el permiso 403."""

import uuid
from collections.abc import Callable, Iterator

from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from backend.auth import SesionApi, UsuarioActual
from backend.db.modelos import Acceso, Permiso, RolPermiso
from backend.errores import ErrorDeLaApi


def requiere_permiso(codigo: str | None = None) -> Callable[..., Iterator[Session]]:
    """La transacción de la empresa de la ruta: revisa el acceso y, si se pide, el permiso,
    y le dice a la base la empresa para que la RLS filtre (D24).

    Sin acceso responde 404 y no 403, para no revelar que la empresa existe.
    """

    def sesion_de_la_empresa(
        empresa_id: uuid.UUID, usuario: UsuarioActual, sesion: SesionApi
    ) -> Iterator[Session]:
        with sesion.begin():
            if not tiene_permiso(sesion, usuario, empresa_id, None):
                raise ErrorDeLaApi(404, f"No existe la empresa {empresa_id}")
            if codigo is not None and not tiene_permiso(sesion, usuario, empresa_id, codigo):
                raise ErrorDeLaApi(403, f"Te falta el permiso {codigo} en esta empresa")
            sesion.execute(
                text("SELECT set_config('app.empresa_id', :e, true)"), {"e": str(empresa_id)}
            )
            yield sesion

    return sesion_de_la_empresa


def tiene_permiso(
    sesion: Session, usuario_id: uuid.UUID, empresa_id: uuid.UUID, codigo: str | None
) -> bool:
    """Un acceso activo a la empresa y, si hay código, que su rol tenga ese permiso."""
    consulta = select(func.count()).select_from(Acceso).where(
        Acceso.usuario_id == usuario_id, Acceso.empresa_id == empresa_id, Acceso.activo
    )
    if codigo is not None:
        consulta = (
            consulta.join(RolPermiso, RolPermiso.rol_id == Acceso.rol_id)
            .join(Permiso, Permiso.id == RolPermiso.permiso_id)
            .where(Permiso.codigo == codigo)
        )
    return bool(sesion.scalar(consulta))
