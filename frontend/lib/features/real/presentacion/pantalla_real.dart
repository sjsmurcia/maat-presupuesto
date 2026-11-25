import 'package:flutter/material.dart';
import 'package:maat_presupuesto/core/widgets/pantalla_en_construccion.dart';

class PantallaReal extends StatelessWidget {
  const PantallaReal({super.key});

  @override
  Widget build(BuildContext context) {
    return const PantallaEnConstruccion(
      titulo: 'Carga del real',
      artboard: '6 · Carga del real',
    );
  }
}
