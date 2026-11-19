from decimal import Decimal

import pytest

from presupuesto.distribucion import (
    Asignacion,
    BaseDelResto,
    MontoFijo,
    PesoDelResto,
    Regla,
    distribuir,
    validar_regla,
)

D = Decimal
PORCENTAJE = BaseDelResto.PORCENTAJE
INDUCTOR = BaseDelResto.INDUCTOR

CONTABILIDAD = "1-1-01"
VENTAS = "1-1-02"
BODEGA = "1-1-03"


def resto(*pares: tuple[str, str]) -> tuple[PesoDelResto, ...]:
    return tuple(PesoDelResto(ceco, D(valor)) for ceco, valor in pares)


def fijos(*pares: tuple[str, str]) -> tuple[MontoFijo, ...]:
    return tuple(MontoFijo(ceco, D(monto)) for ceco, monto in pares)


def asignaciones(*pares: tuple[str, str]) -> tuple[Asignacion, ...]:
    return tuple(Asignacion(ceco, D(monto)) for ceco, monto in pares)


# Reglas de ejemplo
AWS_POR_COMPUTADORAS = Regla(INDUCTOR, resto((CONTABILIDAD, "20"), (VENTAS, "10"), (BODEGA, "10")))
ALQUILER_POR_PORCENTAJE = Regla(
    PORCENTAJE, resto((CONTABILIDAD, "50"), (VENTAS, "30"), (BODEGA, "20"))
)
VIGILANCIA_FIJOS_Y_RESTO = Regla(
    PORCENTAJE,
    resto((BODEGA, "100")),
    fijos((CONTABILIDAD, "200.00"), (VENTAS, "300.00")),
)


# ---------- validar_regla ----------


@pytest.mark.parametrize(
    "regla",
    [AWS_POR_COMPUTADORAS, ALQUILER_POR_PORCENTAJE, VIGILANCIA_FIJOS_Y_RESTO],
)
def test_validar_regla_con_regla_correcta_no_lanza(regla: Regla) -> None:
    validar_regla(regla)


@pytest.mark.parametrize(
    ("regla", "motivo"),
    [
        (Regla(PORCENTAJE, resto((CONTABILIDAD, "50"), (VENTAS, "45"))), "porcentajes suman 95"),
        (Regla(PORCENTAJE, resto((CONTABILIDAD, "50"), (VENTAS, "50.01"))), "suman 100.01"),
        (Regla(PORCENTAJE, resto((CONTABILIDAD, "110"), (VENTAS, "-10"))), "porcentaje negativo"),
        (Regla(INDUCTOR, ()), "resto sin receptores"),
        (Regla(INDUCTOR, resto((CONTABILIDAD, "0"), (VENTAS, "0"))), "inductor todo en cero"),
        (Regla(INDUCTOR, resto((CONTABILIDAD, "-1"), (VENTAS, "3"))), "inductor negativo"),
        (Regla(INDUCTOR, resto((CONTABILIDAD, "1"), (CONTABILIDAD, "2"))), "CeCo repetido en el resto"),
        (Regla(PORCENTAJE, resto((BODEGA, "100")), fijos((VENTAS, "0.00"))), "fijo en cero"),
        (Regla(PORCENTAJE, resto((BODEGA, "100")), fijos((VENTAS, "-5.00"))), "fijo negativo"),
        (Regla(PORCENTAJE, resto((BODEGA, "100")), fijos((VENTAS, "1.001"))), "fijo con 3 decimales"),
        (
            Regla(PORCENTAJE, resto((BODEGA, "100")), fijos((VENTAS, "10.00"), (VENTAS, "20.00"))),
            "CeCo repetido en los fijos",
        ),
    ],
)
def test_validar_regla_con_regla_invalida_lanza_value_error(regla: Regla, motivo: str) -> None:
    with pytest.raises(ValueError):
        validar_regla(regla)


# ---------- distribuir: sin fijos ----------


def test_distribuir_por_inductor_reparte_en_proporcion() -> None:
    # Arrange: AWS L 1,000.00 por computadoras 20 / 10 / 10
    # Act
    resultado = distribuir(D("1000.00"), AWS_POR_COMPUTADORAS)
    # Assert
    assert resultado == asignaciones((CONTABILIDAD, "500.00"), (VENTAS, "250.00"), (BODEGA, "250.00"))


def test_distribuir_por_porcentaje_reparte_en_proporcion() -> None:
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


