import 'package:dio/dio.dart';

/// El puerto por el que las pantallas hablan con la API. Las pantallas no
/// saben si del otro lado está la API de verdad o el adaptador falso.
abstract interface class ClienteHttp {
  Future<Object?> obtener(String ruta, {Map<String, String> parametros});

  Future<Object?> enviar(String ruta, {Object? cuerpo});

  /// PATCH: cambia solo los campos que van en el cuerpo.
  Future<Object?> actualizar(String ruta, {Object? cuerpo});

  /// PUT: reemplaza el recurso completo con el cuerpo.
  Future<Object?> reemplazar(String ruta, {Object? cuerpo});
}

/// Un error de la API, con el mensaje que la pantalla muestra tal cual: las
/// reglas y sus mensajes viven en el dominio, no en la pantalla.
class ErrorDeApi implements Exception {
  const ErrorDeApi(this.codigo, this.mensaje, {this.campo});

  final int codigo;
  final String mensaje;

  /// El dato que falló, para mostrar el error en su lugar. Es null cuando el
  /// error es de toda la acción, como un 401.
  final String? campo;

  @override
  String toString() => 'ErrorDeApi($codigo): $mensaje';
}

/// El adaptador de la API de verdad. Todavía no se usa: entra cuando la API
/// exista (MP-4).
class ClienteHttpDio implements ClienteHttp {
  ClienteHttpDio(String urlBase) : _dio = Dio(BaseOptions(baseUrl: urlBase));

  final Dio _dio;

  @override
  Future<Object?> obtener(
    String ruta, {
    Map<String, String> parametros = const {},
  }) async {
    final respuesta = await _dio.get<Object?>(
      ruta,
      queryParameters: parametros,
    );
    return respuesta.data;
  }

  @override
  Future<Object?> enviar(String ruta, {Object? cuerpo}) async {
    final respuesta = await _dio.post<Object?>(ruta, data: cuerpo);
    return respuesta.data;
  }

  @override
  Future<Object?> actualizar(String ruta, {Object? cuerpo}) async {
    final respuesta = await _dio.patch<Object?>(ruta, data: cuerpo);
    return respuesta.data;
  }

  @override
  Future<Object?> reemplazar(String ruta, {Object? cuerpo}) async {
    final respuesta = await _dio.put<Object?>(ruta, data: cuerpo);
    return respuesta.data;
  }
}
