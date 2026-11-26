import 'package:maat_presupuesto/core/http/cliente_http.dart';

/// El adaptador falso: responde con datos de ejemplo guardados por ruta.
///
/// Sirve para trabajar mientras no hay API y para los widget tests. Una
/// ruta que no tiene respuesta falla como la API: con un 404.
class ClienteHttpFalso implements ClienteHttp {
  ClienteHttpFalso(this._respuestas);

  final Map<String, Object?> _respuestas;

  /// Lo que se envió, en orden, para que un test lo pueda revisar.
  final List<({String ruta, Object? cuerpo})> enviados = [];

  @override
  Future<Object?> obtener(
    String ruta, {
    Map<String, String> parametros = const {},
  }) async => _respuestaDe(ruta);

  @override
  Future<Object?> enviar(String ruta, {Object? cuerpo}) async {
    enviados.add((ruta: ruta, cuerpo: cuerpo));
    return _respuestaDe(ruta);
  }

  Object? _respuestaDe(String ruta) {
    if (!_respuestas.containsKey(ruta)) {
      throw ErrorDeApi(404, 'No hay respuesta de ejemplo para $ruta');
    }
    return _respuestas[ruta];
  }
}
