"""Matemática del reparto: funciones puras, con el dinero en Decimal de 2 decimales."""

from collections.abc import Sequence
from decimal import ROUND_DOWN, Decimal

CENTAVO = Decimal("0.01")


def repartir_por_pesos(monto: Decimal, pesos: Sequence[Decimal]) -> tuple[Decimal, ...]:
    """Reparte `monto` en proporción a `pesos` sin perder ni inventar un centavo.

    Trunca cada parte y da los centavos sobrantes por mayor residuo: redondear
    cada parte puede descuadrar la suma (2.00 / 3 → 0.67 × 3 = 2.01).
    """
    _validar_datos_del_reparto(monto, pesos)
    # se reparte el valor absoluto para que truncar y el mayor residuo
    # funcionen igual con una nota de crédito
    absoluto = abs(monto)
    total_pesos = sum(pesos, Decimal(0))
    exactas = [absoluto * peso / total_pesos for peso in pesos]
    partes = [exacta.quantize(CENTAVO, ROUND_DOWN) for exacta in exactas]

    # truncar nunca inventa centavos: los que faltan se reparten de a uno
    centavos_sobrantes = int((absoluto - sum(partes, Decimal(0))) / CENTAVO)
    por_mayor_residuo = sorted(
        range(len(pesos)),
        key=lambda i: exactas[i] - partes[i],
        reverse=True,
    )
    for i in por_mayor_residuo[:centavos_sobrantes]:
        partes[i] += CENTAVO
    if monto < 0:
        return tuple(-parte for parte in partes)
    return tuple(partes)


def _validar_datos_del_reparto(monto: Decimal, pesos: Sequence[Decimal]) -> None:
    if monto != monto.quantize(CENTAVO):
        raise ValueError("El monto no puede tener mas de 2 decimales")
    if not pesos:
        raise ValueError("Tiene que haber al menos un receptor")
    if any(peso < 0 for peso in pesos):
        raise ValueError("Ningun peso puede ser negativo")
    if sum(pesos, Decimal(0)) == 0:
        raise ValueError("Los pesos no pueden ser todos cero")
