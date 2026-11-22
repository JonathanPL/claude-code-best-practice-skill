#!/usr/bin/env python3
"""Generate the `claude-code-best-practice` skill from shanraisshan/claude-code-best-practice.

Takes the documentation folders of the original repo (best-practice, implementation,
orchestration-workflow, development-workflows, tips, reports, tutorial) and turns them into
ONE skill that Paperclip can import: `skills/claude-code-best-practice/SKILL.md` plus
`references/**`.

Usage (from the repo root):
    python3 -I tools/sync_upstream.py                 # latest commit of main
    python3 -I tools/sync_upstream.py --ref <sha>     # a fixed commit
    python3 -I tools/sync_upstream.py --check         # generate and validate without writing
    python3 -I tools/sync_upstream.py --source DIR    # use an already extracted copy (needs --sha)

It writes nothing unless every check passes: Paperclip's local audit, relative links,
size and UTF-8.
"""

from __future__ import annotations

import argparse
import json
import posixpath
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import urllib.parse
from pathlib import Path

UPSTREAM = "shanraisshan/claude-code-best-practice"
SKILL_NAME = "claude-code-best-practice"
REPO_ROOT = Path(__file__).resolve().parent.parent
SKILL_DIR = REPO_ROOT / "skills" / SKILL_NAME
MAX_FILE_BYTES = 1024 * 1024  # Paperclip limit per skill file

INCLUDE_DIRS = [
    "best-practice",
    "implementation",
    "orchestration-workflow",
    "development-workflows",
    "tips",
    "reports",
    "tutorial",
]
EXCLUDE = {
    # Output of the weather demo, not documentation.
    "orchestration-workflow/output.md",
    # Per-OS install guides: no use to agents, and linux.md (curl | sh) and mac.md
    # (bash -c) fail Paperclip's audit.
    "tutorial/day0/linux.md",
    "tutorial/day0/mac.md",
    "tutorial/day0/windows.md",
    # The author's plan for redesigning their slides, not a guide.
    "reports/learning-journey-weather-reporter-redesign.md",
}
# Links that are broken in the original and have an obvious target.
LINK_FIXES = {
    "reports/claude-cli-startup-flags.md": "best-practice/claude-cli-startup-flags.md",
}
PATH_OVERRIDES = {
    "development-workflows/cross-model-workflow/cross-model-workflow.md": "development-workflows/cross-model-workflow.md",
    "tutorial/day0/README.md": "tutorial/day0.md",
    "tutorial/day1/README.md": "tutorial/day1.md",
}

# Explicit content patches. Each one must apply EXACTLY once, or the script stops.
PATCHES = [
    {
        "file": "best-practice/claude-settings.md",
        "old": '      "Read(.env)",\n      "Read(./secrets/**)",\n      "Bash(curl *)"\n    ],',
        "new": '      "Bash(curl *)",\n      "Read(.env)",\n      "Read(./secrets/**)"\n    ],',
        "why": (
            "Example of `permissions.deny`. The sequence .env, secrets, curl matches the secret-exfiltration "
            "pattern of Paperclip's audit (a false positive: the example forbids those actions). The order of a "
            "deny list does not matter, so curl goes first."
        ),
    },
]

