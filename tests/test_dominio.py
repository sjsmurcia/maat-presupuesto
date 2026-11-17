from decimal import Decimal

import pytest

from presupuesto.dominio import repartir_por_pesos

D = Decimal


def pesos(*valores: int) -> tuple[Decimal, ...]:
    return tuple(D(v) for v in valores)


def montos(*valores: str) -> tuple[Decimal, ...]:
    return tuple(D(v) for v in valores)


def test_repartir_por_pesos_cuando_divide_exacto_reparte_en_proporcion() -> None:
    # Arrange: AWS L 1,000.00 por computadoras: Contabilidad 20, Ventas 10, Bodega 10
    monto = D("1000.00")
    computadoras = pesos(20, 10, 10)
    # Act
    partes = repartir_por_pesos(monto, computadoras)
    # Assert
    assert partes == montos("500.00", "250.00", "250.00")


def test_repartir_por_pesos_cuando_sobra_un_centavo_va_al_primero_si_empatan() -> None:
    # Arrange: 1000 / 3 = 333.333...; truncado suma 999.99 y sobra 1 centavo
    monto = D("1000.00")
    # Act
    partes = repartir_por_pesos(monto, pesos(1, 1, 1))
    # Assert
    assert partes == montos("333.34", "333.33", "333.33")


def test_repartir_por_pesos_cuando_sobran_dos_centavos_van_a_los_dos_primeros() -> None:
    # Arrange: 2.00 / 3 = 0.666...; truncado suma 1.98 y sobran 2 centavos.
    # Redondear en vez de truncar daría 0.67 × 3 = 2.01: un centavo inventado.
    monto = D("2.00")
    # Act
    partes = repartir_por_pesos(monto, pesos(1, 1, 1))
    # Assert
    assert partes == montos("0.67", "0.67", "0.66")


def test_repartir_por_pesos_cuando_un_residuo_es_mayor_gana_aunque_vaya_despues() -> None:
    # Arrange: 1.00 en proporción 1:2 → 0.333 (residuo 0.0033) y 0.666 (residuo 0.0067)
    monto = D("1.00")
    # Act
    partes = repartir_por_pesos(monto, pesos(1, 2))
    # Assert: el centavo que sobra va al segundo, no al primero
    assert partes == montos("0.33", "0.67")


def test_repartir_por_pesos_con_nota_de_credito_reparte_en_negativo() -> None:
    # Arrange: nota de crédito de AWS por −L 100.00, misma regla por computadoras
    monto = D("-100.00")
    # Act
    partes = repartir_por_pesos(monto, pesos(20, 10, 10))
    # Assert
    assert partes == montos("-50.00", "-25.00", "-25.00")


def test_repartir_por_pesos_con_negativo_que_no_divide_exacto_es_simetrico() -> None:
    # Arrange: el mismo caso que 1000 / 3, pero en negativo
    monto = D("-1000.00")
    # Act
    partes = repartir_por_pesos(monto, pesos(1, 1, 1))
    # Assert
    assert partes == montos("-333.34", "-333.33", "-333.33")


def test_repartir_por_pesos_con_peso_cero_ese_receptor_recibe_cero() -> None:
    # Arrange: Bodega todavía no tiene computadoras
    monto = D("100.00")
    # Act
    partes = repartir_por_pesos(monto, pesos(1, 0, 1))
    # Assert
    assert partes == montos("50.00", "0.00", "50.00")


def test_repartir_por_pesos_con_un_solo_receptor_le_da_todo() -> None:
    assert repartir_por_pesos(D("123.45"), pesos(7)) == montos("123.45")


def test_repartir_por_pesos_con_monto_cero_da_ceros() -> None:
    assert repartir_por_pesos(D("0.00"), pesos(3, 7)) == montos("0.00", "0.00")


@pytest.mark.parametrize(
    "monto",
    [D("0.01"), D("0.05"), D("999.99"), D("1000.01"), D("-0.07"), D("-12345.67"), D("98765432.10")],
)
def test_repartir_por_pesos_con_cualquier_monto_la_suma_es_exacta(monto: Decimal) -> None:
    # Act
    partes = repartir_por_pesos(monto, pesos(3, 7, 11, 13))
    # Assert
    assert sum(partes, D("0.00")) == monto
    assert all(parte == parte.quantize(D("0.01")) for parte in partes)


@pytest.mark.parametrize(
    ("monto", "proporcion"),
    [
        (D("1.001"), pesos(1, 1)),  # más de 2 decimales
        (D("100.00"), ()),  # ningún receptor
        (D("100.00"), pesos(0, 0, 0)),  # todos los pesos en cero
        (D("100.00"), pesos(-1, 2)),  # un peso negativo
    ],
)
def test_repartir_por_pesos_con_datos_invalidos_lanza_value_error(
    monto: Decimal, proporcion: tuple[Decimal, ...]
) -> None:
    with pytest.raises(ValueError):
        repartir_por_pesos(monto, proporcion)
