"""Semilla de la demo: la Empresa Demo con su catálogo y dos usuarios ficticios (decisión 53).

Uso, desde la raíz del repo y con DATABASE_URL:  python -m scripts.semilla_demo
Fuera de desarrollo (MP_ENTORNO distinto de dev) exige MP_SEMILLA_PERMITIR igual al
entorno, y la contraseña de los usuarios sale solo de MP_SEMILLA_PASSWORD. Se puede
correr dos veces: lo que ya existe no se toca, tampoco la contraseña de un usuario.
"""

import os
import sys
import uuid
from collections.abc import Mapping, Sequence

from pwdlib import PasswordHash
from sqlalchemy import Connection, create_engine, text

from backend.db.conexion import leer_url_de_la_base
from backend.seguridad import crear_hasher, hashear_password

# Pública a propósito: solo vale en desarrollo y fuera de desarrollo se rechaza.
PASSWORD_DEFAULT = "DemoPresupuesto2026"  # noqa: S105
VARIABLE_PASSWORD = "MP_SEMILLA_PASSWORD"  # noqa: S105 - el nombre de la variable
LARGO_MIN_FUERA_DE_DEV = 16
SALIDA_ABORTADA = 2

EMPRESA_DEMO = uuid.UUID("11111111-1111-1111-1111-111111111111")
ADM, COM, TI, CON, VTA = (uuid.UUID(f"a0000000-0000-0000-0000-00000000000{n}") for n in "12345")
AREAS = (
    (ADM, "ADM", "Administración", None), (COM, "COM", "Comercial", None),
    (TI, "TI", "Tecnología", None), (CON, "CON", "Contabilidad", ADM), (VTA, "VTA", "Ventas", COM),
)
# Primero las de grupo, porque las de detalle apuntan a ellas.
CUENTAS = (
    ("1", "Activo", None, "ACTIVO", False, True), ("2", "Pasivo", None, "PASIVO", False, True),
    ("4", "Ingresos", None, "INGRESO", False, True), ("5", "Gastos", None, "GASTO", False, True),
    ("6", "Costos", None, "COSTO", False, True), ("1101", "Bancos", "1", "ACTIVO", True, True),
    ("2101", "Proveedores", "2", "PASIVO", True, True),
    ("4101", "Ventas de contado", "4", "INGRESO", True, True),
    ("5101", "Sueldos y salarios", "5", "GASTO", True, True),
    ("5201", "Energía eléctrica", "5", "GASTO", True, True),
    ("5202", "Vigilancia", "5", "GASTO", True, True), ("5203", "Alquiler", "5", "GASTO", True, True),
    ("5204", "Servicios en la nube", "5", "GASTO", True, True),
    ("5299", "Papelería (en desuso)", "5", "GASTO", True, False),
    ("6101", "Costo de ventas", "6", "COSTO", True, True),
)
CENTROS = (
    ("CC-1000", "Administración", None, "ESPECIFICO", ADM),
    ("CC-1100", "Contabilidad", "CC-1000", "ESPECIFICO", CON),
    ("CC-1600", "Tecnología", None, "ESPECIFICO", TI),
    ("CC-1910", "Servicios Generales", None, "GENERICO", ADM),
    ("CC-1920", "Nube compartida", None, "GENERICO", TI),
    ("CC-1990", "Gerencia general", None, "INSTITUCIONAL", ADM),
    ("CB-0100", "Ventas", None, "CEBE", VTA),
)
# (email, rol, área que ve): sin área, el acceso ve todas (decisión 52).
USUARIOS = (
    ("analista@ejemplo.edu", "analista", None),
    ("responsable@ejemplo.edu", "responsable", TI),
)
SQL_EMPRESA = "INSERT INTO empresas (id, nombre) VALUES (:e, 'Empresa Demo') ON CONFLICT DO NOTHING"
SQL_AREAS = (
    "INSERT INTO areas (id, empresa_id, codigo, nombre, area_superior_id)"
    " VALUES (:id, :e, :c, :n, :s) ON CONFLICT DO NOTHING"
)
SQL_CUENTAS = (
    "INSERT INTO cuentas (empresa_id, codigo, nombre, codigo_superior, naturaleza, es_detalle,"
    " activa) VALUES (:e, :c, :n, :s, :nat, :d, :a) ON CONFLICT DO NOTHING"
)
SQL_CENTROS = (
    "INSERT INTO centros (empresa_id, codigo, nombre, codigo_superior, tipo, area_id)"
    " VALUES (:e, :c, :n, :s, :t, :area) ON CONFLICT DO NOTHING"
)


class SemillaAbortada(Exception):
    """La semilla no corre: el motivo se imprime y se sale con código 2."""


def verificar_entorno(entorno: str, variables: Mapping[str, str]) -> None:
    """Fuera de desarrollo pide permiso explícito: nadie exporta esa variable sin querer."""
    if entorno != "dev" and variables.get("MP_SEMILLA_PERMITIR", "") != entorno:
        raise SemillaAbortada(
            f"la semilla solo corre en dev, o con MP_SEMILLA_PERMITIR={entorno} explícito"
        )


