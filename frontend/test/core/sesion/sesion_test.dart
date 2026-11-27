import 'package:flutter_test/flutter_test.dart';
import 'package:maat_presupuesto/core/sesion/sesion.dart';

const _universidad = EmpresaElegida(
  id: 'e1',
  nombre: 'Universidad Ejemplo',
  permisos: {'catalogo.editar', 'tablero.ver'},
  areas: null,
  ejercicioActual: 2026,
  mesAbierto: '2026-10',
  estadoPresupuesto: 'APROBADO',
);

void main() {
  for (final (permiso, esperado) in [
    ('catalogo.editar', true),
    ('cierre.ejecutar', false),
  ]) {
    test('tienePermiso con $permiso devuelve $esperado', () {
      // Act
      final tiene = _universidad.tienePermiso(permiso);

      // Assert
      expect(tiene, esperado);
    });
  }
}
