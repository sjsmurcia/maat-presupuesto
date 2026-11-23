"""Regla de distribución de un CeCo genérico: a quién le toca cuánto.

Primero los montos fijos; el resto se reparte por porcentaje o por inductor.
"""

import enum
from collections.abc import Sequence
from dataclasses import dataclass
from decimal import Decimal

from presupuesto.dominio import CENTAVO, repartir_por_pesos

CIEN = Decimal(100)


class BaseDelResto(enum.StrEnum):
    PORCENTAJE = "PORCENTAJE"  # los valores suman exactamente 100
    INDUCTOR = "INDUCTOR"  # computadoras, salarios, horas: cualquier cantidad


@dataclass(frozen=True)
class MontoFijo:
    ceco: str  # código del CeCo receptor
    monto: Decimal


@dataclass(frozen=True)
class PesoDelResto:
    ceco: str  # código del CeCo receptor
    valor: Decimal  # el porcentaje, o la cantidad del inductor


@dataclass(frozen=True)
class Regla:
    base_del_resto: BaseDelResto
    resto: tuple[PesoDelResto, ...]
    fijos: tuple[MontoFijo, ...] = ()


@dataclass(frozen=True)
class Asignacion:
    ceco: str
    monto: Decimal


def validar_regla(regla: Regla) -> None:
    """Lanza ValueError si la regla no se puede guardar ni aplicar.

    Es la misma validación al guardar y al distribuir: la regla vive en un solo lugar.
    """
    _validar_resto_con_receptores(regla.resto)
    _validar_cecos_sin_repetir(regla.fijos, "los fijos")
    _validar_cecos_sin_repetir(regla.resto, "el resto")
    _validar_montos_fijos(regla.fijos)
    _validar_valores_sin_negativos(regla.resto)
    _validar_total_del_resto(regla.base_del_resto, regla.resto)


def _validar_resto_con_receptores(resto: tuple[PesoDelResto, ...]) -> None:
    if not resto:
        raise ValueError("La regla necesita al menos un receptor para el resto")


def _validar_cecos_sin_repetir(
    tramo: Sequence[MontoFijo | PesoDelResto], nombre: str
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


def _validar_valores_sin_negativos(resto: tuple[PesoDelResto, ...]) -> None:
    if any(peso.valor < 0 for peso in resto):
        raise ValueError("Ningun valor del resto puede ser negativo")


def _validar_total_del_resto(
    base: BaseDelResto, resto: tuple[PesoDelResto, ...]
) -> None:
    total = sum((peso.valor for peso in resto), Decimal(0))
    if base is BaseDelResto.PORCENTAJE and total != CIEN:
        raise ValueError(f"Los porcentajes tienen que sumar 100 y suma {total}")
    if total == 0:
        raise ValueError("Los Valores del resto no pueden ser todos cero")


def distribuir(monto: Decimal, regla: Regla) -> tuple[Asignacion, ...]:
    """Reparte `monto` según `regla`: los fijos tal cual y el resto por sus pesos.

    Con fijos, un monto que no alcanza para cubrirlos (una nota de crédito, por
    ejemplo) se rechaza: en la v1 ese caso se reparte a mano.
    """
    validar_regla(regla)
    _validar_monto_contra_fijos(monto, regla.fijos)
    resto_a_repartir = monto - _sumar_fijos(regla.fijos)
    pesos = [peso.valor for peso in regla.resto]
    partes_del_resto = repartir_por_pesos(resto_a_repartir, pesos)
    return _juntar_por_ceco(regla.fijos, regla.resto, partes_del_resto)


def _sumar_fijos(fijos: tuple[MontoFijo, ...]) -> Decimal:
    return sum((fijo.monto for fijo in fijos), Decimal("0.00"))


def _validar_monto_contra_fijos(monto: Decimal, fijos: tuple[MontoFijo, ...]) -> None:
    suma_fijos = _sumar_fijos(fijos)
    if fijos and monto < suma_fijos:
        raise ValueError(
            f"El monto {monto} no alcanza para los fijos, que suman {suma_fijos}"
        )


def _juntar_por_ceco(
    fijos: tuple[MontoFijo, ...],
    resto: tuple[PesoDelResto, ...],
    partes_del_resto: tuple[Decimal, ...],
) -> tuple[Asignacion, ...]:
    por_ceco: dict[str, Decimal] = {}
    for fijo in fijos:
        por_ceco[fijo.ceco] = fijo.monto
    for peso, parte in zip(resto, partes_del_resto, strict=True):
        por_ceco[peso.ceco] = por_ceco.get(peso.ceco, Decimal("0.00")) + parte
    return tuple(Asignacion(ceco, monto) for ceco, monto in por_ceco.items())
