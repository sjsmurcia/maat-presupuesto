import 'package:flutter/widgets.dart';

/// Las medidas del sistema Maat. Radio de 3px en todo, sin sombras salvo en
/// los diálogos y sin degradados.
abstract final class MedidasMaat {
  static const radio = 3.0;

  /// La marca del ítem activo y de la celda con error, al borde izquierdo.
  static const marca = 2.0;

  // Barra lateral
  static const barraExpandida = 236.0;
  static const barraColapsada = 60.0;
  static const itemBarraAlto = 32.0;
  static const iconoBarra = 19.0;
  static const separacionGrupos = 18.0;

  // Cabecera de pantalla
  static const cabeceraPadding = EdgeInsets.fromLTRB(24, 14, 24, 12);
  static const cabeceraGap = 12.0;

  // Tablas
  static const encabezadoTabla = 30.0;
  static const encabezadoBanda = 26.0;
  static const filaLectura = 32.0;
  static const filaEditable = 34.0;
  static const filaDosLineas = 42.0;
  static const pieTotales = 36.0;
  static const margenLateral = 24.0;

  // Botones
  static const botonCabecera = 34.0;
  static const botonPie = 38.0;
  static const botonDialogo = 36.0;
  static const botonAcceso = 40.0;

  // Campos
  static const campoFiltro = 34.0;
  static const campoDialogo = 36.0;
  static const campoAcceso = 38.0;

  // Diálogos
  static const dialogoMinimo = 460.0;
  static const dialogoMaximo = 620.0;
  static const dialogoPadding = 20.0;

  /// Una acción que no se puede usar se ve atenuada, nunca se esconde.
  static const opacidadDeshabilitado = 0.45;
}
