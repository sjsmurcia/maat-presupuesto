import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:maat_presupuesto/core/tema/medidas_maat.dart';
import 'package:maat_presupuesto/core/tema/tipografia_maat.dart';
import 'package:maat_presupuesto/core/tema/tokens_maat.dart';

/// Lo que se ve mientras una pantalla no está hecha. Se borra cuando la
/// última pantalla la reemplace.
class PantallaEnConstruccion extends StatelessWidget {
  const PantallaEnConstruccion({
    required this.titulo,
    required this.artboard,
    this.siguiente,
    super.key,
  });

  final String titulo;

  /// El nombre del artboard del lienzo de diseño que la pantalla copia.
  final String artboard;

  /// Una ruta para seguir navegando antes de que la pantalla exista.
  final ({String texto, String ruta})? siguiente;

  @override
  Widget build(BuildContext context) {
    final paso = siguiente;
    return Padding(
      padding: MedidasMaat.cabeceraPadding,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        spacing: MedidasMaat.cabeceraGap,
        children: [
          Text(titulo, style: TipografiaMaat.tituloPantalla),
          Text(
            'En construcción. Se arma copiando el artboard «$artboard» del '
            'lienzo y su sección del handoff.',
            style: TipografiaMaat.celda.copyWith(color: context.tokens.tenue),
          ),
          if (paso != null)
            FilledButton(
              onPressed: () => context.go(paso.ruta),
              child: Text(paso.texto),
            ),
        ],
      ),
    );
  }
}
