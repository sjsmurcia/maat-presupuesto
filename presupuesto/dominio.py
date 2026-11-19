"""Reglas puras del presupuesto: reciben datos y devuelven datos.

Sin base, sin red, sin «hoy». El servicio lee, llama a estas funciones y
persiste. Dinero siempre en Decimal con 2 decimales; nunca float.
"""

from collections.abc import Sequence
from decimal import ROUND_DOWN, Decimal

CENTAVO = Decimal("0.01")


def repartir_por_pesos(monto: Decimal, pesos: Sequence[Decimal]) -> tuple[Decimal, ...]:
    _validar_datos_del_reparto(monto,pesos)
    #reparte el valor absoluto para que truncar y el mayor resuido

    absoluto = abs(monto)
    total_pesos=sum(pesos,Decimal(0))
    exactas= [absoluto * peso /total_pesos for peso in pesos]
    partes =[exacta.quantize(CENTAVO, ROUND_DOWN) for exacta in exactas]

    #truncar para no inventar centavos 
    centavos_sobrantes = int((absoluto-sum(partes,Decimal(0)))/CENTAVO) 
    por_mayor_residuo = sorted(
            range(len(pesos)),
            key=lambda i:exactas[i] -partes[i],
            reverse=True,
    )
    for i in por_mayor_residuo[:centavos_sobrantes]:
            partes[i] +=CENTAVO
    if monto<0:
        return tuple(-parte for parte in partes)
    return tuple(partes)
def _validar_datos_del_reparto(monto:Decimal, pesos: Sequence[Decimal])->None:
     if monto != monto.quantize(CENTAVO):
          raise ValueError("El monto no puede tener mas de 2 decimales")
     if not pesos:
          raise ValueError("Tiene que haber al menos un receptor")
     if any(peso<0 for peso in pesos):
          raise ValueError("Ningun peso puede ser negativo")
     if sum(pesos, Decimal(0))==0:
          raise ValueError("Los pesos no pueden ser todos cero")
     
