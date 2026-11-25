import 'package:flutter/widgets.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:maat_presupuesto/app/cascaron.dart';
import 'package:maat_presupuesto/app/destinos.dart';
import 'package:maat_presupuesto/features/acceso/presentacion/pantalla_empresa.dart';
import 'package:maat_presupuesto/features/acceso/presentacion/pantalla_login.dart';
import 'package:maat_presupuesto/features/centros/presentacion/pantalla_centros.dart';
import 'package:maat_presupuesto/features/cierre/presentacion/pantalla_cierre.dart';
import 'package:maat_presupuesto/features/cuentas/presentacion/pantalla_cuentas.dart';
import 'package:maat_presupuesto/features/presupuesto/presentacion/pantalla_presupuesto.dart';
import 'package:maat_presupuesto/features/real/presentacion/pantalla_real.dart';
import 'package:maat_presupuesto/features/reglas/presentacion/pantalla_reglas.dart';
import 'package:maat_presupuesto/features/tablero/presentacion/pantalla_tablero.dart';

/// La pantalla de cada destino de la barra lateral.
const _pantallas = <Destino, Widget>{
  Destino.tablero: PantallaTablero(),
  Destino.presupuesto: PantallaPresupuesto(),
  Destino.real: PantallaReal(),
  Destino.cierre: PantallaCierre(),
  Destino.cuentas: PantallaCuentas(),
  Destino.centros: PantallaCentros(),
  Destino.reglas: PantallaReglas(),
};

final routerProvider = Provider<GoRouter>((ref) => crearRouter());

/// El login y la elección de empresa van solos; las demás pantallas van
/// dentro del cascarón, con la barra lateral.
GoRouter crearRouter({String inicio = '/login'}) {
  return GoRouter(
    initialLocation: inicio,
    routes: [
      GoRoute(path: '/login', builder: (_, _) => const PantallaLogin()),
      GoRoute(path: '/empresa', builder: (_, _) => const PantallaEmpresa()),
      ShellRoute(
        builder: (_, estado, pantalla) =>
            Cascaron(ruta: estado.uri.path, pantalla: pantalla),
        routes: [
          for (final destino in Destino.values)
            GoRoute(
              path: destino.ruta,
              builder: (_, _) => _pantallas[destino]!,
            ),
        ],
      ),
    ],
  );
}
