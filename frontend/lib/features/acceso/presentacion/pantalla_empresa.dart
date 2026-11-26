import 'package:flutter/material.dart';
import 'package:maat_presupuesto/core/widgets/pantalla_en_construccion.dart';

class PantallaEmpresa extends StatelessWidget {
  const PantallaEmpresa({super.key});

  @override
  Widget build(BuildContext context) {
    return const PantallaEnConstruccion(
      titulo: 'Elige la empresa',
      artboard: '1 · Elegir empresa',
      siguiente: (texto: 'Entrar a la empresa de ejemplo', ruta: '/tablero'),
    );
  }
}
