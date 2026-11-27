"""Qué cuentas del catálogo reciben presupuesto."""

import enum


class Naturaleza(enum.StrEnum):
    ACTIVO = "ACTIVO"
    PASIVO = "PASIVO"
    PATRIMONIO = "PATRIMONIO"
    INGRESO = "INGRESO"
    COSTO = "COSTO"
    GASTO = "GASTO"


_SE_PRESUPUESTAN = frozenset({Naturaleza.INGRESO, Naturaleza.COSTO, Naturaleza.GASTO})


def recibe_presupuesto(
    naturaleza: Naturaleza, es_detalle: bool, esta_activa: bool
) -> bool:
    """Dice si una cuenta puede llevar líneas de detalle del presupuesto.

    Una cuenta de grupo solo suma a sus hijas, y una inactiva ya no recibe nada nuevo.
    """
    return es_detalle and esta_activa and naturaleza in _SE_PRESUPUESTAN