# One-line index of SKILL.md. Key: path relative to the skill folder.
SUMMARIES = {
    "references/best-practice/claude-settings.md": "Referencia completa de `settings.json` (249+ ajustes, 403+ variables de entorno): permisos, hooks, modelo, sandbox, statusline, MCP…, con un ejemplo final completo. Es la más larga: busca la sección.",
    "references/best-practice/claude-cli-startup-flags.md": "Flags de arranque del CLI, subcomandos de primer nivel y variables de entorno de arranque.",
    "references/best-practice/claude-commands.md": "Comandos slash: campos del frontmatter de un command propio y catálogo de los comandos integrados, por categoría.",
    "references/best-practice/claude-skills.md": "Skills: campos del frontmatter de SKILL.md y skills integradas oficiales.",
    "references/best-practice/claude-subagents.md": "Subagents: campos del frontmatter y tipos de agente integrados.",
    "references/best-practice/claude-memory.md": "CLAUDE.md como memoria persistente: cómo escribirlo y cómo se carga en monorepos.",
    "references/best-practice/claude-mcp.md": "Servidores MCP recomendados para el día a día y cómo configurarlos.",
    "references/best-practice/claude-power-ups.md": "Power-ups: lecciones interactivas del CLI sobre funciones poco conocidas (desde v2.1.90).",
    "references/implementation/claude-subagents-implementation.md": "Ejemplo real de subagent (weather-agent) dentro del patrón Command → Agent → Skill.",
    "references/implementation/claude-skills-implementation.md": "Dos skills de ejemplo y sus dos formas de invocación: precargada en un agente o llamada directamente.",
    "references/implementation/claude-commands-implementation.md": "Ejemplo real de command (`/weather-orchestrator`) como punto de entrada del patrón Command → Agent → Skill.",
    "references/implementation/claude-agent-teams-implementation.md": "Agent Teams: varias sesiones de Claude Code coordinadas con una lista de tareas compartida, y en qué se diferencian de los subagents.",
    "references/implementation/claude-scheduled-tasks-implementation.md": "Tareas recurrentes con la skill `/loop` en un intervalo tipo cron.",
    "references/implementation/claude-goal-implementation.md": "Implementación de `/goal`, a partir de un hilo de la comunidad.",
    "references/orchestration-workflow/orchestration-workflow.md": "El patrón Command → Agent (con skill) → Skill paso a paso, con diagramas y el flujo de la demo del tiempo.",
    "references/development-workflows/rpi/rpi-workflow.md": "Flujo RPI (Research → Plan → Implement) con puertas GO/NO-GO; usa los agentes y commands de `rpi/claude-config/`.",
    "references/development-workflows/cross-model-workflow.md": "Flujo cruzado Claude Code + Codex CLI.",
    "references/development-workflows/rpi/claude-config/commands/rpi/research.md": "Command RPI de investigación: viabilidad y decisión GO/NO-GO.",
    "references/development-workflows/rpi/claude-config/commands/rpi/plan.md": "Command RPI de planificación: documentación completa de una funcionalidad.",
    "references/development-workflows/rpi/claude-config/commands/rpi/implement.md": "Command RPI de implementación por fases con puertas de validación.",
    "references/development-workflows/rpi/claude-config/agents/requirement-parser.md": "Agente que extrae requisitos, objetivos y restricciones de una petición.",
    "references/development-workflows/rpi/claude-config/agents/product-manager.md": "Agente PM: de una petición a un PRD con criterios de aceptación y alcance.",
    "references/development-workflows/rpi/claude-config/agents/ux-designer.md": "Agente UX: brief con flujos, estados y anotaciones.",
    "references/development-workflows/rpi/claude-config/agents/senior-software-engineer.md": "Agente ingeniero senior: pasos pequeños y reversibles, con tests y PRs claros.",
    "references/development-workflows/rpi/claude-config/agents/code-reviewer.md": "Agente revisor: corrección, claridad, seguridad y mantenibilidad.",
    "references/development-workflows/rpi/claude-config/agents/technical-cto-advisor.md": "Agente CTO: contrasta las decisiones técnicas con los principios y estándares de ingeniería.",
    "references/development-workflows/rpi/claude-config/agents/constitutional-validator.md": "Agente que valida propuestas frente a los principios («constitución») del proyecto.",
    "references/development-workflows/rpi/claude-config/agents/documentation-analyst-writer.md": "Agente que analiza la documentación existente y escribe docs según las normas del proyecto.",
    "references/reports/claude-agent-command-skill.md": "Agents vs commands vs skills: cuándo usar cada uno.",
    "references/reports/claude-agent-memory.md": "Memoria persistente de los subagents (frontmatter `memory`).",
    "references/reports/claude-global-vs-project-settings.md": "Qué funciones son solo globales (`~/.claude/`) y cuáles tienen versión de proyecto (`.claude/`).",
    "references/reports/claude-skills-for-larger-mono-repos.md": "Cómo descubre y carga Claude Code las skills en monorepos grandes.",
    "references/reports/claude-advanced-tool-use.md": "Patrones avanzados de tool use en la API para gastar menos tokens y latencia y acertar más con las herramientas.",
    "references/reports/claude-agent-sdk-vs-cli-system-prompts.md": "System prompts del Agent SDK frente a los del CLI, y su efecto en la consistencia de las respuestas.",
    "references/reports/claude-usage-and-rate-limits.md": "Límites de uso, rate limits y créditos de uso, y cómo seguir trabajando al llegar al límite.",
    "references/reports/why-harness-is-important.md": "Por qué el harness de Claude Code marca la diferencia frente a «solo prompts».",
    "references/reports/llm-day-to-day-degradation.md": "¿Empeora un LLM de un día para otro con los pesos congelados? Causas demostradas, bugs de infraestructura y sesgos.",
    "references/reports/claude-in-chrome-v-chrome-devtools-mcp.md": "Comparativa de MCP para automatizar el navegador (Claude in Chrome, Chrome DevTools MCP y un tercero).",
    "references/reports/claude-spinner-verbs-and-tips.md": "Los verbos y tips que muestra el spinner del CLI.",
    "references/tips/claude-boris-13-tips-03-jan-26.md": "Boris Cherny (creador de Claude Code): cómo lo usa él, 13 consejos (3-ene-26).",
    "references/tips/claude-boris-10-tips-01-feb-26.md": "10 consejos del equipo de Claude Code, vía Boris Cherny (1-feb-26).",
    "references/tips/claude-boris-12-tips-12-feb-26.md": "12 formas de personalizar Claude Code, de Boris Cherny (12-feb-26).",
    "references/tips/claude-boris-2-tips-10-mar-26.md": "Revisión de código y test-time compute, de Boris Cherny (10-mar-26).",
    "references/tips/claude-boris-2-tips-25-mar-26.md": "Squash merge y distribución del tamaño de los PR, de Boris Cherny (25-mar-26).",
    "references/tips/claude-boris-15-tips-30-mar-26.md": "15 funciones ocultas o poco usadas de Claude Code, de Boris Cherny (30-mar-26).",
    "references/tips/claude-boris-6-tips-16-apr-26.md": "6 consejos para sacar más partido a Opus 4.7, de Boris Cherny (16-abr-26).",
    "references/tips/claude-thariq-tips-17-mar-26.md": "Thariq: cómo usa Anthropic las skills internamente (17-mar-26).",
    "references/tips/claude-thariq-tips-16-apr-26.md": "Thariq: gestión de sesiones, ventana de 1M y compactación (16-abr-26).",
    "references/tutorial/day0.md": "Día 0: instalar Claude Code y autenticarse (sin las guías por sistema operativo).",
    "references/tutorial/day1.md": "Día 1: los tres niveles de uso: prompts, agentes y skills.",
}

