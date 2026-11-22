# Code Review & Test Time Compute — Tips from Boris Cherny

> Original: [`tips/claude-boris-2-tips-10-mar-26.md`](https://github.com/shanraisshan/claude-code-best-practice/blob/0bbb72f00514e9a8bf16bf8a1de04a5695e8f904/tips/claude-boris-2-tips-10-mar-26.md) en shanraisshan/claude-code-best-practice (MIT, © Shayan Rais). Adaptado para Paperclip: sin imágenes ni badges, con los enlaces reescritos.

A summary of insights shared by Boris Cherny ([@bcherny](https://x.com/bcherny)), creator of Claude Code, on March 10, 2026.

---

## 1/ Introducing Code Review

New in Claude Code: **Code Review**. A team of agents runs a deep review on every PR.

- Built for Anthropic's own team first — code output per engineer is up **200% this year**, and reviews were the bottleneck
- Boris has been using it for a few weeks and found it catches many real bugs he would not have noticed otherwise
- When a PR opens, Claude dispatches a team of agents to hunt for bugs

[imagen: Boris Cherny announcing Code Review](https://raw.githubusercontent.com/shanraisshan/claude-code-best-practice/0bbb72f00514e9a8bf16bf8a1de04a5695e8f904/tips/assets/boris-26-3-10/0.png) ([enlace](https://x.com/bcherny/status/2031089411820228645))

---

## 2/ Test Time Compute & Multiple Context Windows

Roughly, the more tokens you throw at a coding problem, the better the result. Boris calls this **test time compute**.

- Using **separate context windows** makes the result even better — this is what makes subagents work, and why one agent can cause bugs and another (using the same exact model) can find them
- Similar to engineering teams: if Boris causes a bug, his coworker reviewing the code might find it more reliably than he can
- In the limit, agents will probably write perfect bug-free code — until then, **multiple uncorrelated context windows** tends to be a good approach

[imagen: Boris Cherny on test time compute](https://raw.githubusercontent.com/shanraisshan/claude-code-best-practice/0bbb72f00514e9a8bf16bf8a1de04a5695e8f904/tips/assets/boris-26-3-10/1.png) ([enlace](https://x.com/bcherny/status/2031151689219321886))

---

## Sources

- [Boris Cherny (@bcherny) on X — March 10, 2026](https://x.com/bcherny)
