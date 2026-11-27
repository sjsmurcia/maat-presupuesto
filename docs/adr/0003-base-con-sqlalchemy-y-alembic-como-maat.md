# ADR-3: Base con SQLAlchemy y Alembic, como Maat

- **Estado:** aceptada
- **Fecha:** 2026-11-26
- **Decisiones vigentes que aplica:** la 1 (mismo stack que Maat) y la 24 (varias empresas separadas con RLS) de [`docs/decisiones.md`](../decisiones.md).

## Contexto

- El sistema va a ser el módulo de presupuesto de Maat (decisión 1). Maat trabaja su base con modelos de SQLAlchemy y migraciones de Alembic.
- La base es PostgreSQL: la de cada desarrollador, la del CI y la de Azure (ADR-1). Las tres tienen que quedar exactamente iguales.
- Cada empresa ve solo sus datos, y lo impide la propia base con RLS (decisión 24).
- Las reglas del negocio son funciones puras que no conocen la base (ADR-2).

Se compararon dos opciones:

1. **SQL a mano:** archivos `.sql` numerados y un script corto que los aplica. Es más simple, pero es una forma distinta a la de Maat, y al integrarse habría que rehacerlo.
2. **SQLAlchemy 2.0 y Alembic, con psycopg 3**, como Maat.

## Decisión

Elegimos la opción 2:

- **Los modelos** de SQLAlchemy viven en `backend/db/modelos.py`, en el borde. El dominio (`presupuesto/`) no los importa.
- **Cada cambio a la base** es una revisión de Alembic en `alembic/versions/`, escrita a mano para que se pueda leer, con su `upgrade()` y su `downgrade()`. Una revisión que ya se aplicó no se edita: el cambio va en la siguiente.
- **Las políticas de RLS** van dentro de la revisión con `op.execute`, porque Alembic no tiene una operación propia para eso.
- **La URL de la base** sale de la variable de entorno `DATABASE_URL`, nunca del repo.

## Consecuencias

**Lo que ganamos:**

- Las tablas se pueden llevar a Maat sin traducirlas, y quien sabe trabajar en Maat sabe trabajar aquí.
- `alembic upgrade head` deja igual la base local, la del CI y la de Azure, y `downgrade` la puede devolver.
- Un test compara los modelos con la base migrada: si alguien cambia un modelo sin escribir su revisión, el CI falla.
- La RLS se prueba con un rol que no puede saltársela, así que el test demuestra que una empresa no ve los datos de otra.

**Lo que sacrificamos:**

- **Una capa más:** los modelos de SQLAlchemy y los datos del dominio son cosas distintas, y alguien tiene que traducir de uno al otro (ADR-2).
- **Dos lugares que describen las tablas:** el modelo y la revisión. El test de comparación evita que se separen, pero hay que escribir las dos.
- **Más dependencias:** SQLAlchemy, Alembic y psycopg, que hay que mantener al día.
- **La RLS escrita en SQL** dentro de la revisión: Alembic no la ve, así que la comparación de modelos no la revisa. La cubren los tests de RLS.
