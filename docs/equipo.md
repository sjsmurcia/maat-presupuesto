# Equipo

Cómo trabajamos los siete en Maat Presupuesto. Quién tiene cada rol está en Jira (proyecto MP, Epic MP-1), no aquí: el repo es público.

## Antes de escribir código

Lee `CLAUDE.md` y `docs/decisiones.md`. Mandan sobre todo lo demás, también sobre lo que te proponga la IA: si tu Claude propone algo que contradice una decisión, gana la decisión. Si una parte de Jira (MP-2 a MP-8) dice otra cosa que `docs/decisiones.md`, también gana la decisión.

## Cómo empezar

1. Acepta las invitaciones de jm al repo y a Jira.
2. Clona el repo y corre los tests (Python 3.12 o más):
   ```
   git clone https://github.com/sjsmurcia/maat-presupuesto.git
   cd maat-presupuesto
   python -m pip install pytest
   python -m pytest -q
   ```
   Tienes que ver todos los tests en verde.
3. Tu rol es un issue en Jira, bajo el Epic MP-1. Parte el trabajo en subtareas de ese issue, una por PR, y pasa a «En curso» la que vas a hacer.
4. Crea tu rama desde `main` al día, con el tema del issue:
   ```
   git switch main
   git pull
   git switch -c paso/<tema>
   ```
5. Haz commits en **Conventional Commits en español**: `tipo(ámbito): descripción`, con un espacio después de los dos puntos y sin la línea «Co-Authored-By». Por ejemplo: `feat(tablero): mostrar el acumulado por área`, `test(cierre): …`, `docs(adr): …`.
6. Sube la rama y abre el PR contra `main`:
   ```
   git push -u origin paso/<tema>
   ```
   La plantilla del PR te pide el issue, la decisión que aplica, qué hizo la IA y qué hiciste tú, y los tests.
7. jm revisa todos los PR. El tuyo entra cuando jm lo aprueba y el check `pruebas` está en verde. Si pide cambios, súbelos a la misma rama.

## Reglas del grupo

- **Un PR por subtarea de Jira**, de menos de unas 300 líneas. Si crece, pártelo.
- **Puedes usar la IA, pero lo que entra lo explicas tú**, línea por línea. jm te puede preguntar por cualquier línea en la revisión.
- **El dominio (`presupuesto/`) lo escribe jm.** Si tu pantalla necesita una regla que no existe, pídela en tu issue de Jira; no la escribas en la pantalla.
- **Ni vocabulario nuevo ni reglas de negocio sin preguntar**: la pregunta va como comentario en tu issue de Jira, y jm decide.
- **`CLAUDE.md` y `docs/decisiones.md` los cambia solo jm.**
- **Ningún dato real**: ni clientes, ni empresas, ni personas. Los ejemplos son ficticios.

## Roles por capa

| Capa | Rol | Qué le toca | Parte en Jira |
|---|---|---|---|
| Dominio | jm (líder) | Las reglas como funciones puras, con TDD | MP-2 |
| Backend | jm con Claude | La base (PostgreSQL) y la API (FastAPI) | MP-3, MP-4 |
| Frontend | Frontend A | Login, barra lateral, catálogo y árbol de centros | MP-5 |
| Frontend | Frontend B | Presupuesto y reglas de distribución | MP-5 |
| Frontend | Frontend C | Carga de lo real, cierre y tablero | MP-5 |
| Calidad | Calidad y despliegue | CI, SonarCloud, hosting, headers de seguridad, PWA con el service worker escrito a mano y el código LEARN | MP-6, MP-7 |
| Calidad | Pruebas y demo | Widget tests, usuario demo con su recorrido de 4 URLs y capturas | MP-5, MP-7, MP-8 |
| Documentos | Documentos | C4, ADRs, presentación HTML, texto del cliente, bitácora de IA y reflexión | MP-8 |

## Comandos

```
python -m pytest -q
```

Los comandos de Flutter se agregan aquí en el PR que cree la app.
