import 'package:flutter_test/flutter_test.dart';
import 'package:maat_presupuesto/core/http/cliente_http.dart';
import 'package:maat_presupuesto/core/http/cliente_http_falso.dart';

void main() {
  test('obtener con una ruta conocida devuelve su ejemplo', () async {
    // Arrange
    final cliente = ClienteHttpFalso({
      '/empresas': [
        {'id': 'e1', 'nombre': 'Universidad Ejemplo'},
      ],
    });

    // Act
    final respuesta = await cliente.obtener('/empresas');

    // Assert
    expect(respuesta, [
      {'id': 'e1', 'nombre': 'Universidad Ejemplo'},
    ]);
  });

  test('obtener con una ruta sin ejemplo falla como la API, con 404', () {
    final cliente = ClienteHttpFalso(const {});

    expect(
      () => cliente.obtener('/tablero'),
      throwsA(
        isA<ErrorDeApi>()
            .having((e) => e.codigo, 'codigo', 404)
            .having((e) => e.mensaje, 'mensaje', contains('/tablero')),
      ),
    );
  });

  test('enviar guarda lo enviado para que el test lo revise', () async {
    final cliente = ClienteHttpFalso({'/presupuesto/aprobar': null});

    await cliente.enviar('/presupuesto/aprobar', cuerpo: {'anio': 2027});

    expect(cliente.enviados.single.cuerpo, {'anio': 2027});
  });
}
