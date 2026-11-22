# Squash Merging & PR Size Distribution — Tips from Boris Cherny

> Original: [`tips/claude-boris-2-tips-25-mar-26.md`](https://github.com/shanraisshan/claude-code-best-practice/blob/0bbb72f00514e9a8bf16bf8a1de04a5695e8f904/tips/claude-boris-2-tips-25-mar-26.md) en shanraisshan/claude-code-best-practice (MIT, © Shayan Rais). Adaptado para Paperclip: sin imágenes ni badges, con los enlaces reescritos.

A summary of insights shared by Boris Cherny ([@bcherny](https://x.com/bcherny)), creator of Claude Code, on March 25, 2026.

---

## 1/ 266 Contributions in a Single Day — Always Squash

Boris shared his GitHub contribution graph showing **266 contributions on March 24th** — from **141 PRs, always squashed** with a median of **118 lines** per PR.

- Squash merging combines all branch commits into a single commit on the target branch — keeping history clean and linear
- Each PR = one commit makes it easy to revert entire features and simplifies `git bisect`
- At high-velocity AI-assisted workflows (141 PRs/day), squash is the pragmatic choice — individual "fix lint", "try this" commits within a branch are noise

[imagen: Boris Cherny — 266 contributions, always squashed](https://raw.githubusercontent.com/shanraisshan/claude-code-best-practice/0bbb72f00514e9a8bf16bf8a1de04a5695e8f904/tips/assets/boris-26-3-25/1.png) ([enlace](https://x.com/bcherny/status/2038552880018538749))

---

## 2/ PR Size Distribution — Keep PRs Small

Boris shared the size distribution across those 141 PRs, totaling **45,032 lines changed** (additions + deletions):

| Metric | Lines (add+del) | Meaning |
|--------|---------------:|---------|
| **p50** | **118** | Median PR size — half of all PRs were 118 lines or fewer |
| p90 | 498 | 90% of PRs were under 500 lines |
| **p99** | **2,978** | Only ~1 PR exceeded ~3K lines |
| min | 2 | Smallest PR — a quick 2-line fix |
| max | 10,459 | Largest single PR — likely a migration or generated code |

- A **median of 118 lines** means most PRs are focused and reviewable, even at 141 PRs/day
- The distribution is heavily right-skewed — the occasional large PR is inevitable (bulk renames, migrations), but the norm is tight
- Small PRs reduce merge conflict risk, are easier to review, and pair perfectly with squash merging for clean reverts

[imagen: Boris Cherny — PR size distribution table](https://raw.githubusercontent.com/shanraisshan/claude-code-best-practice/0bbb72f00514e9a8bf16bf8a1de04a5695e8f904/tips/assets/boris-26-3-25/2.png) ([enlace](https://x.com/bcherny/status/2038552880018538749))

---

## Sources

- [Boris Cherny (@bcherny) on X — March 25, 2026](https://x.com/bcherny)