INDEX_SECTIONS = [
    ("Guías de referencia", "references/best-practice/"),
    ("Implementaciones de referencia", "references/implementation/"),
    ("Patrón de orquestación Command → Agent → Skill", "references/orchestration-workflow/"),
    ("Workflows de desarrollo", "references/development-workflows/"),
    ("Informes", "references/reports/"),
    ("Tips con fuente (Boris Cherny, Thariq)", "references/tips/"),
    ("Tutorial", "references/tutorial/"),
]

SKILL_FRONTMATTER = f"""---
name: {SKILL_NAME}
description: >-
  Guías de buenas prácticas de Claude Code (adaptadas de shanraisshan/claude-code-best-practice).
  Úsala para configurar o razonar sobre Claude Code: settings.json, permisos, hooks, subagents,
  skills, slash commands, CLAUDE.md y memoria, servidores MCP, flags del CLI, agent teams, /loop y
  /goal; para diseñar flujos de agentes (patrón Command → Agent → Skill, RPI, Claude + Codex); y para
  consultar tips de Boris Cherny y Thariq sobre sesiones, contexto, revisión de código y skills.
tags: [claude-code, best-practices, settings, hooks, subagents, skills, commands, mcp, workflows]
author: Shayan Rais (original); adaptación de JonathanPL
homepage: https://github.com/{UPSTREAM}
---
"""

