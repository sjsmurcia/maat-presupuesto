"""Reglas puras del presupuesto: reciben datos y devuelven datos.

Sin base, sin red, sin «hoy». El servicio lee, llama a estas funciones y
persiste. Dinero siempre en Decimal con 2 decimales; nunca float.
"""

from collections.abc import Sequence
from decimal import Decimal

CENTAVO = Decimal("0.01")


def repartir_por_pesos(monto: Decimal, pesos: Sequence[Decimal]) -> tuple[Decimal, ...]:
    """Reparte `monto` entre los receptores en proporción a sus `pesos`.

    Es la matemática de la regla de distribución: el gasto de un CeCo
    genérico se reparte entre las áreas según un inductor (computadoras,
    salarios, horas) o un porcentaje.

    Reglas:
    - la suma de las partes es EXACTAMENTE el monto: no se pierde ni se
      inventa un centavo;
    - mayor residuo: cada receptor recibe su parte truncada al centavo, y
      los centavos que sobran van, de a uno, a los de mayor residuo; si dos
      residuos empatan, gana el que va primero;
    - un monto negativo (nota de crédito, reclasificación) se reparte igual,
      con todas las partes en negativo: se reparte el valor absoluto y se le
      devuelve el signo;
    - un receptor con peso cero recibe cero;
    - el monto no puede tener más de 2 decimales; tiene que haber al menos
      un receptor, ningún peso negativo y no todos cero.
    Cualquier violación lanza ValueError.
    """
    raise NotImplementedError("jm: escribe esta función")
