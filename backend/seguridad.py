"""Las contraseñas con Argon2id, como en Maat (decisión 51): sin base de datos ni HTTP."""

from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher

# Los parámetros de Maat (RFC 9106); los tests los bajan para no pagar 64 MiB por hash.
ARGON2_TIEMPO = 3
ARGON2_MEMORIA_KIB = 65536
ARGON2_PARALELISMO = 4


def crear_hasher(
    tiempo: int = ARGON2_TIEMPO,
    memoria_kib: int = ARGON2_MEMORIA_KIB,
    paralelismo: int = ARGON2_PARALELISMO,
) -> PasswordHash:
    hasher = Argon2Hasher(time_cost=tiempo, memory_cost=memoria_kib, parallelism=paralelismo)
    return PasswordHash((hasher,))


def hashear_password(hasher: PasswordHash, password: str) -> str:
    return hasher.hash(password)


def verificar_password(
    hasher: PasswordHash, password: str, hash_almacenado: str
) -> tuple[bool, str | None]:
    """(es válida, hash nuevo si los parámetros subieron y conviene volver a guardarlo)."""
    return hasher.verify_and_update(password, hash_almacenado)
