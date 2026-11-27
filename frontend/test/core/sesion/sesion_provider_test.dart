import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:maat_presupuesto/core/sesion/sesion.dart';
import 'package:maat_presupuesto/core/sesion/sesion_provider.dart';

const _universidad = EmpresaElegida(
  id: 'e1',
  nombre: 'Universidad Ejemplo',
  permisos: {'catalogo.editar'},
  areas: null,
  ejercicioActual: 2026,
  mesAbierto: '2026-10',
  estadoPresupuesto: 'APROBADO',
);

void main() {
  test('sin iniciar, la sesión es null', () {
    final contenedor = ProviderContainer.test();

    expect(contenedor.read(sesionProvider), isNull);
  });

  test('iniciar guarda el token y el correo, sin empresa', () {
    // Arrange
    final contenedor = ProviderContainer.test();

    // Act
    contenedor
        .read(sesionProvider.notifier)
        .iniciar(token: 'tk-1', correo: 'analista@ejemplo.edu');

    // Assert
    final sesion = contenedor.read(sesionProvider)!;
    expect(sesion.token, 'tk-1');
    expect(sesion.correo, 'analista@ejemplo.edu');
    expect(sesion.empresa, isNull);
  });

  test('elegirEmpresa deja la empresa en la sesión y conserva el token', () {
    // Arrange
    final contenedor = ProviderContainer.test();
    contenedor
        .read(sesionProvider.notifier)
        .iniciar(token: 'tk-1', correo: 'analista@ejemplo.edu');

    // Act
    contenedor.read(sesionProvider.notifier).elegirEmpresa(_universidad);

    // Assert
    final sesion = contenedor.read(sesionProvider)!;
    expect(sesion.empresa, same(_universidad));
    expect(sesion.token, 'tk-1');
  });

  test('elegirEmpresa sin sesión no crea una', () {
    // Arrange
    final contenedor = ProviderContainer.test();

    // Act
    contenedor.read(sesionProvider.notifier).elegirEmpresa(_universidad);

    // Assert
    expect(contenedor.read(sesionProvider), isNull);
  });

  test('cerrar vuelve la sesión a null', () {
    // Arrange
    final contenedor = ProviderContainer.test();
    contenedor.read(sesionProvider.notifier)
      ..iniciar(token: 'tk-1', correo: 'analista@ejemplo.edu')
      ..elegirEmpresa(_universidad);

    // Act
    contenedor.read(sesionProvider.notifier).cerrar();

    // Assert
    expect(contenedor.read(sesionProvider), isNull);
  });
}
