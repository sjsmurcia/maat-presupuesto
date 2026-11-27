/// La respuesta de ejemplo del login mientras no hay API, con un usuario
/// ficticio. Responde lo mismo a cualquier correo y contraseña.
const ejemplosAcceso = <String, Object?>{
  '/auth/sesion': {
    'token': 'tk-demo',
    'usuario': {'correo': 'analista@ejemplo.edu'},
  },
};
