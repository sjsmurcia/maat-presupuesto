import 'package:flutter/material.dart';
import 'package:maat_presupuesto/core/widgets/pantalla_en_construccion.dart';

class PantallaLogin extends StatelessWidget {
  const PantallaLogin({super.key});

  @override
  Widget build(BuildContext context) {
    return const PantallaEnConstruccion(
      titulo: 'Iniciar sesión',
      artboard: '1 · Login',
      siguiente: (texto: 'Entrar con el usuario de prueba', ruta: '/empresa'),
    );
  }
}
