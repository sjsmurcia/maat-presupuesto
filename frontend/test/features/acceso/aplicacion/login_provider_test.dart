import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:maat_presupuesto/app/proveedores.dart';
import 'package:maat_presupuesto/core/http/cliente_http.dart';
import 'package:maat_presupuesto/core/http/cliente_http_falso.dart';
import 'package:maat_presupuesto/core/sesion/sesion_provider.dart';
import 'package:maat_presupuesto/features/acceso/aplicacion/login_provider.dart';
import 'package:maat_presupuesto/features/acceso/datos/ejemplos_acceso.dart';

const _mensajeDeError =
    'El correo o la contraseña no coinciden. Revisa los dos y vuelve a '
    'intentarlo.';

/// El login es autoDispose: se escucha para que no se descarte a mitad de
/// la llamada, como pasa en la pantalla, que lo está mirando.
ProviderContainer _contenedor(Map<String, Object?> respuestas) {
  final contenedor = ProviderContainer.test(
    overrides: [
      clienteHttpProvider.overrideWithValue(ClienteHttpFalso(respuestas)),
    ],
  )..listen(loginProvider, (_, _) {});
  return contenedor;
}

void main() {
  test(
    'iniciar con credenciales buenas guarda la sesión y devuelve true',
    () async {
      // Arrange
      final contenedor = _contenedor(ejemplosAcceso);

      // Act
      final entro = await contenedor
          .read(loginProvider.notifier)
          .iniciar(correo: 'analista@ejemplo.edu', contrasena: 'secreta');

      // Assert
      final sesion = contenedor.read(sesionProvider)!;
      expect(entro, isTrue);
      expect(sesion.token, 'tk-demo');
      expect(sesion.correo, 'analista@ejemplo.edu');
      expect(contenedor.read(loginProvider), isNull);
    },
  );

  test(
    'iniciar con un 401 guarda el mensaje de la API y no crea la sesión',
    () async {
      // Arrange
      final contenedor = _contenedor({
        '/auth/sesion': const ErrorDeApi(401, _mensajeDeError),
      });

      // Act
      final entro = await contenedor
          .read(loginProvider.notifier)
          .iniciar(correo: 'analista@ejemplo.edu', contrasena: 'equivocada');

      // Assert
      expect(entro, isFalse);
      expect(contenedor.read(loginProvider), _mensajeDeError);
      expect(contenedor.read(sesionProvider), isNull);
    },
  );
}
