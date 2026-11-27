import pytest

from presupuesto.cuentas import Naturaleza, recibe_presupuesto

SE_PRESUPUESTAN = [Naturaleza.INGRESO, Naturaleza.COSTO, Naturaleza.GASTO]


@pytest.mark.parametrize(
    ("naturaleza", "esperado"),
    [
        (Naturaleza.INGRESO, True),
        (Naturaleza.COSTO, True),
        (Naturaleza.GASTO, True),
        (Naturaleza.ACTIVO, False),
        (Naturaleza.PASIVO, False),
        (Naturaleza.PATRIMONIO, False),
    ],
)
def test_recibe_presupuesto_cuenta_de_detalle_activa_depende_de_su_naturaleza(
    naturaleza: Naturaleza, esperado: bool
) -> None:
    # Act
    recibe = recibe_presupuesto(naturaleza, es_detalle=True, esta_activa=True)
    # Assert
    assert recibe is esperado


@pytest.mark.parametrize("naturaleza", SE_PRESUPUESTAN)
def test_recibe_presupuesto_cuenta_de_grupo_no_recibe(naturaleza: Naturaleza) -> None:
    # Arrange: 5 Gastos agrupa a 5204 Servicios en la nube; se presupuesta la hija
    # Act
    recibe = recibe_presupuesto(naturaleza, es_detalle=False, esta_activa=True)
    # Assert
    assert recibe is False


@pytest.mark.parametrize("naturaleza", SE_PRESUPUESTAN)
def test_recibe_presupuesto_cuenta_inactiva_no_recibe(naturaleza: Naturaleza) -> None:
    # Arrange: una cuenta que ya no se usa se inactiva, no se borra
    # Act
    recibe = recibe_presupuesto(naturaleza, es_detalle=True, esta_activa=False)
    # Assert
    assert recibe is False


def test_recibe_presupuesto_cuenta_de_grupo_inactiva_no_recibe() -> None:
    # Act
    recibe = recibe_presupuesto(Naturaleza.GASTO, es_detalle=False, esta_activa=False)
    # Assert
    assert recibe is False