# --- Paperclip audit (copied from /app/server/src/services/company-skills.ts) -----------
# re.ASCII: in JavaScript (without the u flag) \b only counts ASCII letters, so «evalúa»
# contains the word «eval» for Paperclip. Without re.ASCII, Python would not see it.
REMOTE_EXEC_RE = re.compile(
    r"\b(?:curl|wget)\b[\s\S]{0,160}\|\s*(?:sh|bash)|\b(?:bash|sh)\s+-c\b|\beval\b|\bpython\s+-c\b|\bnode\s+-e\b",
    re.I | re.ASCII,
)
SECRET_EXFIL_RE = re.compile(
    r"\b(?:cat|printenv|env|grep)\b[\s\S]{0,160}(?:\.aws\/credentials|\.ssh\/|\.npmrc|id_rsa|OPENAI_API_KEY|"
    r"ANTHROPIC_API_KEY|API_KEY|TOKEN|SECRET)[\s\S]{0,160}\b(?:curl|wget|nc|netcat|scp)\b",
    re.I | re.ASCII,
)

# --- Content transformations ------------------------------------------------------------
HEADER_RE = re.compile(
    r'<table width="100%">\s*<tr>\s*<td><a href="[^"]*">← Back[^<]*</a></td>\s*'
    r"<td[^>]*>\s*<img[^>]*>\s*</td>\s*</tr>\s*</table>[ \t]*\n?",
    re.S,
)
SHIELD_LINKED_RE = re.compile(r"\[!\[([^\]]*)\]\((https://img\.shields\.io/[^)\s]*)\)\]\(([^)\s]+)\)")
SHIELD_RE = re.compile(r"!\[([^\]]*)\]\((https://img\.shields\.io/[^)\s]*)\)")
A_IMG_RE = re.compile(r'<a\s+href="([^"]*)"[^>]*>\s*(<img\b[^>]*>)\s*</a>', re.S)
HTML_IMG_RE = re.compile(r"<img\b[^>]*>")
MD_IMG_RE = re.compile(r'!\[([^\]]*)\]\(([^)\s]+)(?:\s+"[^"]*")?\)')
MD_LINK_RE = re.compile(r'(?<!!)\[((?:[^\[\]\n]|\[[^\]\n]*\])*)\]\(([^)\s]+)((?:\s+"[^"]*")?)\)')
HTML_HREF_RE = re.compile(r'(<a\s+[^>]*?href=")([^"]+)(")')
FENCE_RE = re.compile(r"^(```|~~~)")
ATTR_RE = re.compile(r'(\w+)\s*=\s*"([^"]*)"')


class Ctx:
    def __init__(self, sha: str, src_root: Path, mapping: dict[str, str]):
        self.sha = sha
        self.src_root = src_root
        self.mapping = mapping
        self.warnings: list[str] = []
        self.rewritten_links = 0


def gh_url(ctx: Ctx, path: str, kind: str = "blob") -> str:
    path = path.strip("/")
    base = f"https://github.com/{UPSTREAM}/{kind}/{ctx.sha}"
    return f"{base}/{urllib.parse.quote(path, safe='/')}" if path else f"https://github.com/{UPSTREAM}/tree/{ctx.sha}"


