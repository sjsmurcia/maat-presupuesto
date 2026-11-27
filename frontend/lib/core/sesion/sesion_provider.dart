import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:maat_presupuesto/core/sesion/sesion.dart';

final sesionProvider = NotifierProvider<SesionNotifier, Sesion?>(
  SesionNotifier.new,
);

/// La sesión de toda la app: la leen la barra y todas las pantallas.
class SesionNotifier extends Notifier<Sesion?> {
  @override
  Sesion? build() => null;

  void iniciar({required String token, required String correo}) {
    state = Sesion(token: token, correo: correo);
  }

  void elegirEmpresa(EmpresaElegida empresa) {
    state = state?.conEmpresa(empresa);
  }

  void cerrar() {
    state = null;
  }
}
