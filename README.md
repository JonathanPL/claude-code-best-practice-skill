# claude-code-best-practice-skill

La documentación de [shanraisshan/claude-code-best-practice](https://github.com/shanraisshan/claude-code-best-practice)
(MIT, © Shayan Rais) convertida en **una skill** que [Paperclip](https://paperclip.ing) puede importar desde git.

## Por qué existe

Paperclip solo importa los ficheros que cuelgan de una carpeta con `SKILL.md`. En el repo original eso son las demos
de `.claude/skills/`; las guías (`best-practice/`, `tips/`, `reports/`…) se ignoran. Aquí esas guías son las
referencias de una sola skill, con un índice en `SKILL.md`. El agente lee el índice y abre solo el documento que
necesita.

```
skills/claude-code-best-practice/
  SKILL.md                      índice y modo de uso
  references/best-practice/     settings.json, commands, skills, subagents, memoria, MCP, flags del CLI
  references/implementation/    implementaciones de referencia
  references/orchestration-workflow/   patrón Command → Agent → Skill
  references/development-workflows/    RPI (con sus agentes y commands) y Claude + Codex
  references/reports/           informes
  references/tips/              tips de Boris Cherny y Thariq
  references/tutorial/          día 0 y día 1
tools/sync_upstream.py          generador
UPSTREAM.json                   commit del original usado, exclusiones y parches
```

## Cambios respecto al original

- **Sin imágenes ni badges.**
  - Las imágenes se sustituyen por enlaces `[imagen: alt](…)` a GitHub en el commit usado.
  - Las badges de categoría y versión pasan a texto, y la de «Last Updated» se quita.
  - Se quita la cabecera «← Back» de cada página.
- **Enlaces reescritos.**
  - Los enlaces entre documentos incluidos apuntan a su nueva ruta.
  - Los que apuntan a lo no incluido (`.claude/`, `!/`, el README raíz) pasan a URL de GitHub en el commit usado.
  - Un enlace roto del original (`reports/claude-cli-startup-flags.md`) se redirige a `best-practice/`.
- **Rutas.**
  - `development-workflows/rpi/.claude/` pasa a `rpi/claude-config/`, para que ningún cliente la tome por
    configuración real.
  - `tutorial/day{0,1}/README.md` pasan a `tutorial/day{0,1}.md`.
- **Excluidos:**
  - `orchestration-workflow/output.md` (salida de la demo);
  - `tutorial/day0/{linux,mac,windows}.md` (instalación por sistema operativo);
  - `reports/learning-journey-weather-reporter-redesign.md` (plan de las diapositivas del autor);
  - todo lo que está fuera de las 7 carpetas (`.claude/`, `changelog/`, `presentation/`, `videos/`…).
- **Un parche de contenido.** En el ejemplo de `permissions.deny` de `best-practice/claude-settings.md` se reordena
  la lista para que `"Bash(curl *)"` vaya primero.
  - Motivo: la secuencia `.env` → `secrets` → `curl` casa con el patrón de «exfiltración de secretos» de la auditoría
    de Paperclip, aunque el ejemplo precisamente prohíbe esas acciones.
  - Una lista `deny` significa lo mismo en cualquier orden.
- Cada referencia lleva al principio una nota con el enlace al original.

## Regenerar desde el original

```bash
python3 -I tools/sync_upstream.py             # último commit de main
python3 -I tools/sync_upstream.py --check     # solo valida
```

El script descarga el original con `gh`, aplica los cambios y valida antes de escribir:
- la auditoría de Paperclip, con sus patrones de ejecución remota y de exfiltración copiados;
- el frontmatter de `SKILL.md`;
- UTF-8 y menos de 1 MiB por fichero;
- que no haya enlaces relativos rotos.

Si algo falla, no escribe nada. Si el original añade un documento, sale en el índice como «(sin resumen)» y conviene
añadirle una línea en `SUMMARIES`.

Después: commit y push, y en Paperclip «refresh» de la fuente de skills o «install update» de la skill.

## Licencia

MIT. El contenido es de Shayan Rais (ver `LICENSE`); la adaptación y el generador se publican con la misma licencia.