def test_distribuir_receptor_con_peso_cero_aparece_con_cero() -> None:
    # Arrange: Bodega todavía no tiene computadoras
    regla = Regla(INDUCTOR, resto((CONTABILIDAD, "1"), (BODEGA, "0"), (VENTAS, "1")))
    # Act
    resultado = distribuir(D("100.00"), regla)
    # Assert
    assert resultado == asignaciones((CONTABILIDAD, "50.00"), (BODEGA, "0.00"), (VENTAS, "50.00"))


# ---------- distribuir: con fijos ----------


def test_distribuir_con_fijos_los_fijos_se_llevan_su_monto_y_el_resto_va_al_resto() -> None:
    # Arrange: Vigilancia L 1,000.00: Contabilidad 200 y Ventas 300 fijos, el resto a Bodega
    # Act
    resultado = distribuir(D("1000.00"), VIGILANCIA_FIJOS_Y_RESTO)
    # Assert
    assert resultado == asignaciones((CONTABILIDAD, "200.00"), (VENTAS, "300.00"), (BODEGA, "500.00"))


def test_distribuir_con_fijos_el_resto_se_reparte_por_inductor() -> None:
    # Arrange: L 1,000.00: Contabilidad 200 fijo; los 800 restantes por inductor Ventas 1 y Bodega 3
    regla = Regla(INDUCTOR, resto((VENTAS, "1"), (BODEGA, "3")), fijos((CONTABILIDAD, "200.00")))
    # Act
    resultado = distribuir(D("1000.00"), regla)
    # Assert
    assert resultado == asignaciones((CONTABILIDAD, "200.00"), (VENTAS, "200.00"), (BODEGA, "600.00"))


def test_distribuir_ceco_en_fijo_y_en_resto_suma_sus_dos_partes() -> None:
    # Arrange: Contabilidad 100 fijo, y además 50 % de los 900 restantes
    regla = Regla(PORCENTAJE, resto((CONTABILIDAD, "50"), (VENTAS, "50")), fijos((CONTABILIDAD, "100.00")))
    # Act
    resultado = distribuir(D("1000.00"), regla)
    # Assert: una sola asignación por CeCo
    assert resultado == asignaciones((CONTABILIDAD, "550.00"), (VENTAS, "450.00"))


def test_distribuir_factura_igual_a_los_fijos_el_resto_aparece_con_cero() -> None:
    # Act
    resultado = distribuir(D("500.00"), VIGILANCIA_FIJOS_Y_RESTO)
    # Assert
    assert resultado == asignaciones((CONTABILIDAD, "200.00"), (VENTAS, "300.00"), (BODEGA, "0.00"))


def test_distribuir_factura_menor_que_los_fijos_lanza_value_error() -> None:
    # Arrange: llega L 400.00 y los fijos suman L 500.00
    with pytest.raises(ValueError):
        distribuir(D("400.00"), VIGILANCIA_FIJOS_Y_RESTO)


def test_distribuir_nota_de_credito_con_fijos_lanza_value_error() -> None:
    with pytest.raises(ValueError):
        distribuir(D("-100.00"), VIGILANCIA_FIJOS_Y_RESTO)


# ---------- distribuir: garantías ----------


def test_distribuir_valida_la_regla_otra_vez() -> None:
    # Arrange: una regla que nunca pasó por el guardado (porcentajes suman 95)
    regla_vieja = Regla(PORCENTAJE, resto((CONTABILIDAD, "50"), (VENTAS, "45")))
    # Act / Assert
    with pytest.raises(ValueError):
        distribuir(D("100.00"), regla_vieja)


@pytest.mark.parametrize(
    "monto",
    [D("500.00"), D("500.01"), D("777.77"), D("1000.00"), D("123456.78")],
)
def test_distribuir_con_cualquier_monto_la_suma_es_exacta(monto: Decimal) -> None:
    # Arrange: fijo de 200 y el resto por inductor 3 / 7 / 11
    regla = Regla(
        INDUCTOR,
        resto((VENTAS, "3"), (BODEGA, "7"), (CONTABILIDAD, "11")),
        fijos((CONTABILIDAD, "200.00")),
    )
    # Act
    resultado = distribuir(monto, regla)
    # Assert
    assert sum((a.monto for a in resultado), D("0.00")) == monto
    assert [a.ceco for a in resultado] == [CONTABILIDAD, VENTAS, BODEGA]
