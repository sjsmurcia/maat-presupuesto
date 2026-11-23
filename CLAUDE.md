# CLAUDE.md — Maat Presupuesto

## Idioma y trato
- Todo en ESPAÑOL, con tuteo: mensajes, commits, PR, comentarios y Jira.
- Cuando jm tiene que **ejecutar algo** (comandos, un PR, la plataforma, pegar código): **un paso por mensaje**, con el comando exacto, lo que tiene que ver al terminar, y esperar su «listo». Las cajas de un formulario (título, descripción) van separadas y literales. Una explicación o una revisión puede ir completa.
- No adelantarse al alcance: una decisión de negocio se pregunta, de a una, con una recomendación. Lo decidido se escribe el mismo día en `docs/decisiones.md` y en Jira (proyecto MP).

## Qué es
Presupuesto por cuenta contable, con su ejecución contra lo real por área. La contabilidad registra una sola línea por gasto, con su centro de costo (CeCo) o de beneficio (CeBe), y las reglas de distribución reparten lo compartido. Es el proyecto final de Ingeniería de Software II y un futuro módulo de Maat (el ERP contable de la firma, que usa el mismo stack). El repo es **PÚBLICO**: ningún nombre ni dato de clientes, empresas o personas; los ejemplos son ficticios.

- Stack: Python 3.12, FastAPI, PostgreSQL, Flutter web (PWA). Hoy solo existe el dominio (`presupuesto/`) con pytest.
- Arquitectura: `practica-6/arquitectura.md` (C4).
- Decisiones vigentes: `docs/decisiones.md`. El detalle y la discusión, en Jira MP-1 y sus comentarios.
- Lo que es de una máquina (rutas, cuentas, tokens) va en `CLAUDE.local.md`, que git ignora.

## Vocabulario
- **Partida** es el asiento contable y nada más. Las filas del presupuesto son **líneas de detalle** de una cuenta.
- El **responsable** es el área que presupuesta una línea de detalle. El CeCo no va en el presupuesto: va en el asiento.
- Las definiciones completas están en `docs/decisiones.md`.

## Reglas de oro
1. **Dinero = `Decimal`, nunca float**, con 2 decimales. La v1 trabaja solo en lempiras. Los pesos, porcentajes y cantidades llevan los decimales que necesiten; un resultado en dinero se lleva a 2 sin perder centavos (`repartir_por_pesos`).
2. **El presupuesto controla, no bloquea**, y lo afecta solo lo contabilizado (el real que se carga).
3. **Se presupuestan cuentas, no centros de costo.** La misma regla de distribución reparte el presupuesto de la cuenta (al aprobarse) y lo real (al cierre); cada área se mide por lo ejecutado contra lo presupuestado, y un gasto compartido que se dispara lo explica su dueño.
4. **Mientras el mes está abierto, lo calculado no se guarda**: la ejecución y el tablero se calculan desde el presupuesto, el real y las reglas. **Al cerrar, se guarda la foto del cierre** (lo distribuido con las reglas de ese día), y esa foto no se modifica: cambiar una regla después no reescribe un mes cerrado.

## Arquitectura (capas limpias, módulo 6)
- `presupuesto/` es el **dominio**: reglas puras, sin imports de FastAPI, SQL, HTTP ni archivos. El centro no sabe que el borde existe.
- Los casos de uso orquestan el dominio; la API, la base y el lector del archivo del real son **adaptadores** del borde y dependen hacia adentro.
- Un puerto o un Repository nace cuando un caso de uso lo necesita. **KISS / YAGNI**: ninguna capa ni patrón sin cliente. Los patrones se descubren refactorizando.

## Clean Code y SOLID (módulos 1 y 3)
- **Nombres**: variables sustantivo, funciones verbo, booleanos como pregunta (`es_`, `tiene_`, `esta_`).
- **Funciones cortas**: 30 líneas como máximo contando el docstring, una sola cosa; validar y calcular van en funciones distintas.
- **Comentarios**: solo el **porqué** vigente, que el código no puede decir. Un docstring de 1 a 3 líneas: qué hace y la decisión no obvia. **No se listan las reglas en el docstring: la especificación son los tests**, que no se desactualizan. La historia («antes…», «se cambió porque…») va al mensaje del commit.
- **OCP**: tablas de políticas (un `dict`) en vez de un `if` que crece con cada caso. **SRP**: una razón para cambiar por función o módulo. **DRY** es de conocimiento: cada regla en UN lugar.

## Testing y TDD (módulo 4)
- **Núcleo funcional, cáscara imperativa**: toda regla es una función pura (recibe datos y devuelve datos, sin sesión, sin `await` y sin «hoy»: la fecha llega por parámetro).
- TDD: rojo → verde → refactor. El test se ve fallar antes de darlo por bueno.
- Nombre `test_<qué>_<cuándo>_<espera>`, AAA visible, un concepto por test, casos borde en `parametrize`, assert del valor exacto.
- Un error también se afirma con su mensaje: `pytest.raises(ValueError, match="...")` con una subcadena estable de la regla. Sin `match=`, el test pasa con cualquier `ValueError`, aunque salga de otra validación.
- Dobles solo en las fronteras (base, red, reloj); la lógica propia no se mockea.

## Git (módulo 2)
- Trunk-based: ramas cortas `paso/<tema>` (o `feature/practica-N` para las prácticas) y **un PR por paso**. `main` está protegida: entra solo por PR con el check `pruebas` en verde, con merge commit.
- Conventional Commits en español: `tipo(ámbito): descripción`, con el ámbito y **un espacio después de los dos puntos** (`feat(distribucion): …`, `test(…)`, `refactor(…)`, `docs(…)`). **Sin** la línea «Co-Authored-By: Claude».
- La plataforma del curso exige 25 commits o más en 5 días distintos o más.

## Cómo se trabaja aquí
- **Las funciones puras las escribe jm.** Claude escribe la firma, el docstring corto y los tests en rojo; verifica en una copia aparte que hay una solución que pasa y que los tests se pueden poner rojos, y después guía a jm.
- Lo que no es regla (base, API, pantallas, despliegue) lo prepara Claude y jm lo revisa y lo entra por PR.

## Comandos
```
python -m pytest -q
```
