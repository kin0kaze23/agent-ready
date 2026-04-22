# agent-ready

> Detect what your AI agent is missing. Install it. Get ready.

**Pair with:** [trace-eval](https://github.com/kin0kaze23/trace-eval) — evaluate your agent, then make it ready.

## What It Does (Planned)

```
$ agent-ready check
Missing for deployment tasks:
  ✗ vercel CLI (not installed)
  ✗ GitHub CLI (not authenticated)
  ✗ Doppler (no project linked)

Run `agent-ready fix` to set everything up.
```

## Status: **Pre-alpha — scaffold only**

This repo exists as a placeholder. No implementation yet.
Phase 1 will be built based on real data from trace-eval alpha users.

## Relationship to trace-eval

| Tool | Purpose | When to use |
|------|---------|-------------|
| **trace-eval** | Diagnose what went wrong | After an agent session |
| **agent-ready** | Fix what's missing | Before an agent session |

Agents use both:
1. `trace-eval --json` → score is 26/100, 46 errors
2. `agent-ready detect` → missing: vercel CLI, GitHub auth
3. `agent-ready fix` → install, login, authorize
4. Agent retries → `trace-eval --json` → score is 82/100

## Roadmap

| Phase | What | Trigger |
|-------|------|---------|
| **0 (now)** | Scaffold only | — |
| **1** | Error-to-gap mapping | After trace-eval alpha data |
| **2** | Guided setup flows | After Phase 1 validation |
| **3** | Agent protocol self-upgrade | After Phase 2 validation |

## License

MIT
