import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:maat_presupuesto/app/barra_lateral.dart';
import 'package:maat_presupuesto/app/destinos.dart';
import 'package:maat_presupuesto/app/router.dart';
import 'package:maat_presupuesto/core/tema/tema_maat.dart';
import 'package:maat_presupuesto/core/tema/tokens_maat.dart';

Widget _app(String inicio) => MaterialApp.router(
  theme: temaMaat(TokensMaat.claro, Brightness.light),
  routerConfig: crearRouter(inicio: inicio),
);

void main() {
  for (final destino in Destino.values) {
    testWidgets('la ruta ${destino.ruta} abre su pantalla con la barra', (
      tester,
    ) async {
      // Arrange y Act
      await tester.pumpWidget(_app(destino.ruta));
      await tester.pumpAndSettle();

      // Assert: el título está en la barra y en la pantalla.
      expect(find.byType(BarraLateral), findsOneWidget);
      expect(find.text(destino.titulo), findsWidgets);
    });
  }

  testWidgets('el login va sin barra lateral', (tester) async {
    await tester.pumpWidget(_app('/login'));
    await tester.pumpAndSettle();

    expect(find.text('Iniciar sesión'), findsOneWidget);
    expect(find.byType(BarraLateral), findsNothing);
  });

  testWidgets('tocar un destino de la barra lleva a su pantalla', (
    tester,
  ) async {
    // Arrange
    await tester.pumpWidget(_app(Destino.tablero.ruta));
    await tester.pumpAndSettle();

    // Act
    await tester.tap(find.text('Cierre del mes'));
    await tester.pumpAndSettle();

    // Assert: el título aparece en la barra y en la pantalla.
    expect(find.text('Cierre del mes'), findsNWidgets(2));
  });
}
