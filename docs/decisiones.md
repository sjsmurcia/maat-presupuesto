# Decisiones vigentes

Lo decidido y su porqué, en una línea cada una. La discusión completa está en Jira (proyecto MP). Si una decisión cambia, se reescribe aquí y el motivo va al commit.

## Producto
1. **Sistema independiente**, con repo público. A futuro será el módulo de presupuesto de Maat (el ERP contable de la firma) y leerá lo real del libro diario; por eso usa el mismo stack.
2. **Lo real entra por archivo** (Excel/CSV), para servir con cualquier sistema contable.
3. **La v1 trabaja solo en lempiras.** El archivo del real llega ya convertido, como queda en el libro.

## Dinero
4. **Dinero en `Decimal` con 2 decimales.** Los pesos, porcentajes y cantidades llevan los que necesiten.
5. **Repartir no pierde ni inventa un centavo**: se trunca y los centavos sobrantes van por mayor residuo.

## Centros y reglas
6. **Tres tipos de CeCo**: específico (el gasto se queda ahí), genérico (se reparte con una regla) e institucional (por política no se reparte). Los ingresos van a CeBes.
7. **Un genérico sin regla queda centralizado**, para que un CeCo nuevo no trabe el cierre; el tablero lo avisa. Un específico o un institucional con regla es un error de catálogo.
8. **Una regla tiene dos tramos**: primero los montos fijos y después el resto, por porcentaje (suma 100) o por inductor. Si un CeCo está en los dos tramos, sus partes se suman.
9. **Con fijos, un monto que no alcanza para cubrirlos se rechaza** (por ejemplo, una nota de crédito). En la v1 ese caso se reparte a mano.

## Control y cierre
10. **El presupuesto controla, no bloquea**, y lo afecta solo lo contabilizado. Los compromisos o reservas (órdenes de compra) quedan fuera de la v1.
11. **El control va contra el CeCo responsable, antes de distribuir**: la sobreejecución de un gasto compartido la explica el dueño del genérico. La distribución es costeo (cuánto le cuesta cada área) y no modifica el presupuesto.
12. **Las reglas se aplican al cierre del mes.** Mientras el mes está abierto, todo se recalcula; **al cerrar se guarda la foto del cierre**, que ya no se modifica.

## Proyectos
13. **Costos de proyecto en nivel 1**: solo los costos directos marcados con el proyecto. Recibir gastos compartidos por regla queda para después.
