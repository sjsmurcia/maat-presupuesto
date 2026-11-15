from decimal import Decimal

import pytest

from presupuesto.dominio import (
    Ejecucion,
    EstadoPartida,
    calcular_ejecucion,
    clasificar,
    repartir_en_meses,
)

D = Decimal


def pesos(*valores: int) -> tuple[Decimal, ...]:
    return tuple(D(v) for v in valores)


# ---------- repartir_en_meses ----------


def test_repartir_en_meses_cuando_divide_exacto_da_doce_partes_iguales() -> None:
    # Arrange
    total = D("1200.00")
    # Act
    meses = repartir_en_meses(total)
    # Assert
    assert meses == (D("100.00"),) * 12


def test_repartir_en_meses_cuando_sobran_centavos_van_a_los_primeros_meses() -> None:
    # Arrange: 1000 / 12 = 83.333...; truncado suma 999.96 y sobran 4 centavos
    total = D("1000.00")
    # Act
    meses = repartir_en_meses(total)
    # Assert
    assert meses == (D("83.34"),) * 4 + (D("83.33"),) * 8


def test_repartir_en_meses_cuando_un_residuo_es_mayor_gana_aunque_sea_mes_posterior() -> None:
    # Arrange: 1.00 en proporción 1:2 → 0.333 (residuo 0.0033) y 0.666 (residuo 0.0067)
    total = D("1.00")
    proporcion = pesos(1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    # Act
    meses = repartir_en_meses(total, proporcion)
    # Assert: el centavo que sobra va a febrero, no a enero
    assert meses == (D("0.33"), D("0.67")) + (D("0.00"),) * 10


def test_repartir_en_meses_cuando_hay_estacionalidad_respeta_los_pesos() -> None:
    # Arrange: diciembre pesa 13 veces un mes normal
    total = D("2400.00")
    proporcion = pesos(1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 13)
    # Act
    meses = repartir_en_meses(total, proporcion)
    # Assert
    assert meses == (D("100.00"),) * 11 + (D("1300.00"),)


def test_repartir_en_meses_cuando_el_total_es_cero_da_doce_ceros() -> None:
    assert repartir_en_meses(D("0.00")) == (D("0.00"),) * 12


@pytest.mark.parametrize(
    "total",
    [D("0.01"), D("0.05"), D("0.11"), D("999.99"), D("1000.01"), D("123456789.07")],
)
def test_repartir_en_meses_con_cualquier_total_la_suma_es_exacta(total: Decimal) -> None:
    # Act
    meses = repartir_en_meses(total)
    # Assert
    assert sum(meses, D("0.00")) == total
    assert all(mes == mes.quantize(D("0.01")) for mes in meses)


@pytest.mark.parametrize(
    ("total", "proporcion"),
    [
        (D("-1.00"), None),  # negativo
        (D("1.001"), None),  # más de 2 decimales
        (D("100.00"), pesos(1, 1, 1)),  # no son 12 pesos
        (D("100.00"), pesos(*([0] * 12))),  # todos cero
        (D("100.00"), pesos(-1, *([1] * 11))),  # un peso negativo
    ],
)
def test_repartir_en_meses_con_datos_invalidos_lanza_value_error(
    total: Decimal, proporcion: tuple[Decimal, ...] | None
) -> None:
    with pytest.raises(ValueError):
        if proporcion is None:
            repartir_en_meses(total)
        else:
            repartir_en_meses(total, proporcion)


# ---------- calcular_ejecucion ----------


@pytest.mark.parametrize(
    ("presupuestado", "real", "variacion", "porcentaje"),
    [
        (D("1000.00"), D("850.00"), D("-150.00"), D("85.00")),
        (D("1000.00"), D("1234.56"), D("234.56"), D("123.46")),  # 123.456 sube
        (D("300.00"), D("100.00"), D("-200.00"), D("33.33")),  # 33.333 baja
        (D("1000.00"), D("0.00"), D("-1000.00"), D("0.00")),
    ],
)
def test_calcular_ejecucion_da_variacion_y_porcentaje_exactos(
    presupuestado: Decimal, real: Decimal, variacion: Decimal, porcentaje: Decimal
) -> None:
    # Act
    ejecucion = calcular_ejecucion(presupuestado, real)
    # Assert
    assert ejecucion == Ejecucion(presupuestado, real, variacion, porcentaje)


def test_calcular_ejecucion_en_un_medio_exacto_redondea_hacia_arriba() -> None:
    # Arrange: 0.01 / 200 × 100 = 0.005 → HALF_UP da 0.01; el bancario daría 0.00
    # Act
    ejecucion = calcular_ejecucion(D("200.00"), D("0.01"))
    # Assert
    assert ejecucion.porcentaje == D("0.01")


def test_calcular_ejecucion_sin_presupuesto_no_tiene_porcentaje() -> None:
    # Act
    ejecucion = calcular_ejecucion(D("0.00"), D("50.00"))
    # Assert
    assert ejecucion == Ejecucion(D("0.00"), D("50.00"), D("50.00"), None)


# ---------- clasificar ----------


@pytest.mark.parametrize(
    ("presupuestado", "real", "estado"),
    [
        (D("1000.00"), D("500.00"), EstadoPartida.DENTRO),
        (D("1000.00"), D("899.90"), EstadoPartida.DENTRO),  # 89.99 %
        (D("1000.00"), D("899.99"), EstadoPartida.ALERTA),  # se muestra 90.00 %
        (D("1000.00"), D("900.00"), EstadoPartida.ALERTA),  # justo el umbral
        (D("1000.00"), D("1000.00"), EstadoPartida.ALERTA),  # gastado todo, no excedido
        (D("1000.00"), D("1000.01"), EstadoPartida.EXCEDIDO),  # se muestra 100.00 %
        (D("0.00"), D("0.00"), EstadoPartida.DENTRO),
        (D("0.00"), D("50.00"), EstadoPartida.EXCEDIDO),  # gasto sin presupuesto
        (D("1000.00"), D("-20.00"), EstadoPartida.DENTRO),  # devolución neta
    ],
)
def test_clasificar_da_el_estado_de_la_partida(
    presupuestado: Decimal, real: Decimal, estado: EstadoPartida
) -> None:
    # Arrange
    ejecucion = calcular_ejecucion(presupuestado, real)
    # Act / Assert
    assert clasificar(ejecucion) == estado


def test_clasificar_con_umbral_propio_lo_respeta() -> None:
    # Arrange
    ejecucion = calcular_ejecucion(D("1000.00"), D("750.00"))
    # Act / Assert
    assert clasificar(ejecucion, umbral=D("75")) == EstadoPartida.ALERTA


@pytest.mark.parametrize("umbral", [D("0"), D("-5"), D("100.01")])
def test_clasificar_con_umbral_fuera_de_rango_lanza_value_error(umbral: Decimal) -> None:
    ejecucion = calcular_ejecucion(D("1000.00"), D("500.00"))
    with pytest.raises(ValueError):
        clasificar(ejecucion, umbral=umbral)
