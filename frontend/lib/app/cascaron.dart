import 'package:flutter/material.dart';
import 'package:maat_presupuesto/app/barra_lateral.dart';
import 'package:maat_presupuesto/app/destinos.dart';
import 'package:maat_presupuesto/core/tema/tokens_maat.dart';

/// El marco de las pantallas de trabajo: la barra lateral a la izquierda y
/// la pantalla del destino a la derecha.
class Cascaron extends StatelessWidget {
  const Cascaron({required this.ruta, required this.pantalla, super.key});

  final String ruta;
  final Widget pantalla;

  @override
  Widget build(BuildContext context) {
    final tokens = context.tokens;
    return Scaffold(
      backgroundColor: tokens.chrome,
      body: Row(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          BarraLateral(activo: Destino.deRuta(ruta)),
          VerticalDivider(width: 1, color: tokens.borde),
          Expanded(
            child: ColoredBox(color: tokens.surface, child: pantalla),
          ),
        ],
      ),
    );
  }
}
