import 'package:decimal/decimal.dart';

/// Lee un monto que llega de la API.
///
/// El dinero viaja como texto ("185000.00") y se lee con `Decimal`: un
/// `double` pierde centavos, por eso se rechaza en vez de convertirlo.
Decimal montoDesdeJson(Object? valor) {
  if (valor is! String) {
    throw FormatException(
      'El dinero llega como texto con 2 decimales, y llegó $valor',
    );
  }
  return Decimal.parse(valor);
}

/// Escribe un monto en formato hondureño: `1,234.56`, siempre con 2
/// decimales. Un negativo va entre paréntesis, como en los estados
/// contables.
String formatearMonto(Decimal monto) {
  final texto = _conMiles(monto.abs().toStringAsFixed(2));
  return monto < Decimal.zero ? '($texto)' : texto;
}

String _conMiles(String fijo) {
  final partes = fijo.split('.');
  final enteros = partes.first.replaceAllMapped(
    RegExp(r'\B(?=(\d{3})+(?!\d))'),
    (_) => ',',
  );
  return '$enteros.${partes.last}';
}
