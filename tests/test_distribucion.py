from decimal import Decimal

import pytest

from presupuesto.distribucion import (
    Asignacion,
    MontoFijo,
    Pedazo,
    Receptor,
    Regla,
    distribuir,
    validar_regla,
)

D = Decimal

CONTABILIDAD = "1-1-01"
VENTAS = "1-1-02"
BODEGA = "1-1-03"
ADMINISTRACION = "1-1-04"


def pedazo(porcentaje: str, *pares: tuple[str, str]) -> Pedazo:
    """Un pedazo que se reparte entre varios receptores según su base."""
    return Pedazo(D(porcentaje), tuple(Receptor(ceco, D(valor)) for ceco, valor in pares))


def entero(porcentaje: str, ceco: str) -> Pedazo:
    """Un pedazo que va entero a un solo centro."""
    return pedazo(porcentaje, (ceco, "1"))


def fijos(*pares: tuple[str, str]) -> tuple[MontoFijo, ...]:
    return tuple(MontoFijo(ceco, D(monto)) for ceco, monto in pares)


def asignaciones(*pares: tuple[str, str]) -> tuple[Asignacion, ...]:
    return tuple(Asignacion(ceco, D(monto)) for ceco, monto in pares)


# Reglas de ejemplo: las de siempre son un caso de pedazos
AWS_POR_COMPUTADORAS = Regla(
    (pedazo("100", (CONTABILIDAD, "20"), (VENTAS, "10"), (BODEGA, "10")),)
)
ALQUILER_POR_PORCENTAJE = Regla(
    (entero("50", CONTABILIDAD), entero("30", VENTAS), entero("20", BODEGA))
)
VIGILANCIA_FIJOS_Y_RESTO = Regla(
    (entero("100", BODEGA),),
    fijos((CONTABILIDAD, "200.00"), (VENTAS, "300.00")),
)
ENERGIA_EN_PEDAZOS = Regla(
    (entero("50", ADMINISTRACION), pedazo("50", (VENTAS, "30"), (BODEGA, "70"))),
)


# ---------- validar_regla ----------


@pytest.mark.parametrize(
    "regla",
    [
        AWS_POR_COMPUTADORAS,
        ALQUILER_POR_PORCENTAJE,
        VIGILANCIA_FIJOS_Y_RESTO,
        ENERGIA_EN_PEDAZOS,
        # el mismo CeCo en dos pedazos: entero en uno y por la base en el otro
        Regla((entero("50", ADMINISTRACION), pedazo("50", (ADMINISTRACION, "1"), (VENTAS, "1")))),
    ],
)
def test_validar_regla_con_regla_correcta_no_lanza(regla: Regla) -> None:
    validar_regla(regla)


@pytest.mark.parametrize(
    ("regla", "mensaje"),
    [
        (Regla(()), "al menos un pedazo"),
        (Regla((entero("50", CONTABILIDAD), entero("45", VENTAS))), "tienen que sumar 100"),
        (Regla((entero("50", CONTABILIDAD), entero("50.01", VENTAS))), "tienen que sumar 100"),
        (Regla((entero("110", CONTABILIDAD), entero("-10", VENTAS))), "porcentaje de un pedazo"),
        (Regla((entero("100", CONTABILIDAD), entero("0", VENTAS))), "porcentaje de un pedazo"),
        (Regla((pedazo("100"),)), "al menos un receptor"),
        (Regla((pedazo("100", (CONTABILIDAD, "0"), (VENTAS, "0")),)), "no pueden ser todos cero"),
        (Regla((pedazo("100", (CONTABILIDAD, "-1"), (VENTAS, "3")),)), "receptor puede ser negativo"),
        (Regla((pedazo("100", (CONTABILIDAD, "1"), (CONTABILIDAD, "2")),)), "(?i)repetido en un pedazo"),
        (Regla((entero("100", BODEGA),), fijos((VENTAS, "0.00"))), "monto fijo de .* mayor a cero"),
        (Regla((entero("100", BODEGA),), fijos((VENTAS, "-5.00"))), "monto fijo de .* mayor a cero"),
        (Regla((entero("100", BODEGA),), fijos((VENTAS, "1.001"))), "mas de 2 decimales"),
        (
            Regla((entero("100", BODEGA),), fijos((VENTAS, "10.00"), (VENTAS, "20.00"))),
            "(?i)repetido en los fijos",
        ),
    ],
)
def test_validar_regla_con_regla_invalida_lanza_value_error(regla: Regla, mensaje: str) -> None:
    with pytest.raises(ValueError, match=mensaje):
        validar_regla(regla)


# ---------- distribuir: las reglas de siempre ----------


