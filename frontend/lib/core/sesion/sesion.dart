/// La empresa en la que se trabaja, tal como la manda `GET /empresas`. Su
/// `id` va en cada ruta `/empresas/{id}/…`, y la base (RLS) impide ver otra.
class EmpresaElegida {
  const EmpresaElegida({
    required this.id,
    required this.nombre,
    required this.permisos,
    required this.areas,
    required this.ejercicioActual,
    required this.mesAbierto,
    required this.estadoPresupuesto,
  });

  final String id;
  final String nombre;
  final Set<String> permisos;

  /// Las áreas que el usuario ve; null quiere decir todas.
  final List<String>? areas;
  final int ejercicioActual;

  /// El mes abierto como `AAAA-MM`, o null si no hay ninguno.
  final String? mesAbierto;
  final String? estadoPresupuesto;

  /// La pantalla pregunta por el permiso, nunca por el nombre del rol.
  bool tienePermiso(String codigo) => permisos.contains(codigo);
}

/// Quién entró y en qué empresa trabaja. El token vive solo en memoria: al
/// recargar la página se vuelve a iniciar sesión.
class Sesion {
  const Sesion({required this.token, required this.correo, this.empresa});

  final String token;
  final String correo;
  final EmpresaElegida? empresa;

  Sesion conEmpresa(EmpresaElegida empresa) =>
      Sesion(token: token, correo: correo, empresa: empresa);
}