def raw_url(ctx: Ctx, path: str) -> str:
    return f"https://raw.githubusercontent.com/{UPSTREAM}/{ctx.sha}/{urllib.parse.quote(path.strip('/'), safe='/')}"


def is_external(target: str) -> bool:
    return bool(re.match(r"^(?:[a-z][a-z0-9+.-]*:|#|//)", target, re.I))


def resolve(src_rel: str, target: str) -> str:
    joined = posixpath.normpath(posixpath.join(posixpath.dirname(src_rel), urllib.parse.unquote(target)))
    return "" if joined == "." else joined


def rewrite_target(ctx: Ctx, src_rel: str, target: str) -> str:
    if is_external(target):
        return target
    path, _, anchor = target.partition("#")
    anchor = f"#{anchor}" if anchor else ""
    if not path:
        return target
    resolved = resolve(src_rel, path)
    resolved = LINK_FIXES.get(resolved, resolved)
    if resolved.startswith(".."):
        ctx.warnings.append(f"{src_rel}: link outside the repo ({target}); left unchanged")
        return target
    ctx.rewritten_links += 1
    if resolved in ctx.mapping:
        here = posixpath.dirname(ctx.mapping[src_rel])
        return posixpath.relpath(ctx.mapping[resolved], here) + anchor
    full = ctx.src_root / resolved
    if full.is_dir() or not resolved:
        return gh_url(ctx, resolved, "tree")
    if not full.exists():
        ctx.warnings.append(f"{src_rel}: link to {resolved}, which does not exist in the original")
    return gh_url(ctx, resolved) + anchor


def shield_text(alt: str, url: str) -> str | None:
    """Text for a shields.io badge, or None to drop it."""
    if alt.strip().lower() == "last updated":
        return None
    path = urllib.parse.urlparse(url).path
    content = path.split("/badge/", 1)[-1]
    content = content.replace("--", "\0").replace("__", "\1")
    parts = [p.replace("\0", "-").replace("\1", "_").replace("_", " ") for p in content.split("-")]
    parts = [urllib.parse.unquote(p).strip() for p in parts]
    if len(parts) >= 3:
        return f"{parts[0]} {parts[1]}".strip()
    return parts[0] if parts and parts[0] else alt


def img_attrs(tag: str) -> dict[str, str]:
    return {k.lower(): v for k, v in ATTR_RE.findall(tag)}


def image_replacement(ctx: Ctx, src_rel: str, src: str, alt: str, href: str | None = None) -> str:
    alt = alt.strip() or "imagen"
    if "claude-jumping" in src:
        return ""
    if "!/tags/" in src or "/!/tags/" in src:
        return f"[{alt}]({href})" if href else f"**{alt}**"
    if "img.shields.io" in src:
        text = shield_text(alt, src)
        if text is None:
            return ""
        return f"[{text}]({href})" if href else f"`{text}`"
    img = src if is_external(src) else raw_url(ctx, resolve(src_rel, src))
    out = f"[imagen: {alt}]({img})"
    if href and href != src:
        out += f" ([enlace]({href}))"
    return out


