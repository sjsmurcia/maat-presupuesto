# Decisiones vigentes

Lo decidido y su porqué, en una línea cada una. La discusión completa está en Jira (proyecto MP). Si una decisión cambia, se reescribe aquí y el motivo va al commit.

## Vocabulario
- **Partida**: el asiento contable. No se usa para nada más.
- **Línea de detalle**: cada fila del presupuesto dentro de una cuenta.
- **Responsable**: el área que presupuesta una línea de detalle y responde por ella.
- **CeCo / CeBe**: centro de costo (gasto) y centro de beneficio (ingreso). Son una dimensión del asiento, no cuentas.
- **Fotografía**: los porcentajes de una regla, fijos durante su vigencia.
- **Original / vigente**: el presupuesto aprobado, que ya no se edita, y el original más sus ajustes.
- **Ajuste presupuestario**: un traslado, o un aumento o una rebaja, que se registra después de aprobar.
- **Base**: la lista de valores por destino con que una regla reparte por inductor (empleados, metros cuadrados…).

## Producto
1. **Sistema independiente**, con repo público. A futuro será el módulo de presupuesto de Maat (el ERP contable de la firma) y leerá lo real del libro diario; por eso usa el mismo stack.
2. **Lo real entra por archivo** (Excel/CSV), para servir con cualquier sistema contable; en un segundo paso se lee de Maat (decisión 37).
3. **La v1 trabaja solo en lempiras.** El archivo del real llega ya convertido, como queda en el libro.

## Dinero
4. **Dinero en `Decimal` con 2 decimales.** Los pesos, porcentajes y cantidades llevan los que necesiten.
5. **Repartir no pierde ni inventa un centavo**: se trunca y los centavos sobrantes van por mayor residuo.

## Presupuesto
6. **Se presupuestan cuentas contables, no centros de costo.** La fila es cuenta × línea de detalle × responsable × mes. No lleva CeCo, salvo la línea de un gasto compartido, que dice de qué genérico es (decisión 29).
7. **Los meses se agrupan en períodos que define cada empresa** (decisión 33); el tablero muestra mes, período y acumulado.

## Centros
8. **Los centros son un árbol aparte del catálogo de cuentas.** Cada centro apunta a su superior, todos pueden recibir movimiento y la unidad de negocio es el nivel superior del árbol. Los totales suben por el árbol.
9. **Cada CeCo pertenece a un área responsable.** En un genérico, esa área es el dueño del gasto compartido.
10. **Tres tipos de CeCo**: específico (el gasto se queda ahí), genérico (se reparte con una regla) e institucional (por política no se reparte). Los ingresos van a CeBes.
11. **Un gasto directo va al CeCo propio del área**, sin genérico y sin regla.
12. **Un genérico sin regla queda centralizado**, para que un CeCo nuevo no trabe el cierre; el tablero lo avisa. Un específico o un institucional con regla es un error de catálogo.

## Reglas de distribución
13. **Una regla siempre reparte el 100 %.** Tiene dos tramos: primero los montos fijos y después el resto, por porcentaje (suma 100) o por inductor, que se puede partir en pedazos (decisión 43). Si un CeCo está en los dos tramos, sus partes se suman.
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

## Modelo de datos
24. **Varias empresas, separadas en la base.** Cada empresa tiene su catálogo, sus centros, su presupuesto, sus reglas y su real, y la base (RLS) impide que una empresa vea los datos de otra: como en Maat, la firma lleva varias empresas.
25. **Las áreas son un catálogo propio de cada empresa, en varios niveles.** Cada área puede tener un área superior (Comercial agrupa a Ventas y Mercadeo) y los totales suben por ese árbol, aparte del árbol de centros: así el área no depende de cómo se ordenen los centros.
26. **Cada CeCo pertenece a exactamente un área, y el área sale del CeCo: no se digita en el asiento.** Así la suma de las áreas siempre cuadra con el total real.
27. **La foto del cierre guarda el área que tenía cada CeCo ese día**, para que reorganizar las áreas no reescriba un mes cerrado.
28. **Cualquier área, de cualquier nivel, puede tener CeCos y presupuestar líneas de detalle**, igual que los centros (decisión 8). El tablero de un área superior separa lo propio de lo que suma de sus sub-áreas.
29. **El presupuesto de un gasto compartido también se reparte** con la regla de su genérico, igual que lo real (decisión 15), para que cada área compare su parte del presupuesto contra su parte de lo real. Por eso esa línea de detalle dice de qué genérico es: sin ese dato no se sabe con qué regla partirla.

## Permisos
30. **Todo se controla por permisos, y un rol es un juego de permisos dentro de una empresa.** Nada queda amarrado a una persona: cada acción (editar catálogos y reglas, capturar, aprobar y ajustar el presupuesto, cargar el real, cerrar el mes, ver el tablero) es un permiso, con un código al estilo de Maat (`presupuesto.aprobar`). La v1 trae dos roles: el analista de presupuesto, con todos los permisos, y el responsable de área, que consulta el presupuesto y el tablero de sus áreas y sub-áreas. Las pantallas preguntan por el permiso, nunca por el nombre del rol.

