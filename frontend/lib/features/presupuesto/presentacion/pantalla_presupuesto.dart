import 'package:flutter/material.dart';
import 'package:maat_presupuesto/core/widgets/pantalla_en_construccion.dart';

class PantallaPresupuesto extends StatelessWidget {
  const PantallaPresupuesto({super.key});

  @override
  Widget build(BuildContext context) {
    return const PantallaEnConstruccion(
      titulo: 'Presupuesto',
      artboard: '4 · Presupuesto en borrador',
    );
  }
}