def transform_prose(ctx: Ctx, src_rel: str, text: str) -> str:
    text = SHIELD_LINKED_RE.sub(
        lambda m: "" if shield_text(m.group(1), m.group(2)) is None else f"[{shield_text(m.group(1), m.group(2))}]({m.group(3)})",
        text,
    )
    text = SHIELD_RE.sub(
        lambda m: "" if shield_text(m.group(1), m.group(2)) is None else f"`{shield_text(m.group(1), m.group(2))}`",
        text,
    )

    def a_img(m: re.Match) -> str:
        attrs = img_attrs(m.group(2))
        return image_replacement(ctx, src_rel, attrs.get("src", ""), attrs.get("alt", ""), m.group(1))

    text = A_IMG_RE.sub(a_img, text)
    text = HTML_IMG_RE.sub(
        lambda m: image_replacement(ctx, src_rel, img_attrs(m.group(0)).get("src", ""), img_attrs(m.group(0)).get("alt", "")),
        text,
    )
    text = MD_IMG_RE.sub(lambda m: image_replacement(ctx, src_rel, m.group(2), m.group(1)), text)
    text = MD_LINK_RE.sub(lambda m: f"[{m.group(1)}]({rewrite_target(ctx, src_rel, m.group(2))}{m.group(3)})", text)
    text = HTML_HREF_RE.sub(lambda m: m.group(1) + rewrite_target(ctx, src_rel, m.group(2)) + m.group(3), text)
    # Lines left empty, or holding only <br>, after removing badges.
    text = re.sub(r"(?m)^[ \t]*(?:<br\s*/?>[ \t]*)+$", "", text)
    # A line left with only the version badge: no leading space or trailing <br>.
    text = re.sub(r"(?m)^[ \t]+(`[^`\n]+`)[ \t]*(?:<br\s*/?>)?[ \t]*$", r"\1", text)
    text = re.sub(r"(?m)^(`[^`\n]+`)[ \t]*<br\s*/?>[ \t]*$", r"\1", text)
    return text


def transform(ctx: Ctx, src_rel: str, text: str) -> str:
    text = text.replace("\r\n", "\n")
    text, n = HEADER_RE.subn("", text)
    if "← Back" in text:
        ctx.warnings.append(f"{src_rel}: a «← Back» header was not removed")
    # Apply the transformations only outside fenced code blocks.
    out, chunk, in_fence = [], [], False
    for line in text.split("\n"):
        if FENCE_RE.match(line.lstrip()):
            if not in_fence:
                out.append(transform_prose(ctx, src_rel, "\n".join(chunk)))
                chunk = []
            in_fence = not in_fence
            out.append(line)
            continue
        if in_fence:
            out.append(line)
        else:
            chunk.append(line)
    out.append(transform_prose(ctx, src_rel, "\n".join(chunk)))
    text = "\n".join(out)
    text = re.sub(r"\n{3,}", "\n\n", text).strip() + "\n"
    return add_provenance(ctx, src_rel, text)


def add_provenance(ctx: Ctx, src_rel: str, text: str) -> str:
    note = (
        f"> Original: [`{src_rel}`]({gh_url(ctx, src_rel)}) en {UPSTREAM} (MIT, © Shayan Rais). "
        "Adaptado para Paperclip: sin imágenes ni badges, con los enlaces reescritos.\n"
    )
    if text.startswith("---\n"):
        end = text.find("\n---\n", 4)
        if end != -1:
            cut = end + len("\n---\n")
            return text[:cut] + "\n" + note + "\n" + text[cut:].lstrip("\n")
    lines = text.split("\n")
    if lines and lines[0].startswith("# "):
        return lines[0] + "\n\n" + note + "\n" + "\n".join(lines[1:]).lstrip("\n")
    return note + "\n" + text


