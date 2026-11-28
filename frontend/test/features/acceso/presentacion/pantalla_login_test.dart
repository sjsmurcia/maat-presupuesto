import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:go_router/go_router.dart';
import 'package:maat_presupuesto/app/proveedores.dart';
import 'package:maat_presupuesto/core/http/cliente_http_falso.dart';
import 'package:maat_presupuesto/core/sesion/sesion_provider.dart';
import 'package:maat_presupuesto/core/tema/tema_maat.dart';
import 'package:maat_presupuesto/core/tema/tokens_maat.dart';
import 'package:maat_presupuesto/features/acceso/presentacion/pantalla_login.dart';
import 'package:material_symbols_icons/symbols.dart';

const _correo = 'analista@ejemplo.edu';

const _sesionBuena = <String, Object?>{
  '/auth/sesion': {
    'token': 'tk-demo',
    'usuario': {'correo': _correo},
  },
};

/// La app con el login y un `/empresa` de relleno, para no depender del
/// router real. Devuelve el contenedor para revisar la sesión al final.
Future<ProviderContainer> _abrirLogin(
  WidgetTester tester,
  ClienteHttpFalso cliente,
) async {
  final contenedor = ProviderContainer.test(
    overrides: [clienteHttpProvider.overrideWithValue(cliente)],
  );
  final router = GoRouter(
    initialLocation: '/login',
    routes: [
      GoRoute(path: '/login', builder: (_, _) => const PantallaLogin()),
      GoRoute(path: '/empresa', builder: (_, _) => const Text('empresa')),
    ],
  );
  await tester.pumpWidget(
    UncontrolledProviderScope(
      container: contenedor,
      child: MaterialApp.router(
        theme: temaMaat(TokensMaat.claro, Brightness.light),
        routerConfig: router,
      ),
    ),
  );
  await tester.pumpAndSettle();
  return contenedor;
}

Future<void> _entrar(WidgetTester tester, String contrasena) async {
  await tester.enterText(find.byType(TextField).first, _correo);
  await tester.enterText(find.byType(TextField).last, contrasena);
  await tester.tap(find.text('Iniciar sesión'));
  await tester.pumpAndSettle();
}

TextField _campoContrasena(WidgetTester tester) =>
    tester.widget<TextField>(find.byType(TextField).last);

void main() {
  testWidgets('el login al abrir muestra los textos del artboard', (
    tester,
  ) async {
    // Arrange y Act
    await _abrirLogin(tester, ClienteHttpFalso(_sesionBuena));

    // Assert
    expect(find.text('Maat Presupuesto'), findsOneWidget);
    expect(
      find.text('Presupuesto por cuenta y su ejecución por área.'),
      findsOneWidget,
    );
    expect(find.text('CORREO ELECTRÓNICO'), findsOneWidget);
    expect(find.text('CONTRASEÑA'), findsOneWidget);
    expect(find.text('Iniciar sesión'), findsOneWidget);
    expect(
      find.text('¿No tienes acceso? Pídeselo al administrador de tu firma.'),
      findsOneWidget,
    );
  });

  testWidgets(
    'el login con credenciales buenas envía correo y contraseña, guarda la '
    'sesión y va a /empresa',
    (tester) async {
      // Arrange
      final cliente = ClienteHttpFalso(_sesionBuena);
      final contenedor = await _abrirLogin(tester, cliente);

      // Act
      await _entrar(tester, 'secreta');

      // Assert
      final enviado = cliente.enviados.single;
      expect(enviado.metodo, 'POST');
      expect(enviado.ruta, '/auth/sesion');
      expect(enviado.cuerpo, {'correo': _correo, 'contrasena': 'secreta'});
      expect(contenedor.read(sesionProvider)!.token, 'tk-demo');
      expect(contenedor.read(sesionProvider)!.correo, _correo);
      expect(find.text('empresa'), findsOneWidget);
    },
  );

  testWidgets('tocar ver contraseña muestra el texto oculto', (tester) async {
    // Arrange
    await _abrirLogin(tester, ClienteHttpFalso(_sesionBuena));
    expect(_campoContrasena(tester).obscureText, isTrue);

    // Act
    await tester.tap(find.byIcon(Symbols.visibility));
    await tester.pump();

    // Assert
    expect(_campoContrasena(tester).obscureText, isFalse);
  });
}
