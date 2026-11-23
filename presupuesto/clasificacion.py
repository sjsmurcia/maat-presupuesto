"""Qué se hace con un gasto real según el CeCo donde se cargó.

Puro: recibe el tipo de CeCo y si tiene regla, y devuelve el destino. La
decisión vive en una tabla, no en un if que crece con cada caso.
"""

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
    """Decide el destino de un gasto real al cierre del mes.

    - ESPECIFICO sin regla: DIRECTO;
    - GENERICO con regla: DISTRIBUIDO;
    - GENERICO sin regla: CENTRALIZADO. El cierre no se traba por un CeCo
      nuevo; el tablero avisa que quedó dinero sin distribuir;
    - INSTITUCIONAL sin regla: CENTRALIZADO;
    - un ESPECIFICO o un INSTITUCIONAL CON regla es un error de catálogo:
      ValueError, porque esos CeCos no se reparten.
    """
    destino = _DESTINOS.get((tipo, tiene_regla))
    if destino is None:
        raise ValueError(f"Un CeCo {tipo} no puede tener regla de distribucion")
    return destino