# --- SKILL.md --------------------------------------------------------------------------
def build_skill_md(ctx: Ctx, outputs: dict[str, str], upstream_date: str) -> str:
    lines = [
        SKILL_FRONTMATTER,
        "# Claude Code: buenas prácticas",
        "",
        f"Documentación de [{UPSTREAM}](https://github.com/{UPSTREAM}) (MIT, © Shayan Rais), adaptada como skill:",
        "una referencia por documento, sin imágenes ni badges y con los enlaces internos reescritos. Original en el",
        f"commit [`{ctx.sha[:7]}`]({gh_url(ctx, '', 'tree')}) ({upstream_date}).",
        "",
        "## Cómo usarla",
        "",
        "1. Busca en el índice de abajo el documento que responde a tu duda.",
        "2. Abre SOLO esa referencia. Son largas: `claude-settings.md` tiene ~1.480 líneas, así que busca la sección",
        "   (`grep -n`) en vez de leerla entera.",
        "3. Lo que estas guías describen es Claude Code (el CLI). Antes de aplicarlo a otro cliente (OpenCode,",
        "   Paperclip), comprueba que la función existe allí.",
        "4. Las imágenes del original no están copiadas: aparecen como enlaces `[imagen: …]` a GitHub.",
        "",
        "## Índice",
    ]
    for title, prefix in INDEX_SECTIONS:
        entries = sorted(p for p in outputs if p.startswith(prefix))
        if not entries:
            continue
        lines += ["", f"### {title}", ""]
        for p in entries:
            summary = SUMMARIES.get(p)
            if summary is None:
                ctx.warnings.append(f"{p}: no index summary (new in the original?)")
                summary = "(sin resumen)"
            lines.append(f"- [`{p.removeprefix('references/')}`]({p}) — {summary}")
    leftovers = [p for p in outputs if not any(p.startswith(pr) for _, pr in INDEX_SECTIONS)]
    if leftovers:
        lines += ["", "### Otros", ""] + [f"- [`{p}`]({p}) — {SUMMARIES.get(p, '(sin resumen)')}" for p in sorted(leftovers)]
    return "\n".join(lines).rstrip() + "\n"


# --- Validations -----------------------------------------------------------------------
def audit(files: dict[str, bytes]) -> list[str]:
    errors = []
    skill = files.get("SKILL.md", b"").decode("utf-8", "replace")
    if not skill.startswith("---\n") or not re.search(r"(?m)^name:\s*\S", skill.split("\n---", 1)[0]):
        errors.append("SKILL.md: frontmatter without `name`")
    for path, data in files.items():
        if len(data) > MAX_FILE_BYTES:
            errors.append(f"{path}: {len(data)} bytes > 1 MiB")
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            errors.append(f"{path}: not UTF-8")
            continue
        for name, rx in (("remote_fetch_exec", REMOTE_EXEC_RE), ("secret_exfiltration", SECRET_EXFIL_RE)):
            m = rx.search(text)
            if m:
                snippet = text[max(0, m.start() - 40): m.end() + 40].replace("\n", "⏎")
                errors.append(f"{path}: {name} :: …{snippet[:200]}…")
    return errors


def check_links(files: dict[str, bytes]) -> list[str]:
    broken = []
    for path, data in files.items():
        text = data.decode("utf-8")
        in_fence = False
        for line in text.split("\n"):
            if FENCE_RE.match(line.lstrip()):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            for target in [m.group(2) for m in MD_LINK_RE.finditer(line)] + [m.group(2) for m in HTML_HREF_RE.finditer(line)]:
                if is_external(target):
                    continue
                rel = target.split("#", 1)[0]
                if not rel:
                    continue
                dest = posixpath.normpath(posixpath.join(posixpath.dirname(path), urllib.parse.unquote(rel)))
                if dest not in files:
                    broken.append(f"{path} → {target}")
    return broken


# --- Download --------------------------------------------------------------------------
def gh(*args: str) -> str:
    return subprocess.run(["gh", *args], check=True, capture_output=True, text=True).stdout.strip()


