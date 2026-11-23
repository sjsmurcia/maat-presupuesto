"""Qué se hace con un gasto real según el tipo de CeCo donde se cargó."""

import enum


class TipoCeco(enum.StrEnum):
    ESPECIFICO = "ESPECIFICO"  # un área concreta: Ventas, Bodega
    GENERICO = "GENERICO"  # gasto compartido que se reparte con una regla
    INSTITUCIONAL = "INSTITUCIONAL"  # por política no se distribuye


class Destino(enum.StrEnum):
    DIRECTO = "DIRECTO"  # se queda en el CeCo donde se cargó
    DISTRIBUIDO = "DISTRIBUIDO"  # se reparte con `distribuir`
    CENTRALIZADO = "CENTRALIZADO"  # queda en el CeCo, sin repartir


_DESTINOS: dict[tuple[TipoCeco, bool], Destino] = {
    (TipoCeco.ESPECIFICO, False): Destino.DIRECTO,
    (TipoCeco.GENERICO, True): Destino.DISTRIBUIDO,
    (TipoCeco.GENERICO, False): Destino.CENTRALIZADO,
    (TipoCeco.INSTITUCIONAL, False): Destino.CENTRALIZADO,
}


def clasificar_movimiento(tipo: TipoCeco, tiene_regla: bool) -> Destino:
    """Decide si el gasto va directo, se distribuye o queda centralizado.

    Un genérico sin regla queda centralizado para que un CeCo nuevo no trabe
    el cierre; el tablero avisa que quedó dinero sin distribuir.
    """
    destino = _DESTINOS.get((tipo, tiene_regla))
    if destino is None:
        raise ValueError(f"Un CeCo {tipo} no puede tener regla de distribucion")
    return destino
