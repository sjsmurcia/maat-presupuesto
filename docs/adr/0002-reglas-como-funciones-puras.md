# ADR-2: Las reglas de negocio son funciones puras, separadas de la API y de la base

- **Estado:** aceptada
- **Fecha:** 2026-11-22
- **Dónde se explica también:** el nivel 2 del C4, en [`practica-6/arquitectura.md`](../../practica-6/arquitectura.md), y la sección «Arquitectura» del [`CLAUDE.md`](../../CLAUDE.md).

## Contexto

- Las reglas del presupuesto mueven dinero y no pueden fallar:
  - repartir sin perder ni inventar un centavo (decisión 5);
  - distribuir con montos fijos y pedazos (decisiones 13 y 43);
  - decidir si un gasto va directo, se distribuye o queda centralizado (decisiones 10 a 12);
  - leer la ejecución contra los umbrales (decisión 47).
- La misma regla se aplica dos veces: al presupuesto cuando se aprueba y a lo real en cada cierre (decisión 15).
- El sistema va a ser el módulo de presupuesto de Maat, con el mismo stack (decisión 1). Las reglas se tienen que poder llevar allá sin reescribirlas.
- Las reglas se escriben con TDD, y las pruebas tienen que correr rápido en cada pull request, sin levantar una base ni un servidor.

## Decisión

- La carpeta `presupuesto/` es el **dominio**. Cada regla es una **función pura**: recibe datos y devuelve datos.
- El dominio **no importa** FastAPI, SQL, HTTP ni archivos. Tampoco usa una sesión ni la fecha de «hoy»: la fecha le llega por parámetro.
- Los **casos de uso** orquestan el dominio. La API, la base y el lector del archivo del real son **adaptadores del borde**, y dependen hacia adentro: el dominio no sabe que existen.
- Un puerto o un repository se crea solo cuando un caso de uso lo necesita, y no antes.

## Consecuencias

**Lo que ganamos:**

- Las reglas se prueban con pytest en milisegundos, sin mocks: no hay nada que simular, porque no tocan la base, la red ni el reloj.
- La misma función sirve en todos los lugares que la necesitan. Por ejemplo, `validar_regla` corre al guardar una regla y otra vez al distribuir, así que la regla vive en un solo lugar.
- Cambiar de framework o de base no toca las reglas, y llevarlas a Maat es copiar la carpeta.
- Las pantallas no repiten reglas: lo que necesitan lo calcula la API con el dominio.

**Lo que sacrificamos:**

- **Una capa más:** alguien tiene que traducir las filas de la base a los datos del dominio y de vuelta.
- **Disciplina:** hay que resistir la tentación de poner una regla «rápida» en la API, en una consulta SQL o en una pantalla de Flutter.
- **Cálculo en Python y no en la base:** mientras el mes está abierto, la ejecución se calcula cada vez desde el presupuesto, lo real y las reglas (decisión 21). Con muchos datos eso puede volverse lento, y al cerrar el mes se guarda la foto del cierre.
