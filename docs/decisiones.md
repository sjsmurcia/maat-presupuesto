# Decisiones vigentes

Lo decidido y su porqué, en una línea cada una. La discusión completa está en Jira (proyecto MP). Si una decisión cambia, se reescribe aquí y el motivo va al commit.

## Vocabulario
- **Partida**: el asiento contable. No se usa para nada más.
- **Línea de detalle**: cada fila del presupuesto dentro de una cuenta.
- **Responsable**: el área que presupuesta una línea de detalle y responde por ella.
- **CeCo / CeBe**: centro de costo (gasto) y centro de beneficio (ingreso). Son una dimensión del asiento, no cuentas.
- **Fotografía**: los porcentajes de una regla, fijos durante su vigencia.

## Producto
1. **Sistema independiente**, con repo público. A futuro será el módulo de presupuesto de Maat (el ERP contable de la firma) y leerá lo real del libro diario; por eso usa el mismo stack.
2. **Lo real entra por archivo** (Excel/CSV), para servir con cualquier sistema contable.
3. **La v1 trabaja solo en lempiras.** El archivo del real llega ya convertido, como queda en el libro.

## Dinero
4. **Dinero en `Decimal` con 2 decimales.** Los pesos, porcentajes y cantidades llevan los que necesiten.
5. **Repartir no pierde ni inventa un centavo**: se trunca y los centavos sobrantes van por mayor residuo.

## Presupuesto
6. **Se presupuestan cuentas contables, no centros de costo.** La fila es cuenta × línea de detalle × responsable × mes. No lleva CeCo.
7. **Los meses se agrupan en períodos** (por ejemplo, cuatrimestres); el tablero muestra mes, período y acumulado.

## Centros
8. **Los centros son un árbol aparte del catálogo de cuentas.** Cada centro apunta a su superior, todos pueden recibir movimiento y la unidad de negocio es el nivel superior del árbol. Los totales suben por el árbol.
9. **Cada CeCo pertenece a un área responsable.** En un genérico, esa área es el dueño del gasto compartido.
10. **Tres tipos de CeCo**: específico (el gasto se queda ahí), genérico (se reparte con una regla) e institucional (por política no se reparte). Los ingresos van a CeBes.
11. **Un gasto directo va al CeCo propio del área**, sin genérico y sin regla.
12. **Un genérico sin regla queda centralizado**, para que un CeCo nuevo no trabe el cierre; el tablero lo avisa. Un específico o un institucional con regla es un error de catálogo.

## Reglas de distribución
13. **Una regla siempre reparte el 100 %.** Tiene dos tramos: primero los montos fijos y después el resto, por porcentaje (suma 100) o por inductor. Si un CeCo está en los dos tramos, sus partes se suman.
14. **Un gasto con varias formas de reparto es una sola regla con tramos**, no varias reglas.
15. **La misma regla se aplica dos veces**: al presupuesto de la cuenta cuando se aprueba y a lo real en cada cierre.
16. **La fotografía vale por ejercicio y tiene fecha de vigencia**, para poder cambiarla por período sin tocar lo ya cerrado.
17. **Con fijos, un monto que no alcanza para cubrirlos se rechaza** (por ejemplo, una nota de crédito). En la v1 ese caso se reparte a mano.

## Control y cierre
18. **El presupuesto controla, no bloquea**, y lo afecta solo lo contabilizado. Los compromisos o reservas (órdenes de compra) quedan fuera de la v1.
19. **Cada área se mide por lo ejecutado contra lo presupuestado**, por cuenta, del mes y acumulado. En un gasto directo es lo que cayó en sus CeCos contra lo que presupuestó en la cuenta; en uno compartido, su parte de lo real contra su parte del presupuesto, las dos por la misma regla.
20. **Si un gasto compartido se dispara, lo explica el dueño del genérico.**
21. **Las reglas se aplican al cierre del mes.** Mientras el mes está abierto, todo se recalcula; **al cerrar se guarda la foto del cierre**, que ya no se modifica.

## Alcance
22. **Entra seguro**: presupuesto por cuenta, árbol de centros, reglas, cierre y tablero por área.
23. **Entra solo si hay tiempo**: resultado por carrera (CeBe) y proyectos. Si entran proyectos, sus costos son solo los directos marcados con el proyecto.
