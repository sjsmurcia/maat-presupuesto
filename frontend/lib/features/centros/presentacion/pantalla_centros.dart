import 'package:flutter/material.dart';
import 'package:maat_presupuesto/core/widgets/pantalla_en_construccion.dart';

class PantallaCentros extends StatelessWidget {
  const PantallaCentros({super.key});

  @override
  Widget build(BuildContext context) {
    return const PantallaEnConstruccion(
      titulo: 'Centros y áreas',
      artboard: '3 · Árbol de centros',
    );
  }
}
