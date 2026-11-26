# ADR-1: Sitio y API en Vercel, base en PostgreSQL de Azure

- **Estado:** aceptada
- **Fecha:** 2026-11-25
- **Decisión vigente:** la 48 de [`docs/decisiones.md`](../decisiones.md). Este ADR cuenta el contexto y las consecuencias.

## Contexto

- El producto tiene que estar publicado en una URL pública con HTTPS, y el sitio, el login, el portal privado y el healthcheck de la API tienen que responder en el mismo dominio.
- El stack es el de Maat (decisión 1): Flutter web, que se publica como archivos estáticos, una API en FastAPI con Python 3.12 o más (`pyproject.toml`) y PostgreSQL.
- La base tiene que ser un PostgreSQL de verdad: cada empresa ve solo sus datos, y eso lo impide la propia base con RLS (decisión 24).
- El presupuesto es cero. Tenemos una cuenta de estudiante de Azure con crédito y servicios gratis por 12 meses, que solo deja crear recursos en algunas regiones.
- El repo es público y la base guarda solo datos ficticios.

Opciones que se compararon:

1. **Todo en Azure Static Web Apps.** Sirve el sitio gratis, pero sus funciones administradas llegan solo a Python 3.11.
2. **Sitio y API en Vercel, base en Neon** (PostgreSQL serverless con plan gratis). Cumple, pero deja sin usar la cuenta de estudiante, que ya da un PostgreSQL gestionado completo.
3. **Sitio y API en Vercel, base en Azure.**

## Decisión

Elegimos la opción 3:

- **Vercel** publica el Flutter web como sitio estático y FastAPI como función de Python 3.12, en el mismo dominio.
- **La base** es un servidor flexible de Azure Database for PostgreSQL, tamaño B1MS, de la cuenta de estudiante, en una de las regiones que la cuenta permite.
- **La cadena de conexión** vive solo en las variables de entorno de Vercel y en los secrets de GitHub, nunca en el repo.

## Consecuencias

**Lo que ganamos:**

- Cuesta cero el primer año: el B1MS trae 750 horas al mes y 32 GB gratis por 12 meses, y Vercel tiene plan gratis.
- La API corre en Python 3.12, la misma versión del dominio y de los tests.
- El sitio y la API comparten dominio y HTTPS: el navegador no necesita permisos entre dominios (CORS) para hablar con la API.
- La base es el mismo motor de Maat, con RLS, llaves foráneas e índices, así que el modelo de datos se puede llevar a Maat sin traducirlo.

**Lo que sacrificamos:**

- **Dos proveedores en vez de uno:** dos cuentas, dos consolas y dos lugares donde mirar si algo falla.
- **Latencia entre la API y la base:** cada consulta viaja por internet de Vercel a Azure. Para que pese poco, la región de Azure se elige cerca de la región de las funciones de Vercel.
- **Funciones serverless:** la primera llamada después de un rato quieto tarda más (arranque en frío), y cada invocación abre su conexión, así que hay que cuidar el número de conexiones, que en un B1MS es bajo.
- **Un firewall que no puede filtrar por IP:** las funciones de Vercel no tienen IP fija, así que la base acepta conexiones de internet. La protección queda en TLS obligatorio, una contraseña fuerte y un usuario de la app con los permisos justos.
- **Gratis solo por un año:** después hay que pagar el servidor o mudar la base. Cuando el sistema se integre a Maat (decisión 1), el hosting lo define Maat.
