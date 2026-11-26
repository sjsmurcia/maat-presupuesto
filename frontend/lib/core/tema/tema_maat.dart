import 'package:flutter/material.dart';
import 'package:maat_presupuesto/core/tema/medidas_maat.dart';
import 'package:maat_presupuesto/core/tema/tipografia_maat.dart';
import 'package:maat_presupuesto/core/tema/tokens_maat.dart';

/// Arma el tema de Material a partir de los tokens de Maat. Los colores de
/// la app se leen con `context.tokens`; aquí solo se adapta Material.
ThemeData temaMaat(TokensMaat tokens, Brightness brillo) {
  const esquinas = RoundedRectangleBorder(
    borderRadius: BorderRadius.all(Radius.circular(MedidasMaat.radio)),
  );
  return ThemeData(
    brightness: brillo,
    fontFamily: TipografiaMaat.sans,
    scaffoldBackgroundColor: tokens.surface,
    colorScheme: _esquemaDeColores(tokens, brillo),
    extensions: [tokens],
    filledButtonTheme: const FilledButtonThemeData(
      style: ButtonStyle(shape: WidgetStatePropertyAll(esquinas)),
    ),
    outlinedButtonTheme: const OutlinedButtonThemeData(
      style: ButtonStyle(shape: WidgetStatePropertyAll(esquinas)),
    ),
    dialogTheme: const DialogThemeData(shape: esquinas),
    inputDecorationTheme: const InputDecorationTheme(
      border: OutlineInputBorder(
        borderRadius: BorderRadius.all(Radius.circular(MedidasMaat.radio)),
      ),
    ),
  );
}

ColorScheme _esquemaDeColores(TokensMaat tokens, Brightness brillo) {
  return ColorScheme(
    brightness: brillo,
    primary: tokens.accion,
    onPrimary: tokens.onAccion,
    secondary: tokens.accion,
    onSecondary: tokens.onAccion,
    error: tokens.descuadre,
    onError: tokens.surface,
    surface: tokens.surface,
    onSurface: tokens.texto,
  );
}
