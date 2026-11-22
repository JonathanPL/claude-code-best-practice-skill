# Scheduled Tasks Implementation

> Original: [`implementation/claude-scheduled-tasks-implementation.md`](https://github.com/shanraisshan/claude-code-best-practice/blob/0bbb72f00514e9a8bf16bf8a1de04a5695e8f904/implementation/claude-scheduled-tasks-implementation.md) en shanraisshan/claude-code-best-practice (MIT, © Shayan Rais). Adaptado para Paperclip: sin imágenes ni badges, con los enlaces reescritos.

---

[Implemented](#loop-demo)

The `/loop` skill is used to schedule recurring tasks on a cron interval. Below is a demo of `/loop 1m "tell current time"` — a simple recurring task that fires every minute.

---

## Loop Demo

### 1. Scheduling the Task

<p align="center">
  [imagen: /loop 1m tell current time — scheduling and cron setup](https://raw.githubusercontent.com/shanraisshan/claude-code-best-practice/0bbb72f00514e9a8bf16bf8a1de04a5695e8f904/implementation/assets/impl-loop-1.png)
</p>

`/loop 1m "tell current time"` parses the interval (`1m` → every 1 minute), creates a cron job, and confirms the schedule. Key notes:

- Cron's minimum granularity is **1 minute** — `1m` maps to `*/1 * * * *`
- Recurring tasks **auto-expire after 3 days**
- Jobs are **session-scoped** — they live in memory only and stop when Claude exits
- Cancel anytime with `cron cancel <job-id>`

---

### 2. Loop in Action

<p align="center">
  [imagen: Recurring task firing every minute](https://raw.githubusercontent.com/shanraisshan/claude-code-best-practice/0bbb72f00514e9a8bf16bf8a1de04a5695e8f904/implementation/assets/impl-loop-2.png)
</p>

The task fires every minute, running `date` and reporting the current time. Each iteration triggers async **UserPromptSubmit** and **Stop** hooks — the same hook system used throughout this repo for sound notifications.

---

## **How to Use**

```bash
$ claude
> /loop 1m "tell current time"
> /loop 5m /simplify
> /loop 10m "check deploy status"
```

---

## **How to Implement**

`/loop` is a built-in Claude Code skill — no setup required. It uses the cron tools (`CronCreate`, `CronList`, `CronDelete`) under the hood to manage recurring schedules.
