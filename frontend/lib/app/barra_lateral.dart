import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:maat_presupuesto/app/destinos.dart';
import 'package:maat_presupuesto/core/tema/medidas_maat.dart';
import 'package:maat_presupuesto/core/tema/tipografia_maat.dart';
import 'package:maat_presupuesto/core/tema/tokens_maat.dart';

/// La barra lateral de 236px: la marca y los destinos agrupados, con el
/// activo marcado. Copia el artboard «Componente · Barra lateral».
class BarraLateral extends StatelessWidget {
  const BarraLateral({required this.activo, super.key});

  final Destino? activo;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: MedidasMaat.barraExpandida,
      child: ListView(
        padding: const EdgeInsets.symmetric(horizontal: 12),
        children: [
          const _Marca(),
          for (final grupo in GrupoDeMenu.values)
            _Grupo(grupo: grupo, activo: activo),
        ],
      ),
    );
  }
}

class _Marca extends StatelessWidget {
  const _Marca();

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: 52,
      child: Row(
        spacing: 10,
        children: [
          const SizedBox(width: 6),
          const Text(
            'Maat',
            style: TextStyle(fontSize: 15, fontWeight: FontWeight.w600),
          ),
          Flexible(
            child: Text(
              'Presupuesto',
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
              style: TextStyle(color: context.tokens.tenue),
            ),
          ),
        ],
      ),
    );
  }
}

class _Grupo extends StatelessWidget {
  const _Grupo({required this.grupo, required this.activo});

  final GrupoDeMenu grupo;
  final Destino? activo;

  @override
  Widget build(BuildContext context) {
    final destinos = Destino.values.where((d) => d.grupo == grupo);
    return Padding(
      padding: const EdgeInsets.only(bottom: MedidasMaat.separacionGrupos),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(10, 0, 10, 6),
            child: Text(
              grupo.titulo.toUpperCase(),
              style: TipografiaMaat.encabezado.copyWith(
                color: context.tokens.tenue,
              ),
            ),
          ),
          for (final destino in destinos)
            _Item(destino: destino, esActivo: destino == activo),
        ],
      ),
    );
  }
}

class _Item extends StatelessWidget {
  const _Item({required this.destino, required this.esActivo});

  final Destino destino;
  final bool esActivo;

  @override
  Widget build(BuildContext context) {
    final tokens = context.tokens;
    return Semantics(
      selected: esActivo,
      button: true,
      child: InkWell(
        onTap: () => context.go(destino.ruta),
        child: Container(
          height: MedidasMaat.itemBarraAlto,
          decoration: BoxDecoration(
            color: esActivo ? tokens.surface : null,
            borderRadius: BorderRadius.circular(MedidasMaat.radio),
          ),
          child: Row(
            spacing: 8,
            children: [
              // La marca de 2px al borde izquierdo dice cuál está activo.
              Container(
                width: MedidasMaat.marca,
                color: esActivo ? tokens.accion : null,
              ),
              Icon(destino.icono, size: MedidasMaat.iconoBarra),
              // Un título largo se corta con «…» en vez de desbordar.
              Expanded(
                child: Text(
                  destino.titulo,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: TextStyle(
                    fontSize: 13,
                    fontWeight: esActivo ? FontWeight.w500 : FontWeight.w400,
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
