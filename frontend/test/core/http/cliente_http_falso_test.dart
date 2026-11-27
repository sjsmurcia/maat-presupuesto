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
    expect(cliente.enviados.single.metodo, 'POST');
  });

  test('actualizar guarda el método PATCH, la ruta y el cuerpo', () async {
    // Arrange
    final cliente = ClienteHttpFalso({'/empresas/e1/cuentas/5204': null});

    // Act
    await cliente.actualizar(
      '/empresas/e1/cuentas/5204',
      cuerpo: {'activa': false},
    );

    // Assert
    final enviado = cliente.enviados.single;
    expect(enviado.metodo, 'PATCH');
    expect(enviado.ruta, '/empresas/e1/cuentas/5204');
    expect(enviado.cuerpo, {'activa': false});
  });

  test('reemplazar guarda el método PUT, la ruta y el cuerpo', () async {
    // Arrange
    final cliente = ClienteHttpFalso({'/empresas/e1/centros/CC-1920': null});

    // Act
    await cliente.reemplazar(
      '/empresas/e1/centros/CC-1920',
      cuerpo: {'tipo': 'ESPECIFICO'},
    );

    // Assert
    final enviado = cliente.enviados.single;
    expect(enviado.metodo, 'PUT');
    expect(enviado.ruta, '/empresas/e1/centros/CC-1920');
    expect(enviado.cuerpo, {'tipo': 'ESPECIFICO'});
  });

  test('una respuesta ErrorDeApi 401 se lanza con su código y mensaje', () {
    // Arrange
    final cliente = ClienteHttpFalso({
      '/auth/sesion': const ErrorDeApi(
        401,
        'El correo o la contraseña no coinciden. '
        'Revisa los dos y vuelve a intentarlo.',
      ),
    });

    // Act y Assert
    expect(
      () => cliente.enviar(
        '/auth/sesion',
        cuerpo: {'correo': 'analista@ejemplo.edu', 'contrasena': 'x'},
      ),
      throwsA(
        isA<ErrorDeApi>()
            .having((e) => e.codigo, 'codigo', 401)
            .having(
              (e) => e.mensaje,
              'mensaje',
              'El correo o la contraseña no coinciden. '
                  'Revisa los dos y vuelve a intentarlo.',
            ),
      ),
    );
  });

  test('una respuesta ErrorDeApi 422 llega con el campo que falló', () {
    // Arrange
    final cliente = ClienteHttpFalso({
      '/empresas/e1/centros/CC-1920': const ErrorDeApi(
        422,
        'CC-1920 tiene la regla RD-02. Un CeCo específico no puede tener '
        'regla: quita la regla antes de cambiar el tipo, o déjalo genérico. '
        'No se guardó ningún cambio.',
        campo: 'tipo',
      ),
    });

    // Act y Assert
    expect(
      () => cliente.reemplazar(
        '/empresas/e1/centros/CC-1920',
        cuerpo: {'tipo': 'ESPECIFICO'},
      ),
      throwsA(
        isA<ErrorDeApi>()
            .having((e) => e.codigo, 'codigo', 422)
            .having((e) => e.campo, 'campo', 'tipo')
            .having((e) => e.mensaje, 'mensaje', contains('RD-02')),
      ),
    );
  });
}
