import 'package:decimal/decimal.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:maat_presupuesto/core/montos/montos.dart';

void main() {
  group('formatearMonto', () {
    const casos = {
      '0': '0.00',
      '8333.34': '8,333.34',
      '1234567.8': '1,234,567.80',
      '-5150': '(5,150.00)',
    };
    for (final MapEntry(key: monto, value: esperado) in casos.entries) {
      test('con $monto escribe $esperado', () {
        // Arrange
        final valor = Decimal.parse(monto);

        // Act
        final texto = formatearMonto(valor);

        // Assert
        expect(texto, esperado);
      });
    }
  });

  group('montoDesdeJson', () {
    test('con texto devuelve el Decimal exacto', () {
      expect(montoDesdeJson('185000.10'), Decimal.parse('185000.10'));
    });

    test('con un double lo rechaza en vez de perder centavos', () {
      expect(
        () => montoDesdeJson(0.1),
        throwsA(
          isA<FormatException>().having(
            (e) => e.message,
            'mensaje',
            contains('El dinero llega como texto'),
          ),
        ),
      );
    });
  });
}
