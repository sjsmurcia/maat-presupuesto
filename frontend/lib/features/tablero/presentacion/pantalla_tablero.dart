import 'package:flutter/material.dart';
import 'package:maat_presupuesto/core/widgets/pantalla_en_construccion.dart';

class PantallaTablero extends StatelessWidget {
  const PantallaTablero({super.key});

  @override
  Widget build(BuildContext context) {
    return const PantallaEnConstruccion(
      titulo: 'Tablero por área',
      artboard: '8 · Tablero por área',
    );
  }
}
