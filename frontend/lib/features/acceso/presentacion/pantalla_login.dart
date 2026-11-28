import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:maat_presupuesto/core/tema/medidas_maat.dart';
import 'package:maat_presupuesto/core/tema/tipografia_maat.dart';
import 'package:maat_presupuesto/core/tema/tokens_maat.dart';
import 'package:maat_presupuesto/features/acceso/aplicacion/login_provider.dart';
import 'package:material_symbols_icons/symbols.dart';

const _anchoTarjeta = 400.0;
const _paddingTarjeta = 32.0;
const _separacion = 16.0;
const _separacionRotulo = 6.0;
const _paddingCampo = EdgeInsets.symmetric(horizontal: 10);
const _esquinas = BorderRadius.all(Radius.circular(MedidasMaat.radio));

/// Entra con correo y contraseña; la empresa se elige después (D24).
class PantallaLogin extends ConsumerStatefulWidget {
  const PantallaLogin({super.key});

  @override
  ConsumerState<PantallaLogin> createState() => _EstadoPantallaLogin();
}

class _EstadoPantallaLogin extends ConsumerState<PantallaLogin> {
  final _correo = TextEditingController();
  final _contrasena = TextEditingController();

  @override
  void dispose() {
    _correo.dispose();
    _contrasena.dispose();
    super.dispose();
  }

  Future<void> _iniciar() async {
    final entro = await ref
        .read(loginProvider.notifier)
        .iniciar(correo: _correo.text, contrasena: _contrasena.text);
    if (!mounted) return;
    if (entro) context.go('/empresa');
  }

  @override
  Widget build(BuildContext context) {
    // Escucharlo lo mantiene vivo mientras espera la respuesta: es autoDispose.
    ref.watch(loginProvider);
    return Scaffold(
      backgroundColor: context.tokens.chrome,
      body: Center(
        child: SingleChildScrollView(
          child: _Tarjeta(
            children: [
              const _Marca(),
              _CampoCorreo(controller: _correo),
              _Campo(
                rotulo: 'CONTRASEÑA',
                child: _CampoContrasena(
                  controller: _contrasena,
                  alEnviar: _iniciar,
                ),
              ),
              _BotonIniciar(alPresionar: _iniciar),
              const _Pie(),
            ],
          ),
        ),
      ),
    );
  }
}

InputDecoration _decoracion(BuildContext context, {Widget? sufijo}) {
  final tokens = context.tokens;
  return InputDecoration(
    isDense: true,
    filled: true,
    fillColor: tokens.surface,
    constraints: const BoxConstraints.tightFor(height: MedidasMaat.campoAcceso),
    contentPadding: _paddingCampo,
    enabledBorder: OutlineInputBorder(
      borderRadius: _esquinas,
      borderSide: BorderSide(color: tokens.borde),
    ),
    focusedBorder: OutlineInputBorder(
      borderRadius: _esquinas,
      borderSide: BorderSide(color: tokens.accion, width: MedidasMaat.marca),
    ),
    suffixIcon: sufijo,
    suffixIconConstraints: const BoxConstraints.tightFor(
      width: MedidasMaat.campoAcceso,
      height: MedidasMaat.campoAcceso,
    ),
  );
}

class _Tarjeta extends StatelessWidget {
  const _Tarjeta({required this.children});

  final List<Widget> children;

  @override
  Widget build(BuildContext context) {
    return Container(
      constraints: const BoxConstraints(maxWidth: _anchoTarjeta),
      padding: const EdgeInsets.all(_paddingTarjeta),
      decoration: BoxDecoration(
        color: context.tokens.surface,
        border: Border.all(color: context.tokens.borde),
        borderRadius: _esquinas,
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.stretch,
        spacing: _separacion,
        children: children,
      ),
    );
  }
}

class _Marca extends StatelessWidget {
  const _Marca();

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      spacing: _separacionRotulo,
      children: [
        const Text('Maat Presupuesto', style: TipografiaMaat.tituloPantalla),
        Text(
          'Presupuesto por cuenta y su ejecución por área.',
          style: TipografiaMaat.celda.copyWith(color: context.tokens.tenue),
        ),
      ],
    );
  }
}

class _Campo extends StatelessWidget {
  const _Campo({required this.rotulo, required this.child});

  final String rotulo;
  final Widget child;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      spacing: _separacionRotulo,
      children: [
        Text(
          rotulo,
          style: TipografiaMaat.encabezado.copyWith(
            color: context.tokens.tenue,
          ),
        ),
        child,
      ],
    );
  }
}

class _CampoCorreo extends StatelessWidget {
  const _CampoCorreo({required this.controller});

  final TextEditingController controller;

  @override
  Widget build(BuildContext context) {
    return _Campo(
      rotulo: 'CORREO ELECTRÓNICO',
      child: TextField(
        controller: controller,
        keyboardType: TextInputType.emailAddress,
        decoration: _decoracion(context),
      ),
    );
  }
}

class _CampoContrasena extends StatefulWidget {
  const _CampoContrasena({required this.controller, required this.alEnviar});

  final TextEditingController controller;
  final AsyncCallback alEnviar;

  @override
  State<_CampoContrasena> createState() => _EstadoCampoContrasena();
}

class _EstadoCampoContrasena extends State<_CampoContrasena> {
  var _estaOculta = true;

  @override
  Widget build(BuildContext context) {
    return TextField(
      controller: widget.controller,
      obscureText: _estaOculta,
      onSubmitted: (_) => unawaited(widget.alEnviar()),
      decoration: _decoracion(
        context,
        sufijo: IconButton(
          padding: EdgeInsets.zero,
          icon: const Icon(Symbols.visibility),
          onPressed: () => setState(() => _estaOculta = !_estaOculta),
        ),
      ),
    );
  }
}

class _BotonIniciar extends StatelessWidget {
  const _BotonIniciar({required this.alPresionar});

  final AsyncCallback alPresionar;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: MedidasMaat.botonAcceso,
      child: FilledButton(
        onPressed: () => unawaited(alPresionar()),
        child: const Text('Iniciar sesión'),
      ),
    );
  }
}

class _Pie extends StatelessWidget {
  const _Pie();

  @override
  Widget build(BuildContext context) {
    return Text(
      '¿No tienes acceso? Pídeselo al administrador de tu firma.',
      style: TipografiaMaat.nota.copyWith(color: context.tokens.tenue),
    );
  }
}