def test_distribuir_un_pedazo_por_base_reparte_en_proporcion() -> None:
    # Arrange: AWS L 1,000.00 por computadoras 20 / 10 / 10
    # Act
    resultado = distribuir(D("1000.00"), AWS_POR_COMPUTADORAS)
    # Assert
    assert resultado == asignaciones((CONTABILIDAD, "500.00"), (VENTAS, "250.00"), (BODEGA, "250.00"))


def test_distribuir_pedazos_enteros_reparte_por_sus_porcentajes() -> None:
    # Arrange: alquiler L 1,000.00 al 50 / 30 / 20 %
    # Act
    resultado = distribuir(D("1000.00"), ALQUILER_POR_PORCENTAJE)
    # Assert
    assert resultado == asignaciones((CONTABILIDAD, "500.00"), (VENTAS, "300.00"), (BODEGA, "200.00"))


def test_distribuir_nota_de_credito_sin_fijos_reparte_en_negativo() -> None:
    # Arrange: nota de crédito de AWS por −L 100.00
    # Act
    resultado = distribuir(D("-100.00"), AWS_POR_COMPUTADORAS)
    # Assert
    assert resultado == asignaciones((CONTABILIDAD, "-50.00"), (VENTAS, "-25.00"), (BODEGA, "-25.00"))


def test_distribuir_receptor_con_valor_cero_aparece_con_cero() -> None:
    # Arrange: Bodega todavía no tiene computadoras
    regla = Regla((pedazo("100", (CONTABILIDAD, "1"), (BODEGA, "0"), (VENTAS, "1")),))
    # Act
    resultado = distribuir(D("100.00"), regla)
    # Assert
    assert resultado == asignaciones((CONTABILIDAD, "50.00"), (BODEGA, "0.00"), (VENTAS, "50.00"))


# ---------- distribuir: con fijos ----------


def test_distribuir_con_fijos_los_fijos_se_llevan_su_monto_y_el_resto_va_a_los_pedazos() -> None:
    # Arrange: Vigilancia L 1,000.00: Contabilidad 200 y Ventas 300 fijos, el resto a Bodega
    # Act
    resultado = distribuir(D("1000.00"), VIGILANCIA_FIJOS_Y_RESTO)
    # Assert
    assert resultado == asignaciones((CONTABILIDAD, "200.00"), (VENTAS, "300.00"), (BODEGA, "500.00"))


def test_distribuir_con_fijos_el_resto_se_reparte_por_base() -> None:
    # Arrange: L 1,000.00: Contabilidad 200 fijo; los 800 restantes por la base Ventas 1 y Bodega 3
    regla = Regla((pedazo("100", (VENTAS, "1"), (BODEGA, "3")),), fijos((CONTABILIDAD, "200.00")))
    # Act
    resultado = distribuir(D("1000.00"), regla)
    # Assert
    assert resultado == asignaciones((CONTABILIDAD, "200.00"), (VENTAS, "200.00"), (BODEGA, "600.00"))


def test_distribuir_ceco_en_fijo_y_en_un_pedazo_suma_sus_dos_partes() -> None:
    # Arrange: Contabilidad 100 fijo, y además 50 % de los 900 restantes
    regla = Regla((entero("50", CONTABILIDAD), entero("50", VENTAS)), fijos((CONTABILIDAD, "100.00")))
    # Act
    resultado = distribuir(D("1000.00"), regla)
    # Assert: una sola asignación por CeCo
    assert resultado == asignaciones((CONTABILIDAD, "550.00"), (VENTAS, "450.00"))


def test_distribuir_factura_igual_a_los_fijos_los_pedazos_aparecen_con_cero() -> None:
    # Act
    resultado = distribuir(D("500.00"), VIGILANCIA_FIJOS_Y_RESTO)
    # Assert
    assert resultado == asignaciones((CONTABILIDAD, "200.00"), (VENTAS, "300.00"), (BODEGA, "0.00"))


def test_distribuir_factura_menor_que_los_fijos_lanza_value_error() -> None:
    # Arrange: llega L 400.00 y los fijos suman L 500.00
    with pytest.raises(ValueError, match="no alcanza para los fijos"):
        distribuir(D("400.00"), VIGILANCIA_FIJOS_Y_RESTO)


def test_distribuir_nota_de_credito_con_fijos_lanza_value_error() -> None:
    with pytest.raises(ValueError, match="no alcanza para los fijos"):
        distribuir(D("-100.00"), VIGILANCIA_FIJOS_Y_RESTO)


# ---------- distribuir: en pedazos ----------


def test_distribuir_en_pedazos_uno_va_entero_y_otro_por_base() -> None:
    # Arrange: energía L 1,000.00: 50 % a Administración y 50 % por metros cuadrados 30 / 70
    # Act
    resultado = distribuir(D("1000.00"), ENERGIA_EN_PEDAZOS)
    # Assert
    assert resultado == asignaciones((ADMINISTRACION, "500.00"), (VENTAS, "150.00"), (BODEGA, "350.00"))


