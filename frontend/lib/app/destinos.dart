import 'package:flutter/widgets.dart';
import 'package:material_symbols_icons/symbols.dart';

/// Los grupos de la barra lateral, en el orden en que aparecen.
enum GrupoDeMenu {
  control('Control'),
  cierre('Cierre'),
  catalogos('Catálogos');

  const GrupoDeMenu(this.titulo);

  final String titulo;
}

/// Las pantallas a las que se llega desde la barra lateral.
///
/// Es la única tabla de destinos: el router y la barra lateral la leen, así
/// que agregar una pantalla es agregar una fila aquí y no tocar un `if`.
enum Destino {
  tablero(
    'Tablero por área',
    Symbols.monitoring,
    '/tablero',
    GrupoDeMenu.control,
  ),
  presupuesto(
    'Presupuesto',
    Symbols.savings,
    '/presupuesto',
    GrupoDeMenu.control,
  ),
  real('Carga del real', Symbols.upload_file, '/real', GrupoDeMenu.cierre),
  cierre(
    'Cierre del mes',
    Symbols.event_available,
    '/cierre',
    GrupoDeMenu.cierre,
  ),
  cuentas('Cuentas', Symbols.account_tree, '/cuentas', GrupoDeMenu.catalogos),
  centros('Centros y áreas', Symbols.lan, '/centros', GrupoDeMenu.catalogos),
  reglas(
    'Reglas de distribución',
    Symbols.call_split,
    '/reglas',
    GrupoDeMenu.catalogos,
  );

  const Destino(this.titulo, this.icono, this.ruta, this.grupo);

  final String titulo;
  final IconData icono;
  final String ruta;
  final GrupoDeMenu grupo;

  /// El destino que corresponde a una ruta, o null si la ruta no es de la
  /// barra lateral (el login, por ejemplo).
  static Destino? deRuta(String ruta) {
    for (final destino in values) {
      if (ruta.startsWith(destino.ruta)) return destino;
    }
    return null;
  }
}