def password_de_semilla(entorno: str, argv: Sequence[str], variables: Mapping[str, str]) -> str:
    """En dev, el argumento o la del repo; fuera de dev, solo la variable, larga y propia."""
    if entorno == "dev":
        return argv[1] if len(argv) > 1 else PASSWORD_DEFAULT
    if len(argv) > 1:
        raise SemillaAbortada(
            f"fuera de dev la contraseña no va por la línea de comandos: va en {VARIABLE_PASSWORD}"
        )
    password = variables.get(VARIABLE_PASSWORD, "")
    if not password:
        raise SemillaAbortada(f"fuera de dev la contraseña sale de {VARIABLE_PASSWORD}")
    if password == PASSWORD_DEFAULT:
        raise SemillaAbortada(f"{VARIABLE_PASSWORD} es la contraseña de dev que está en el repo")
    if len(password) < LARGO_MIN_FUERA_DE_DEV:
        raise SemillaAbortada(
            f"{VARIABLE_PASSWORD} tiene {len(password)} caracteres y fuera de dev pide"
            f" {LARGO_MIN_FUERA_DE_DEV} o más"
        )
    return password


def sembrar(conexion: Connection, password: str, hasher: PasswordHash | None = None) -> None:
    """La empresa, su catálogo y los usuarios; lo que ya existe se deja como está."""
    _sembrar_empresa(conexion)
    hasher = hasher or crear_hasher()
    for email, rol, area in USUARIOS:
        usuario_id = _asegurar_usuario(conexion, hasher, email, password)
        _asegurar_acceso(conexion, usuario_id, rol, area)


def _sembrar_empresa(conexion: Connection) -> None:
    # Con FORCE ROW LEVEL SECURITY también el dueño de las tablas dice su empresa.
    e = {"e": EMPRESA_DEMO}
    conexion.execute(text("SELECT set_config('app.empresa_id', CAST(:e AS text), true)"), e)
    conexion.execute(text(SQL_EMPRESA), e)
    conexion.execute(
        text(SQL_AREAS), [{**e, "id": i, "c": c, "n": n, "s": s} for i, c, n, s in AREAS]
    )
    conexion.execute(
        text(SQL_CUENTAS),
        [{**e, "c": c, "n": n, "s": s, "nat": nat, "d": d, "a": a} for c, n, s, nat, d, a in CUENTAS],
    )
    conexion.execute(
        text(SQL_CENTROS),
        [{**e, "c": c, "n": n, "s": s, "t": t, "area": area} for c, n, s, t, area in CENTROS],
    )


def _asegurar_usuario(
    conexion: Connection, hasher: PasswordHash, email: str, password: str
) -> uuid.UUID:
    existente = conexion.scalar(text("SELECT id FROM usuarios WHERE email = :m"), {"m": email})
    if existente is not None:
        return existente
    return conexion.scalar(
        text("INSERT INTO usuarios (email, hash_password) VALUES (:m, :h) RETURNING id"),
        {"m": email, "h": hashear_password(hasher, password)},
    )


def _asegurar_acceso(
    conexion: Connection, usuario_id: uuid.UUID, rol: str, area: uuid.UUID | None
) -> None:
    datos = {"u": usuario_id, "e": EMPRESA_DEMO, "rol": rol, "area": area}
    conexion.execute(
        text(
            "INSERT INTO accesos (usuario_id, empresa_id, rol_id) SELECT :u, :e, id FROM roles"
            " WHERE codigo = :rol ON CONFLICT (usuario_id, empresa_id) DO NOTHING"
        ),
        datos,
    )
    if area is not None:
        conexion.execute(
            text(
                "INSERT INTO accesos_areas (acceso_id, empresa_id, area_id) SELECT id, :e, :area"
                " FROM accesos WHERE usuario_id = :u AND empresa_id = :e"
                " ON CONFLICT (acceso_id, area_id) DO NOTHING"
            ),
            datos,
        )


def sembrar_en_la_base(url: str, password: str) -> None:
    motor = create_engine(url)
    with motor.begin() as conexion:
        sembrar(conexion, password)
    motor.dispose()


def main(argv: Sequence[str] | None = None, variables: Mapping[str, str] | None = None) -> None:
    argv = sys.argv if argv is None else argv
    variables = os.environ if variables is None else variables
    entorno = variables.get("MP_ENTORNO", "dev")
    try:
        verificar_entorno(entorno, variables)
        password = password_de_semilla(entorno, argv, variables)
    except SemillaAbortada as error:
        print(f"ABORTADO: {error}")
        sys.exit(SALIDA_ABORTADA)
    sembrar_en_la_base(leer_url_de_la_base(variables), password)
    usuarios = ", ".join(email for email, _, _ in USUARIOS)
    print(f"Semilla creada: Empresa Demo {EMPRESA_DEMO} con {usuarios}")
    print("(la contraseña no se imprime)")


if __name__ == "__main__":
    main()
