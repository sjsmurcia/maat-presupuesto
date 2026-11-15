"""Reglas puras del presupuesto: reciben datos y devuelven datos.

Sin base, sin red, sin «hoy». El servicio lee, llama a estas funciones y
persiste. Dinero siempre en Decimal con 2 decimales; nunca float.
"""

import enum
from collections.abc import Sequence
from dataclasses import dataclass
from decimal import Decimal

MESES = 12
CENTAVO = Decimal("0.01")
PESOS_IGUALES: tuple[Decimal, ...] = (Decimal(1),) * MESES
UMBRAL_ALERTA = Decimal(90)


class EstadoPartida(enum.StrEnum):
    DENTRO = "DENTRO"
    ALERTA = "ALERTA"
    EXCEDIDO = "EXCEDIDO"


@dataclass(frozen=True)
class Ejecucion:
    presupuestado: Decimal
    real: Decimal
    variacion: Decimal
    porcentaje: Decimal | None  # None cuando no hay presupuesto: no se divide entre cero


def repartir_en_meses(
    total: Decimal, pesos: Sequence[Decimal] = PESOS_IGUALES
) -> tuple[Decimal, ...]:
    """Reparte el total anual en 12 meses en proporción a `pesos`.

    Reglas:
    - la suma de los 12 meses es EXACTAMENTE el total: no se pierde ni se
      inventa un centavo;
    - método del mayor residuo: cada mes recibe su parte truncada al centavo,
      y los centavos que sobran van, de a uno, a los meses con mayor residuo;
      si dos residuos empatan, gana el mes más temprano;
    - el total no puede ser negativo ni tener más de 2 decimales;
    - tienen que ser 12 pesos, ninguno negativo y no todos cero.
    Cualquier violación lanza ValueError.
    """
    raise NotImplementedError("jm: escribe esta función")


def calcular_ejecucion(presupuestado: Decimal, real: Decimal) -> Ejecucion:
    """Compara lo real contra lo presupuestado.

    - variacion = real - presupuestado (positiva: se gastó de más);
    - porcentaje = real / presupuestado × 100, redondeado a 2 decimales
      con ROUND_HALF_UP (el redondeo comercial; el de Python por defecto es
      el bancario, ROUND_HALF_EVEN, y da otro resultado en los medios exactos);
    - si presupuestado es cero, porcentaje es None.
    """
    raise NotImplementedError("jm: escribe esta función")


def clasificar(ejecucion: Ejecucion, umbral: Decimal = UMBRAL_ALERTA) -> EstadoPartida:
    """El semáforo de una partida de gasto.

    - EXCEDIDO si lo real supera lo presupuestado, aunque sea por un centavo.
      Se decide con los MONTOS, no con el porcentaje redondeado: 1000.01 sobre
      1000.00 se muestra 100.00 % y aun así está excedido;
    - ALERTA si el porcentaje mostrado llega al umbral (así el color coincide
      con el número que ve el contador);
    - DENTRO en cualquier otro caso. Sin presupuesto y sin gasto, DENTRO.
    - El umbral tiene que estar entre 0 (excluido) y 100 (incluido); si no,
      ValueError.
    """
    raise NotImplementedError("jm: escribe esta función")
