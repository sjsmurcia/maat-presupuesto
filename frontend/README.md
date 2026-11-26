# Frontend de Maat Presupuesto

La app web (Flutter, PWA) de Maat Presupuesto: las 8 pantallas del lienzo de diseño. El enlace al lienzo está en Jira, en MP-5. Las reglas de negocio no se escriben aquí: las aplica la API, y la app muestra lo que la API responde.

## Requisitos

- Flutter **3.44.0**, la versión fijada en `.fvmrc`. Con [FVM](https://fvm.app): `fvm install 3.44.0` y después `fvm flutter …` en lugar de `flutter …`.
- Chrome, para correr la app.

## Comandos

Desde la carpeta `frontend/`:

```
flutter pub get
flutter analyze
flutter test
flutter run -d chrome
```

`flutter analyze` tiene que salir sin problemas y `flutter test`, en verde, antes de abrir un PR. Para dar formato al código: `dart format .`.

## Dónde va cada cosa

```
lib/
  main.dart               arranca la app dentro de un ProviderScope
  app/                    el armado: tema, router, barra lateral, cascarón
    destinos.dart         la tabla de pantallas de la barra (una fila por pantalla)
    proveedores.dart      el cliente HTTP que usa toda la app
  core/                   lo que comparten todas las pantallas
    tema/                 tokens de color, medidas y tipografía de Maat
    montos/               leer y mostrar dinero (Decimal, nunca double)
    http/                 el puerto ClienteHttp, su adaptador con Dio y uno falso
    widgets/              widgets que usan varias pantallas
  features/<pantalla>/
    datos/                habla con la API: rutas, JSON y modelos
    aplicacion/           el estado de la pantalla (providers de Riverpod)
    presentacion/         los widgets de la pantalla
test/                     la misma estructura que lib/
```

Las dependencias van hacia adentro: `presentacion` usa `aplicacion`, que usa `datos`, que usa `core`. Una pantalla no importa nada de otra: si algo se comparte, sube a `core/`.

Las reglas para escribir código aquí (también para la IA) están en `CLAUDE.md`, en esta carpeta.
