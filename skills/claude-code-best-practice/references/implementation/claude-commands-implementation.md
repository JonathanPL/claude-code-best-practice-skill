# Commands Implementation

> Original: [`implementation/claude-commands-implementation.md`](https://github.com/shanraisshan/claude-code-best-practice/blob/0bbb72f00514e9a8bf16bf8a1de04a5695e8f904/implementation/claude-commands-implementation.md) en shanraisshan/claude-code-best-practice (MIT, © Shayan Rais). Adaptado para Paperclip: sin imágenes ni badges, con los enlaces reescritos.

---

[Implemented](#weather-orchestrator)

The weather orchestrator command is implemented in this repo as the entry point of the **Command → Agent → Skill** architecture pattern, demonstrating how commands orchestrate multi-step workflows.

---

## Weather Orchestrator

**File**: [`.claude/commands/weather-orchestrator.md`](https://github.com/shanraisshan/claude-code-best-practice/blob/0bbb72f00514e9a8bf16bf8a1de04a5695e8f904/.claude/commands/weather-orchestrator.md)

```yaml
---
description: Fetch weather data for Dubai and create an SVG weather card
model: haiku
---

# Weather Orchestrator Command

Fetch the current temperature for Dubai, UAE and create a visual SVG weather card.

## Workflow

### Step 1: Ask User Preference
Use the AskUserQuestion tool to ask the user whether they want the temperature
in Celsius or Fahrenheit.

### Step 2: Fetch Weather Data
Use the Agent tool to invoke the weather agent:
- subagent_type: weather-agent
- prompt: Fetch the current temperature for Dubai, UAE in [unit]...

### Step 3: Create SVG Weather Card
Use the Skill tool to invoke the weather-svg-creator skill:
- skill: weather-svg-creator

...
```

The command orchestrates the entire workflow: it asks the user for their temperature unit preference, invokes the `weather-agent` via the Agent tool, and then invokes the `weather-svg-creator` skill via the Skill tool.

---

## **How to Use**

```bash
$ claude
> /weather-orchestrator
```

---

## **How to Implement**

Ask Claude to create one for you — it will generate the markdown file with YAML frontmatter and body in `.claude/commands/<name>.md`

---

[Orchestration Workflow](https://github.com/shanraisshan/claude-code-best-practice#orchestration-workflow)

The weather orchestrator is the **Command** in the Command → Agent → Skill orchestration pattern. It serves as the entry point — handling user interaction (temperature unit preference), delegating data fetching to the `weather-agent`, and invoking the `weather-svg-creator` skill for visual output.

<p align="center">
  [imagen: Command Skill Agent Architecture Flow](https://raw.githubusercontent.com/shanraisshan/claude-code-best-practice/0bbb72f00514e9a8bf16bf8a1de04a5695e8f904/orchestration-workflow/orchestration-workflow.svg)
</p>

| Component | Role | This Repo |
|-----------|------|-----------|
| **Command** | Entry point, user interaction | [`/weather-orchestrator`](https://github.com/shanraisshan/claude-code-best-practice/blob/0bbb72f00514e9a8bf16bf8a1de04a5695e8f904/.claude/commands/weather-orchestrator.md) |
| **Agent** | Fetches data with preloaded skill (agent skill) | [`weather-agent`](https://github.com/shanraisshan/claude-code-best-practice/blob/0bbb72f00514e9a8bf16bf8a1de04a5695e8f904/.claude/agents/weather-agent.md) with [`weather-fetcher`](https://github.com/shanraisshan/claude-code-best-practice/blob/0bbb72f00514e9a8bf16bf8a1de04a5695e8f904/.claude/skills/weather-fetcher/SKILL.md) |
| **Skill** | Creates output independently (skill) | [`weather-svg-creator`](https://github.com/shanraisshan/claude-code-best-practice/blob/0bbb72f00514e9a8bf16bf8a1de04a5695e8f904/.claude/skills/weather-svg-creator/SKILL.md) |
