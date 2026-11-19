"""Regla de distribución de un CeCo genérico: a quién le toca cuánto.

Una regla se arma en dos tramos: primero los montos fijos y después el
resto, que se reparte por porcentaje o por inductor. Nunca queda dinero sin
distribuir: lo que no se lleva un fijo va al resto.

Puro: recibe la regla y el monto y devuelve las asignaciones. La matemática
del reparto vive en `dominio.repartir_por_pesos`, en un solo lugar.
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

    Es la MISMA validación al guardar la regla y al distribuir: la regla de
    negocio vive en un solo lugar.

    - el resto tiene al menos un receptor: la regla siempre dice a dónde va
      lo que no se llevan los fijos;
    - un CeCo no se repite dentro del mismo tramo;
    - cada monto fijo es mayor que cero y tiene como máximo 2 decimales;
    - por PORCENTAJE: ningún valor negativo, y suman exactamente 100;
    - por INDUCTOR: ningún valor negativo, y no todos en cero.
    """
    _validar_resto_con_receptores(regla.resto)
    _validar_cecos_sin_repetir(regla.fijos, "los fijos")
    _validar_cecos_sin_repetir(regla.resto, "el resto")
    _validar_montos_fijos(regla.fijos)
    _validar_valores_sin_negativos(regla.resto)
    _validar_total_del_resto(regla.base_del_resto, regla.resto)


def _validar_resto_con_receptores(resto: tuple[PesoDelResto, ...]) -> None:
    """la regla simpre dice donde va lo que no se llevan los montos fijos"""
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
    """Reparte `monto` según `regla`.

    - valida la regla con `validar_regla`;
    - los fijos se llevan su monto tal cual; el resto (monto menos la suma
      de los fijos) se reparte con `repartir_por_pesos` según los valores
      del resto;
    - CON fijos: si el monto es menor que la suma de los fijos, ValueError.
      Eso incluye cualquier nota de crédito (monto negativo), que en la v1
      se reparte a mano;
    - SIN fijos: un monto negativo (nota de crédito) se reparte igual, en
      negativo;
    - el resultado trae una asignación por CeCo, en el orden en que aparece
      por primera vez (fijos primero, después el resto). Si un CeCo está en
      los fijos Y en el resto, sus dos partes se suman en una sola
      asignación. Un CeCo al que le toca cero aparece igual, con 0.00;
    - la suma de las asignaciones es EXACTAMENTE el monto.
    """
    raise NotImplementedError("jm: escribe esta función")
