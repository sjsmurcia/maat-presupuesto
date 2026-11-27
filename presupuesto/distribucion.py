"""Regla de distribución de un CeCo genérico: a quién le toca cuánto.

Primero los montos fijos; el resto se parte en pedazos por porcentaje, y cada
pedazo va entero a un centro o se reparte entre varios según una base.
"""

from collections.abc import Sequence
from dataclasses import dataclass
from decimal import Decimal

from presupuesto.dominio import CENTAVO

CIEN = Decimal(100)


@dataclass(frozen=True)
class MontoFijo:
    ceco: str  # código del CeCo receptor
    monto: Decimal


@dataclass(frozen=True)
class Receptor:
    ceco: str  # código del CeCo receptor
    valor: Decimal  # su número en la base: empleados, metros cuadrados, horas…


@dataclass(frozen=True)
class Pedazo:
    porcentaje: Decimal  # su parte del resto; los pedazos de una regla suman 100
    # con un solo receptor el pedazo va entero; con varios, por sus valores
    receptores: tuple[Receptor, ...]


@dataclass(frozen=True)
class Regla:
    pedazos: tuple[Pedazo, ...]
    fijos: tuple[MontoFijo, ...] = ()


@dataclass(frozen=True)
class Asignacion:
    ceco: str
    monto: Decimal


def validar_regla(regla: Regla) -> None:
    """Lanza ValueError si la regla no se puede guardar ni aplicar.

    Es la misma validación al guardar y al distribuir: la regla vive en un solo lugar.
    """
    _validar_cecos_sin_repetir(regla.fijos, "los fijos")
    _validar_montos_fijos(regla.fijos)
    _validar_pedazos(regla.pedazos)
    for pedazo in regla.pedazos:
        _validar_receptores(pedazo.receptores)


def _validar_pedazos(pedazos: tuple[Pedazo, ...]) -> None:
    # 1. sin pedazos
    if not pedazos:
        raise ValueError("La regla necesita al menos un pedazo")
    # 2. algún porcentaje <= 0
    if any(pedazo.porcentaje <= 0 for pedazo in pedazos):
        raise ValueError("El porcentaje de un pedazo tiene que ser mayor a cero")
    total = sum((pedazo.porcentaje for pedazo in pedazos), Decimal(0))
    if total != CIEN:
        raise ValueError(f"Los porcentajes tienen que sumar 100 y suman {total}")


def _validar_receptores(receptores: tuple[Receptor, ...]) -> None:
    if not receptores:
        raise ValueError("Un pedazo necesita al menos un receptor")
    _validar_cecos_sin_repetir(receptores, "un pedazo")
    if any(receptor.valor < 0 for receptor in receptores):
        raise ValueError("Ningun valor de un receptor puede ser negativo")
    total = sum((receptor.valor for receptor in receptores), Decimal(0))
    if total == 0:
        raise ValueError("Los valores de un pedazo no pueden ser todos cero")


def _validar_cecos_sin_repetir(
    tramo: Sequence[MontoFijo | Receptor], nombre: str
) -> None:
    cecos = [elemento.ceco for elemento in tramo]
    if len(cecos) != len(set(cecos)):
        raise ValueError(f"Un Centro de Costo Repetido en {nombre}")


def _validar_montos_fijos(fijos: tuple[MontoFijo, ...]) -> None:
    for fijo in fijos:
        if fijo.monto <= 0:
            raise ValueError(f"El monto fijo de {fijo.ceco} tiene que ser mayor a cero")
        if fijo.monto != fijo.monto.quantize(CENTAVO):
            raise ValueError(
                f"El monto fijo de {fijo.ceco} no puede tener mas de 2 decimales"
            )


def distribuir(monto: Decimal, regla: Regla) -> tuple[Asignacion, ...]:
    """Reparte `monto` según `regla`: los fijos tal cual y el resto por pedazos.

    El resto se reparte dos veces, sin perder un centavo: entre los pedazos, y
    después cada pedazo entre sus receptores.
    """
    validar_regla(regla)
    _validar_monto_contra_fijos(monto, regla.fijos)

    raise NotImplementedError("jm: reparte los fijos y después cada pedazo")


def _sumar_fijos(fijos: tuple[MontoFijo, ...]) -> Decimal:
    return sum((fijo.monto for fijo in fijos), Decimal("0.00"))


def _validar_monto_contra_fijos(monto: Decimal, fijos: tuple[MontoFijo, ...]) -> None:
    suma_fijos = _sumar_fijos(fijos)
    if fijos and monto < suma_fijos:
        raise ValueError(
            f"El monto {monto} no alcanza para los fijos, que suman {suma_fijos}"
        )
