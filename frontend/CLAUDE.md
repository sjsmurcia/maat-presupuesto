# CLAUDE.md — frontend (Flutter)

Se suma al `CLAUDE.md` de la raíz, que sigue mandando: idioma, vocabulario, reglas de oro, Clean Code, TDD, Git y «Trabajo en grupo». Aquí va solo lo propio de Flutter. Los comandos y la estructura están en `README.md`.

## Qué copia cada pantalla
- Cada pantalla copia su artboard del lienzo de diseño y su sección del handoff: medidas, estados, textos y campos de la API. El enlace al lienzo está en Jira, en MP-5.
- Un estado del lienzo (vacío, error, confirmar, cerrado…) es un estado de la pantalla, con su widget test.

## Dónde va cada cosa
- `features/<pantalla>/datos`: la ruta de la API, el JSON y el modelo. Solo esta capa usa `ClienteHttp`.
- `features/<pantalla>/aplicacion`: el estado de la pantalla, con providers de Riverpod.
- `features/<pantalla>/presentacion`: los widgets. Un widget no llama a la API ni arma JSON.
- `core/` lo comparten todas; `app/` arma la app (tema, router, barra lateral). Una pantalla no importa nada de otra: lo compartido sube a `core/`.
- Una pantalla nueva en la barra es una fila en `Destino` (`app/destinos.dart`) y su entrada en el router. No se agrega un `if`.

## Reglas
- **Ninguna regla de negocio en Dart.** La API valida, calcula y reparte. La pantalla muestra el mensaje de error de la API tal cual. Si falta una regla, se pide en el issue de Jira.
- **Dinero:** llega como texto con 2 decimales y se lee con `montoDesdeJson`; se muestra con `formatearMonto`. Nunca `double`.
- **Permisos, no roles:** la pantalla pregunta por un permiso (`presupuesto.aprobar`), nunca por el nombre de un rol.
- **Tema de Maat:** colores solo con `context.tokens`, medidas con `MedidasMaat` y textos con `TipografiaMaat`. Nada de hex ni de números sueltos en un widget. Radio de 3px, sin sombras ni degradados. Las cifras van en mono con `tabularFigures`.
- **Nombres en español**, como el dominio: clases sustantivo, funciones verbo, booleanos como pregunta (`esActivo`, `tieneRegla`, `estaCerrado`).
- **Funciones y `build` de 30 líneas como máximo.** Un widget que crece se parte en widgets privados (`_Fila`, `_Pie`), no en métodos que devuelven widgets.
- **Comentarios:** solo el porqué que el código no dice.

## Tests
- Un widget test por estado del lienzo, con `ClienteHttpFalso` y las respuestas de ejemplo del handoff. La red real no se usa en un test.
- Nombre que dice qué, cuándo y qué espera; AAA visible; el valor exacto en el `expect`.
- Antes del PR: `flutter analyze` sin problemas, `flutter test` en verde y `dart format .`.
