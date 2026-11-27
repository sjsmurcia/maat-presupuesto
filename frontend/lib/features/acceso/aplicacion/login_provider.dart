import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:maat_presupuesto/core/http/cliente_http.dart';
import 'package:maat_presupuesto/core/sesion/sesion_provider.dart';
import 'package:maat_presupuesto/features/acceso/datos/acceso_api.dart';

/// Se descarta al salir del login, para que un error viejo no aparezca al
/// volver después de cerrar sesión.
final NotifierProvider<LoginNotifier, String?> loginProvider =
    NotifierProvider.autoDispose(LoginNotifier.new);

/// El estado del login: el mensaje de error de la API, o null si no hay.
class LoginNotifier extends Notifier<String?> {
  @override
  String? build() => null;

  /// Devuelve si se entró, para que la pantalla sepa si seguir a la empresa.
  Future<bool> iniciar({
    required String correo,
    required String contrasena,
  }) async {
    try {
      final usuario = await ref
          .read(accesoApiProvider)
          .iniciarSesion(correo: correo, contrasena: contrasena);
      ref
          .read(sesionProvider.notifier)
          .iniciar(token: usuario.token, correo: usuario.correo);
      state = null;
      return true;
    } on ErrorDeApi catch (error) {
      state = error.mensaje;
      return false;
    }
  }
}
