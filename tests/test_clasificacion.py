import pytest

from presupuesto.clasificacion import Destino, TipoCeco, clasificar_movimiento


@pytest.mark.parametrize(
    ("tipo", "tiene_regla", "esperado"),
    [
        (TipoCeco.ESPECIFICO, False, Destino.DIRECTO),  # papelería de Ventas
        (TipoCeco.GENERICO, True, Destino.DISTRIBUIDO),  # AWS por computadoras
        (TipoCeco.GENERICO, False, Destino.CENTRALIZADO),  # CeCo nuevo, sin regla todavía
        (TipoCeco.INSTITUCIONAL, False, Destino.CENTRALIZADO),  # auditoría externa
    ],
)
def test_clasificar_movimiento_segun_tipo_y_regla_da_su_destino(
    tipo: TipoCeco, tiene_regla: bool, esperado: Destino
) -> None:
    # Act
    destino = clasificar_movimiento(tipo, tiene_regla)
    # Assert
    assert destino is esperado


@pytest.mark.parametrize("tipo", [TipoCeco.ESPECIFICO, TipoCeco.INSTITUCIONAL])
def test_clasificar_movimiento_ceco_que_no_se_reparte_con_regla_lanza_value_error(
    tipo: TipoCeco,
) -> None:
    with pytest.raises(ValueError):
        clasificar_movimiento(tipo, tiene_regla=True)