## Ciclo del presupuesto
31. **El presupuesto se aprueba completo, una vez al año, no por área.** El original ya no se edita, los ejercicios anteriores se consultan como histórico en solo lectura, y lo que cambie después de aprobar entra como ajuste presupuestario.
32. **En la v1 entran los dos tipos de ajuste**: traslados (mueven un monto entre líneas o meses sin cambiar el total) y aumentos o rebajas (cambian el total del año). Llevan motivo y fecha, y solo tocan meses abiertos. El tablero compara contra el vigente, y el original se sigue viendo.
33. **Los períodos los define cada empresa en cada ejercicio; el sistema no fija ninguna agrupación.** Hay opciones rápidas (mensual, bimestral, trimestral, cuatrimestral, semestral, anual) y rangos propios, siempre de meses seguidos, sin traslaparse y cubriendo los 12. Un ejercicio nuevo propone los del anterior, y al aprobar el presupuesto quedan fijos.
34. **La v1 presupuesta ingresos, costos y gastos**: toda cuenta de detalle de naturaleza INGRESO, COSTO o GASTO. En los ingresos la lectura va al revés (cobrar de más es bueno y cobrar de menos es lo que se explica); sale de una tabla por naturaleza, con los mismos umbrales. El resultado por CeBe sigue fuera (decisión 23).
35. **El presupuesto también se importa, con una plantilla que se descarga del sistema**, solo mientras el ejercicio está en borrador: `cuenta, descripcion, responsable, generico` (solo en gasto compartido) y los 12 meses. Cada archivo agrega sus líneas al borrador, así cada área manda el suyo, con vista previa y todo o nada (decisión 40); una línea repetida (misma cuenta, descripción y responsable) es un error. La captura a mano queda para corregir o agregar.
36. **La pantalla del presupuesto muestra, en solo lectura, el aprobado del año anterior**: por cuenta siempre y por línea cuando la línea ya existía (misma cuenta, descripción y responsable). La plantilla de importación lo trae lleno. Los reportes y exportaciones fuera del tablero no son parte de este proyecto.

## Cómo entran los datos
37. **Maat Presupuesto maneja todo lo del presupuesto, y a Maat no se le cambia nada.** Para no tener la misma información dos veces, el catálogo, los centros y el real vienen de Maat, y aquí se guarda lo propio: tipo, área y regla de cada centro, bases y presupuesto. Va en dos pasos dentro de la v1. Primero por archivo, con las columnas de la importación de asientos de Maat más el centro (`comprobante, fecha, descripcion, cuenta, centro_costo, debe, haber` y, opcional, `descripcion_linea`). Después, un adaptador del borde lee de la API de Maat el catálogo, los centros y los asientos contabilizados, con un botón «Traer de Maat» junto a «Importar archivo»; el dominio no cambia.
38. **Lo que se repite cada mes es automático; a mano queda solo lo que decide una persona o lo que vive en otro sistema.** Con el segundo paso de la decisión 37, cada mes solo se revisa y se cierra: el real llega de Maat, y el reparto, la comparación y el tablero los calcula el sistema. El tipo, el área y la regla de cada centro se cargan una vez y se mantienen; el presupuesto, una vez al año, y las bases, unas veces al año.
39. **Los catálogos (cuentas, centros y áreas) entran la primera vez por archivo, con plantillas que se descargan del sistema**, con vista previa y todo o nada. Después se mantienen a mano: agregar, renombrar o inactivar, sin borrar. Con «Traer de Maat», las cuentas y los centros llegan de Maat y aquí se completa lo que Maat no tiene; las áreas son siempre de Maat Presupuesto.
40. **El archivo del real entra entero o no entra.** Si una fila tiene error no se carga ninguna: se corrige el archivo y se sube completo, para que el real del mes cuadre con el libro.
41. **Un archivo nuevo del mes abierto reemplaza completo al anterior**, que queda en el historial como reemplazado, con su fecha y quién lo subió. Un mes cerrado no acepta archivos.

## Reglas y bases
42. **Una regla por gasto.** Un genérico tiene una regla por cada gasto que recibe (energía, vigilancia, teléfono…): cada regla es de un genérico y una cuenta, con su fotografía y sus tramos, y sus montos fijos salen solo de ese gasto. Un gasto de un genérico sin regla queda centralizado (decisión 12, leída por gasto).
43. **El resto de una regla se puede partir en pedazos por porcentaje**, y cada pedazo va entero a un centro o se reparte según una base. Por ejemplo, después de los fijos, el 50 % a Administración y el 50 % entre las sucursales según los metros cuadrados. Un solo nivel: un pedazo no se vuelve a partir. Primero se parte el resto y después cada pedazo, las dos veces sin perder un centavo (decisión 5). Quien no lo necesita usa un solo pedazo.
44. **Las bases se guardan aparte y las reglas las usan.** Una base es una lista de números por destino con el nombre que le pone la empresa: el sistema no sabe qué representan. Vale desde un mes, como la fotografía, y entra por archivo con plantilla (`destino, valor` y el mes desde el que vale), con vista previa y todo o nada; se corrige a mano. Varias reglas usan la misma base, que se actualiza una sola vez, y una regla puede usar la base completa o solo algunos destinos. Los meses cerrados conservan su foto.
