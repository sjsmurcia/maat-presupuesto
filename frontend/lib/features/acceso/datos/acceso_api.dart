import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:maat_presupuesto/app/proveedores.dart';
import 'package:maat_presupuesto/core/http/cliente_http.dart';

final accesoApiProvider = Provider<AccesoApi>(
  (ref) => AccesoApi(ref.watch(clienteHttpProvider)),
);

/// Habla con la API de acceso. Un 401 sube como `ErrorDeApi`, sin tocarlo:
/// su mensaje es el que la pantalla muestra tal cual.
class AccesoApi {
  const AccesoApi(this._cliente);

  final ClienteHttp _cliente;

  Future<({String token, String correo})> iniciarSesion({
    required String correo,
    required String contrasena,
  }) async {
    final respuesta = await _cliente.enviar(
      '/auth/sesion',
      cuerpo: {'correo': correo, 'contrasena': contrasena},
    );
    final json = respuesta! as Map<String, Object?>;
    final usuario = json['usuario']! as Map<String, Object?>;
    return (
      token: json['token']! as String,
      correo: usuario['correo']! as String,
    );
  }
}
