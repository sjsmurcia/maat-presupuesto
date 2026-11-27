import 'package:maat_presupuesto/core/http/cliente_http.dart';

/// El adaptador falso: responde con datos de ejemplo guardados por ruta.
///
/// Sirve para trabajar mientras no hay API y para los widget tests. Una
/// ruta que no tiene respuesta falla como la API: con un 404. Una respuesta
/// que es un `ErrorDeApi` se lanza, para simular un 401 o un 422.
class ClienteHttpFalso implements ClienteHttp {
  ClienteHttpFalso(this._respuestas);

  final Map<String, Object?> _respuestas;

  /// Lo que se envió, en orden, para que un test lo pueda revisar.
  final List<({String metodo, String ruta, Object? cuerpo})> enviados = [];

  @override
  Future<Object?> obtener(
    String ruta, {
    Map<String, String> parametros = const {},
  }) async => _respuestaDe(ruta);

  @override
  Future<Object?> enviar(String ruta, {Object? cuerpo}) async =>
      _registrar('POST', ruta, cuerpo);

  @override
  Future<Object?> actualizar(String ruta, {Object? cuerpo}) async =>
      _registrar('PATCH', ruta, cuerpo);

  @override
  Future<Object?> reemplazar(String ruta, {Object? cuerpo}) async =>
      _registrar('PUT', ruta, cuerpo);

  Object? _registrar(String metodo, String ruta, Object? cuerpo) {
    enviados.add((metodo: metodo, ruta: ruta, cuerpo: cuerpo));
    return _respuestaDe(ruta);
  }

  Object? _respuestaDe(String ruta) {
    if (!_respuestas.containsKey(ruta)) {
      throw ErrorDeApi(404, 'No hay respuesta de ejemplo para $ruta');
    }
    final respuesta = _respuestas[ruta];
    if (respuesta is ErrorDeApi) throw respuesta;
    return respuesta;
  }
}
