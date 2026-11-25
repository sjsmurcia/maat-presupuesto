import 'package:flutter/widgets.dart';

/// La tipografía de Maat: IBM Plex Sans para todo y Plex Mono solo para
/// códigos. Ninguna cifra va en Mono: los montos usan cifras tabulares, que
/// son las que alinean las columnas.
abstract final class TipografiaMaat {
  static const sans = 'IBM Plex Sans';
  static const mono = 'IBM Plex Mono';
  static const cifras = [FontFeature.tabularFigures()];

  static const tituloPantalla = TextStyle(
    fontSize: 20,
    fontWeight: FontWeight.w600,
    letterSpacing: -0.2,
  );

  static const cifraResumen = TextStyle(
    fontSize: 19,
    fontWeight: FontWeight.w600,
    fontFeatures: cifras,
  );

  static const celda = TextStyle(fontSize: 13);

  static const monto = TextStyle(fontSize: 13, fontFeatures: cifras);

  static const codigo = TextStyle(fontFamily: mono, fontSize: 13);

  /// Encabezado de columna y rótulo de campo: va en mayúsculas.
  static const encabezado = TextStyle(fontSize: 10, letterSpacing: 1);

  /// Chip de estado (BORRADOR, CERRADO, SOBREGIRO): va en mayúsculas.
  static const chip = TextStyle(
    fontSize: 11,
    fontWeight: FontWeight.w600,
    letterSpacing: 0.4,
  );

  static const nota = TextStyle(fontSize: 11);
}
