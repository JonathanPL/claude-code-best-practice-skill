---
name: claude-code-best-practice
description: >-
  Guías de buenas prácticas de Claude Code (adaptadas de shanraisshan/claude-code-best-practice).
  Úsala para configurar o razonar sobre Claude Code: settings.json, permisos, hooks, subagents,
  skills, slash commands, CLAUDE.md y memoria, servidores MCP, flags del CLI, agent teams, /loop y
  /goal; para diseñar flujos de agentes (patrón Command → Agent → Skill, RPI, Claude + Codex); y para
  consultar tips de Boris Cherny y Thariq sobre sesiones, contexto, revisión de código y skills.
tags: [claude-code, best-practices, settings, hooks, subagents, skills, commands, mcp, workflows]
author: Shayan Rais (original); adaptación de JonathanPL
homepage: https://github.com/shanraisshan/claude-code-best-practice
---

# Claude Code: buenas prácticas

Documentación de [shanraisshan/claude-code-best-practice](https://github.com/shanraisshan/claude-code-best-practice) (MIT, © Shayan Rais), adaptada como skill:
una referencia por documento, sin imágenes ni badges y con los enlaces internos reescritos. Original en el
commit [`0bbb72f`](https://github.com/shanraisshan/claude-code-best-practice/tree/0bbb72f00514e9a8bf16bf8a1de04a5695e8f904) (2026-11-22).

## Cómo usarla

1. Busca en el índice de abajo el documento que responde a tu duda.
2. Abre SOLO esa referencia. Son largas: `claude-settings.md` tiene ~1.480 líneas, así que busca la sección
   (`grep -n`) en vez de leerla entera.
3. Lo que estas guías describen es Claude Code (el CLI). Antes de aplicarlo a otro cliente (OpenCode,
   Paperclip), comprueba que la función existe allí.
4. Las imágenes del original no están copiadas: aparecen como enlaces `[imagen: …]` a GitHub.

## Índice

### Guías de referencia

- [`best-practice/claude-cli-startup-flags.md`](references/best-practice/claude-cli-startup-flags.md) — Flags de arranque del CLI, subcomandos de primer nivel y variables de entorno de arranque.
- [`best-practice/claude-commands.md`](references/best-practice/claude-commands.md) — Comandos slash: campos del frontmatter de un command propio y catálogo de los comandos integrados, por categoría.
- [`best-practice/claude-mcp.md`](references/best-practice/claude-mcp.md) — Servidores MCP recomendados para el día a día y cómo configurarlos.
- [`best-practice/claude-memory.md`](references/best-practice/claude-memory.md) — CLAUDE.md como memoria persistente: cómo escribirlo y cómo se carga en monorepos.
- [`best-practice/claude-power-ups.md`](references/best-practice/claude-power-ups.md) — Power-ups: lecciones interactivas del CLI sobre funciones poco conocidas (desde v2.1.90).
- [`best-practice/claude-settings.md`](references/best-practice/claude-settings.md) — Referencia completa de `settings.json` (249+ ajustes, 403+ variables de entorno): permisos, hooks, modelo, sandbox, statusline, MCP…, con un ejemplo final completo. Es la más larga: busca la sección.
- [`best-practice/claude-skills.md`](references/best-practice/claude-skills.md) — Skills: campos del frontmatter de SKILL.md y skills integradas oficiales.
- [`best-practice/claude-subagents.md`](references/best-practice/claude-subagents.md) — Subagents: campos del frontmatter y tipos de agente integrados.

### Implementaciones de referencia

- [`implementation/claude-agent-teams-implementation.md`](references/implementation/claude-agent-teams-implementation.md) — Agent Teams: varias sesiones de Claude Code coordinadas con una lista de tareas compartida, y en qué se diferencian de los subagents.
- [`implementation/claude-commands-implementation.md`](references/implementation/claude-commands-implementation.md) — Ejemplo real de command (`/weather-orchestrator`) como punto de entrada del patrón Command → Agent → Skill.
- [`implementation/claude-goal-implementation.md`](references/implementation/claude-goal-implementation.md) — Implementación de `/goal`, a partir de un hilo de la comunidad.
- [`implementation/claude-scheduled-tasks-implementation.md`](references/implementation/claude-scheduled-tasks-implementation.md) — Tareas recurrentes con la skill `/loop` en un intervalo tipo cron.
- [`implementation/claude-skills-implementation.md`](references/implementation/claude-skills-implementation.md) — Dos skills de ejemplo y sus dos formas de invocación: precargada en un agente o llamada directamente.
- [`implementation/claude-subagents-implementation.md`](references/implementation/claude-subagents-implementation.md) — Ejemplo real de subagent (weather-agent) dentro del patrón Command → Agent → Skill.

### Patrón de orquestación Command → Agent → Skill

- [`orchestration-workflow/orchestration-workflow.md`](references/orchestration-workflow/orchestration-workflow.md) — El patrón Command → Agent (con skill) → Skill paso a paso, con diagramas y el flujo de la demo del tiempo.

### Workflows de desarrollo

- [`development-workflows/cross-model-workflow.md`](references/development-workflows/cross-model-workflow.md) — Flujo cruzado Claude Code + Codex CLI.
- [`development-workflows/rpi/claude-config/agents/code-reviewer.md`](references/development-workflows/rpi/claude-config/agents/code-reviewer.md) — Agente revisor: corrección, claridad, seguridad y mantenibilidad.
- [`development-workflows/rpi/claude-config/agents/constitutional-validator.md`](references/development-workflows/rpi/claude-config/agents/constitutional-validator.md) — Agente que valida propuestas frente a los principios («constitución») del proyecto.
- [`development-workflows/rpi/claude-config/agents/documentation-analyst-writer.md`](references/development-workflows/rpi/claude-config/agents/documentation-analyst-writer.md) — Agente que analiza la documentación existente y escribe docs según las normas del proyecto.
- [`development-workflows/rpi/claude-config/agents/product-manager.md`](references/development-workflows/rpi/claude-config/agents/product-manager.md) — Agente PM: de una petición a un PRD con criterios de aceptación y alcance.
- [`development-workflows/rpi/claude-config/agents/requirement-parser.md`](references/development-workflows/rpi/claude-config/agents/requirement-parser.md) — Agente que extrae requisitos, objetivos y restricciones de una petición.
- [`development-workflows/rpi/claude-config/agents/senior-software-engineer.md`](references/development-workflows/rpi/claude-config/agents/senior-software-engineer.md) — Agente ingeniero senior: pasos pequeños y reversibles, con tests y PRs claros.
- [`development-workflows/rpi/claude-config/agents/technical-cto-advisor.md`](references/development-workflows/rpi/claude-config/agents/technical-cto-advisor.md) — Agente CTO: contrasta las decisiones técnicas con los principios y estándares de ingeniería.
- [`development-workflows/rpi/claude-config/agents/ux-designer.md`](references/development-workflows/rpi/claude-config/agents/ux-designer.md) — Agente UX: brief con flujos, estados y anotaciones.
- [`development-workflows/rpi/claude-config/commands/rpi/implement.md`](references/development-workflows/rpi/claude-config/commands/rpi/implement.md) — Command RPI de implementación por fases con puertas de validación.
- [`development-workflows/rpi/claude-config/commands/rpi/plan.md`](references/development-workflows/rpi/claude-config/commands/rpi/plan.md) — Command RPI de planificación: documentación completa de una funcionalidad.
- [`development-workflows/rpi/claude-config/commands/rpi/research.md`](references/development-workflows/rpi/claude-config/commands/rpi/research.md) — Command RPI de investigación: viabilidad y decisión GO/NO-GO.
- [`development-workflows/rpi/rpi-workflow.md`](references/development-workflows/rpi/rpi-workflow.md) — Flujo RPI (Research → Plan → Implement) con puertas GO/NO-GO; usa los agentes y commands de `rpi/claude-config/`.

### Informes

- [`reports/claude-advanced-tool-use.md`](references/reports/claude-advanced-tool-use.md) — Patrones avanzados de tool use en la API para gastar menos tokens y latencia y acertar más con las herramientas.
- [`reports/claude-agent-command-skill.md`](references/reports/claude-agent-command-skill.md) — Agents vs commands vs skills: cuándo usar cada uno.
- [`reports/claude-agent-memory.md`](references/reports/claude-agent-memory.md) — Memoria persistente de los subagents (frontmatter `memory`).
- [`reports/claude-agent-sdk-vs-cli-system-prompts.md`](references/reports/claude-agent-sdk-vs-cli-system-prompts.md) — System prompts del Agent SDK frente a los del CLI, y su efecto en la consistencia de las respuestas.
- [`reports/claude-global-vs-project-settings.md`](references/reports/claude-global-vs-project-settings.md) — Qué funciones son solo globales (`~/.claude/`) y cuáles tienen versión de proyecto (`.claude/`).
- [`reports/claude-in-chrome-v-chrome-devtools-mcp.md`](references/reports/claude-in-chrome-v-chrome-devtools-mcp.md) — Comparativa de MCP para automatizar el navegador (Claude in Chrome, Chrome DevTools MCP y un tercero).
- [`reports/claude-skills-for-larger-mono-repos.md`](references/reports/claude-skills-for-larger-mono-repos.md) — Cómo descubre y carga Claude Code las skills en monorepos grandes.
- [`reports/claude-spinner-verbs-and-tips.md`](references/reports/claude-spinner-verbs-and-tips.md) — Los verbos y tips que muestra el spinner del CLI.
- [`reports/claude-usage-and-rate-limits.md`](references/reports/claude-usage-and-rate-limits.md) — Límites de uso, rate limits y créditos de uso, y cómo seguir trabajando al llegar al límite.
- [`reports/llm-day-to-day-degradation.md`](references/reports/llm-day-to-day-degradation.md) — ¿Empeora un LLM de un día para otro con los pesos congelados? Causas demostradas, bugs de infraestructura y sesgos.
- [`reports/why-harness-is-important.md`](references/reports/why-harness-is-important.md) — Por qué el harness de Claude Code marca la diferencia frente a «solo prompts».

### Tips con fuente (Boris Cherny, Thariq)

- [`tips/claude-boris-10-tips-01-feb-26.md`](references/tips/claude-boris-10-tips-01-feb-26.md) — 10 consejos del equipo de Claude Code, vía Boris Cherny (1-feb-26).
- [`tips/claude-boris-12-tips-12-feb-26.md`](references/tips/claude-boris-12-tips-12-feb-26.md) — 12 formas de personalizar Claude Code, de Boris Cherny (12-feb-26).
- [`tips/claude-boris-13-tips-03-jan-26.md`](references/tips/claude-boris-13-tips-03-jan-26.md) — Boris Cherny (creador de Claude Code): cómo lo usa él, 13 consejos (3-ene-26).
- [`tips/claude-boris-15-tips-30-mar-26.md`](references/tips/claude-boris-15-tips-30-mar-26.md) — 15 funciones ocultas o poco usadas de Claude Code, de Boris Cherny (30-mar-26).
- [`tips/claude-boris-2-tips-10-mar-26.md`](references/tips/claude-boris-2-tips-10-mar-26.md) — Revisión de código y test-time compute, de Boris Cherny (10-mar-26).
- [`tips/claude-boris-2-tips-25-mar-26.md`](references/tips/claude-boris-2-tips-25-mar-26.md) — Squash merge y distribución del tamaño de los PR, de Boris Cherny (25-mar-26).
- [`tips/claude-boris-6-tips-16-apr-26.md`](references/tips/claude-boris-6-tips-16-apr-26.md) — 6 consejos para sacar más partido a Opus 4.7, de Boris Cherny (16-abr-26).
- [`tips/claude-thariq-tips-16-apr-26.md`](references/tips/claude-thariq-tips-16-apr-26.md) — Thariq: gestión de sesiones, ventana de 1M y compactación (16-abr-26).
- [`tips/claude-thariq-tips-17-mar-26.md`](references/tips/claude-thariq-tips-17-mar-26.md) — Thariq: cómo usa Anthropic las skills internamente (17-mar-26).

### Tutorial

- [`tutorial/day0.md`](references/tutorial/day0.md) — Día 0: instalar Claude Code y autenticarse (sin las guías por sistema operativo).
- [`tutorial/day1.md`](references/tutorial/day1.md) — Día 1: los tres niveles de uso: prompts, agentes y skills.
