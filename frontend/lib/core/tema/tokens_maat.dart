import 'package:flutter/material.dart';

/// Los colores por rol del tema Tierra neutra de Maat, en claro y en oscuro.
///
/// Ningún color de la app se usa fuera de esta tabla. El oscuro tiene sus
/// propios valores: no se calcula invirtiendo el claro.
@immutable
class TokensMaat extends ThemeExtension<TokensMaat> {
  const TokensMaat({
    required this.chrome,
    required this.surface,
    required this.texto,
    required this.tenue,
    required this.accion,
    required this.onAccion,
    required this.acento,
    required this.borde,
    required this.bordeVar,
    required this.cuadra,
    required this.cuadraFondo,
    required this.descuadre,
    required this.descuadreFondo,
    required this.borrador,
    required this.borradorFondo,
    required this.inmutable,
    required this.inmutableFondo,
    required this.info,
    required this.infoFondo,
    required this.natIngreso,
    required this.natCosto,
    required this.natGasto,
  });

  static const claro = TokensMaat(
    chrome: Color(0xFFEDE9E6),
    surface: Color(0xFFFBFAF9),
    texto: Color(0xFF5C4F4A),
    tenue: Color(0xFF8B807A),
    accion: Color(0xFF5C766D),
    onAccion: Color(0xFFFFFFFF),
    acento: Color(0xFFC9996B),
    borde: Color(0xFFD8D2CC),
    bordeVar: Color(0xFFE3DEDA),
    cuadra: Color(0xFF356B44),
    cuadraFondo: Color(0xFFE2EDE4),
    descuadre: Color(0xFFB3403C),
    descuadreFondo: Color(0xFFF8E9E8),
    borrador: Color(0xFF8A6116),
    borradorFondo: Color(0xFFF6EDDB),
    inmutable: Color(0xFF635B55),
    inmutableFondo: Color(0xFFE7E2DE),
    info: Color(0xFF4A6470),
    infoFondo: Color(0xFFE4EBEE),
    natIngreso: Color(0xFF33655A),
    natCosto: Color(0xFF6B4A5E),
    natGasto: Color(0xFF96432F),
  );

  static const oscuro = TokensMaat(
    chrome: Color(0xFF262220),
    surface: Color(0xFF1D1A18),
    texto: Color(0xFFE5DFDA),
    tenue: Color(0xFF9A8F89),
    accion: Color(0xFF8FA89E),
    onAccion: Color(0xFF14201B),
    acento: Color(0xFFC9996B),
    borde: Color(0xFF413B37),
    bordeVar: Color(0xFF332E2A),
    cuadra: Color(0xFF8CC29B),
    cuadraFondo: Color(0xFF25322A),
    descuadre: Color(0xFFE59490),
    descuadreFondo: Color(0xFF3A2523),
    borrador: Color(0xFFD9B36A),
    borradorFondo: Color(0xFF383021),
    inmutable: Color(0xFFA79E98),
    inmutableFondo: Color(0xFF302C29),
    info: Color(0xFF9BB4C0),
    infoFondo: Color(0xFF222C31),
    natIngreso: Color(0xFF85B5A9),
    natCosto: Color(0xFFC099AF),
    natGasto: Color(0xFFD28A72),
  );

  /// Barra lateral, pies de pantalla y filas de grupo.
  final Color chrome;

  /// Área de trabajo, campos y diálogos.
  final Color surface;
  final Color texto;

  /// Rótulos, metadatos y encabezados de tabla.
  final Color tenue;

  /// Botón primario, enlaces, fila seleccionada y foco.
  final Color accion;
  final Color onAccion;

  /// Solo el hover de un enlace y la barra del logo.
  final Color acento;
  final Color borde;
  final Color bordeVar;
  final Color cuadra;
  final Color cuadraFondo;
  final Color descuadre;
  final Color descuadreFondo;
  final Color borrador;
  final Color borradorFondo;
  final Color inmutable;
  final Color inmutableFondo;
  final Color info;
  final Color infoFondo;

  /// Las naturalezas solo tiñen texto y chips, nunca fondos.
  final Color natIngreso;
  final Color natCosto;
  final Color natGasto;

  /// Los tokens son fijos: no se copian con cambios.
  @override
  TokensMaat copyWith() => this;

  /// Sin transición de colores entre temas: cambia de golpe a la mitad.
  @override
  TokensMaat lerp(TokensMaat? other, double t) =>
      other == null || t < 0.5 ? this : other;
}

/// Atajo para leer los tokens desde cualquier widget.
extension TokensDelContexto on BuildContext {
  TokensMaat get tokens => Theme.of(this).extension<TokensMaat>()!;
}