def test_distribuir_con_fijos_y_pedazos_los_pedazos_parten_lo_que_queda() -> None:
    # Arrange: L 10,000.00: Contabilidad 2,000 fijo; los 8,000 restantes en dos pedazos
    regla = Regla(
        (entero("50", ADMINISTRACION), pedazo("50", (VENTAS, "1"), (BODEGA, "3"))),
        fijos((CONTABILIDAD, "2000.00")),
    )
    # Act
    resultado = distribuir(D("10000.00"), regla)
    # Assert
    assert resultado == asignaciones(
        (CONTABILIDAD, "2000.00"), (ADMINISTRACION, "4000.00"), (VENTAS, "1000.00"), (BODEGA, "3000.00")
    )


def test_distribuir_en_pedazos_el_centavo_que_sobra_entre_pedazos_va_por_mayor_residuo() -> None:
    # Arrange: L 100.01 en dos pedazos de 50 %: 50.005 cada uno; el centavo va al primero
    regla = Regla((entero("50", ADMINISTRACION), pedazo("50", (VENTAS, "1"), (BODEGA, "1"))))
    # Act
    resultado = distribuir(D("100.01"), regla)
    # Assert: el segundo pedazo reparte sus 50.00, no 50.005
    assert resultado == asignaciones((ADMINISTRACION, "50.01"), (VENTAS, "25.00"), (BODEGA, "25.00"))


def test_distribuir_en_pedazos_el_centavo_que_sobra_dentro_de_un_pedazo_va_por_mayor_residuo() -> None:
    # Arrange: el segundo pedazo, de L 500.00, se reparte en tercios: 166.666...
    regla = Regla(
        (entero("50", ADMINISTRACION), pedazo("50", (VENTAS, "1"), (BODEGA, "1"), (CONTABILIDAD, "1")))
    )
    # Act
    resultado = distribuir(D("1000.00"), regla)
    # Assert
    assert resultado == asignaciones(
        (ADMINISTRACION, "500.00"), (VENTAS, "166.67"), (BODEGA, "166.67"), (CONTABILIDAD, "166.66")
    )


def test_distribuir_ceco_en_dos_pedazos_suma_sus_dos_partes() -> None:
    # Arrange: Administración se lleva su pedazo entero y además su parte del otro
    regla = Regla((entero("50", ADMINISTRACION), pedazo("50", (ADMINISTRACION, "1"), (VENTAS, "1"))))
    # Act
    resultado = distribuir(D("1000.00"), regla)
    # Assert: una sola asignación por CeCo
    assert resultado == asignaciones((ADMINISTRACION, "750.00"), (VENTAS, "250.00"))


def test_distribuir_nota_de_credito_en_pedazos_reparte_en_negativo() -> None:
    # Arrange: nota de crédito de energía por −L 100.00
    regla = Regla((entero("50", ADMINISTRACION), pedazo("50", (VENTAS, "1"), (BODEGA, "1"))))
    # Act
    resultado = distribuir(D("-100.00"), regla)
    # Assert
    assert resultado == asignaciones((ADMINISTRACION, "-50.00"), (VENTAS, "-25.00"), (BODEGA, "-25.00"))


# ---------- distribuir: garantías ----------


def test_distribuir_valida_la_regla_otra_vez() -> None:
    # Arrange: una regla que nunca pasó por el guardado (los pedazos suman 95)
    regla_vieja = Regla((entero("50", CONTABILIDAD), entero("45", VENTAS)))
    # Act / Assert
    with pytest.raises(ValueError, match="tienen que sumar 100"):
        distribuir(D("100.00"), regla_vieja)


@pytest.mark.parametrize(
    "monto",
    [D("500.00"), D("500.01"), D("777.77"), D("1000.00"), D("123456.78")],
)
def test_distribuir_con_cualquier_monto_la_suma_es_exacta(monto: Decimal) -> None:
    # Arrange: fijo de 200, y el resto en un pedazo entero y otro por la base 3 / 7 / 11
    regla = Regla(
        (entero("33.33", ADMINISTRACION), pedazo("66.67", (VENTAS, "3"), (BODEGA, "7"), (CONTABILIDAD, "11"))),
        fijos((CONTABILIDAD, "200.00")),
    )
    # Act
    resultado = distribuir(monto, regla)
    # Assert
    assert sum((a.monto for a in resultado), D("0.00")) == monto
    assert all(a.monto == a.monto.quantize(D("0.01")) for a in resultado)
    assert [a.ceco for a in resultado] == [CONTABILIDAD, ADMINISTRACION, VENTAS, BODEGA]
