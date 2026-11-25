import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:maat_presupuesto/core/http/cliente_http.dart';
import 'package:maat_presupuesto/core/http/cliente_http_falso.dart';

/// El cliente HTTP que usa toda la app.
///
/// Mientras no hay API es el adaptador falso: cada funcionalidad agrega sus
/// datos de ejemplo en `features/<funcionalidad>/datos/` y se suman aquí.
/// Cuando la API exista, se cambia por `ClienteHttpDio` en esta línea y
/// ninguna pantalla cambia. Los tests lo reemplazan con `overrides`.
final clienteHttpProvider = Provider<ClienteHttp>(
  (ref) => ClienteHttpFalso(const {}),
);
