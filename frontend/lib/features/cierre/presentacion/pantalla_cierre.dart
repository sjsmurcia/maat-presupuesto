import 'package:flutter/material.dart';
import 'package:maat_presupuesto/core/widgets/pantalla_en_construccion.dart';

class PantallaCierre extends StatelessWidget {
  const PantallaCierre({super.key});

  @override
  Widget build(BuildContext context) {
    return const PantallaEnConstruccion(
      titulo: 'Cierre del mes',
      artboard: '7 · Revisión antes de cerrar',
    );
  }
}