def fetch_upstream(ref: str, workdir: Path) -> tuple[str, str, Path]:
    sha = gh("api", f"repos/{UPSTREAM}/commits/{ref}", "--jq", ".sha")
    date = gh("api", f"repos/{UPSTREAM}/commits/{sha}", "--jq", ".commit.committer.date")
    tgz = workdir / "upstream.tgz"
    with open(tgz, "wb") as fh:
        subprocess.run(["gh", "api", f"repos/{UPSTREAM}/tarball/{sha}"], check=True, stdout=fh)
    dest = workdir / "src"
    dest.mkdir()
    with tarfile.open(tgz) as tar:
        tar.extractall(dest, filter="data")
    (top,) = list(dest.iterdir())
    return sha, date, top


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ref", default="main", help="branch, tag or SHA of the original (default: main)")
    ap.add_argument("--source", type=Path, help="already extracted copy of the original (needs --sha)")
    ap.add_argument("--sha", help="SHA of the copy passed in --source")
    ap.add_argument("--check", action="store_true", help="validate only; write nothing")
    args = ap.parse_args()

    with tempfile.TemporaryDirectory(prefix="ccbp-") as tmp:
        if args.source:
            if not args.sha:
                ap.error("--source needs --sha")
            sha, src_root = args.sha, args.source.resolve()
            date = gh("api", f"repos/{UPSTREAM}/commits/{sha}", "--jq", ".commit.committer.date")
        else:
            sha, date, src_root = fetch_upstream(args.ref, Path(tmp))

        sources = sorted(
            str(p.relative_to(src_root))
            for d in INCLUDE_DIRS
            for p in (src_root / d).rglob("*.md")
            if str(p.relative_to(src_root)) not in EXCLUDE
        )
        mapping = {}
        for s in sources:
            dst = PATH_OVERRIDES.get(s, s).replace("/.claude/", "/claude-config/")
            mapping[s] = "references/" + dst
        ctx = Ctx(sha, src_root, mapping)

        outputs: dict[str, str] = {}
        for s in sources:
            text = (src_root / s).read_text(encoding="utf-8")
            for patch in PATCHES:
                if patch["file"] == s:
                    count = text.count(patch["old"])
                    if count != 1:
                        print(f"ERROR: the patch for {s} appears {count} times (expected 1)", file=sys.stderr)
                        return 1
                    text = text.replace(patch["old"], patch["new"])
            outputs[mapping[s]] = transform(ctx, s, text)
        missing_patch = [p["file"] for p in PATCHES if p["file"] not in sources]
        if missing_patch:
            print(f"ERROR: patches for files that no longer exist: {missing_patch}", file=sys.stderr)
            return 1

        skill_md = build_skill_md(ctx, outputs, date[:10])
        files = {"SKILL.md": skill_md.encode("utf-8")} | {k: v.encode("utf-8") for k, v in outputs.items()}

        errors = audit(files)
        broken = check_links(files)
        total = sum(len(v) for v in files.values())
        print(f"Original: {UPSTREAM}@{sha[:7]} ({date})")
        print(f"Files: {len(files)} ({len(outputs)} references + SKILL.md), {total / 1024:.0f} KB")
        print(f"Largest: {max(files, key=lambda k: len(files[k]))} ({max(len(v) for v in files.values()) / 1024:.0f} KB)")
        print(f"Links rewritten: {ctx.rewritten_links}")
        print(f"Broken relative links: {len(broken)}")
        for b in broken:
            print(f"  ✗ {b}")
        print(f"Audit errors: {len(errors)}")
        for e in errors:
            print(f"  ✗ {e}")
        print(f"Warnings: {len(ctx.warnings)}")
        for w in ctx.warnings:
            print(f"  · {w}")
        if errors or broken:
            print("Nothing written.", file=sys.stderr)
            return 1
        if args.check:
            print("--check: nothing written.")
            return 0

        if SKILL_DIR.exists():
            shutil.rmtree(SKILL_DIR)
        for rel, data in files.items():
            dest = SKILL_DIR / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
        (REPO_ROOT / "UPSTREAM.json").write_text(
            json.dumps(
                {
                    "repo": UPSTREAM,
                    "ref": args.ref,
                    "sha": sha,
                    "commit_date": date,
                    "files": len(files),
                    "excluded": sorted(EXCLUDE),
                    "patches": [{"file": p["file"], "why": p["why"]} for p in PATCHES],
                },
                indent=2,
                ensure_ascii=False,
            )
            + "\n",
            encoding="utf-8",
        )
        print(f"Written to {SKILL_DIR.relative_to(REPO_ROOT)}/ and UPSTREAM.json")
        return 0


if __name__ == "__main__":
    sys.exit(main())
