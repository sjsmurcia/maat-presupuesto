import 'package:flutter/material.dart';
import 'package:maat_presupuesto/core/widgets/pantalla_en_construccion.dart';

class PantallaCuentas extends StatelessWidget {
  const PantallaCuentas({super.key});

  @override
  Widget build(BuildContext context) {
    return const PantallaEnConstruccion(
      titulo: 'Catálogo de cuentas',
      artboard: '2 · Catálogo de cuentas',
    );
  }
}
