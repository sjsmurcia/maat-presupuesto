import 'package:flutter/material.dart';
import 'package:maat_presupuesto/core/widgets/pantalla_en_construccion.dart';

class PantallaReglas extends StatelessWidget {
  const PantallaReglas({super.key});

  @override
  Widget build(BuildContext context) {
    return const PantallaEnConstruccion(
      titulo: 'Reglas de distribución',
      artboard: '5 · Regla de un gasto: fijos y pedazos',
    );
  }
}
