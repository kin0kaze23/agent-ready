# Roadmap

> `agent-ready` and `trace-eval` share a roadmap. Source of truth: [trace-eval/docs/ROADMAP.md](https://github.com/kin0kaze23/trace-eval/blob/main/docs/ROADMAP.md).

This file is a local summary. When the two drift, trace-eval wins.

---

## Where We Are

**Phase 0 — Contract.** Schemas drafted, docs in both repos, CI green, but no implementation code.

## What Unblocks Phase 1

1. `trace-eval` emits `schema/trace.v1.json` from real Claude Code traces.
2. Alpha data tells us which 3 capabilities to implement first (current bet: Vercel CLI, GitHub CLI, Node.js).
3. Security review of the install path (sandboxing, rollback, credential handling).

## Phase 1 Targets for agent-ready

- [ ] `agent-ready detect --from diagnose.json` — reads trace-eval output, emits a capability plan.
- [ ] Capability modules: `vercel_cli`, `github_cli`, one of `{nodejs, python}`.
- [ ] Each capability implements `detect`, `install`, `auth`, `verify`, `undo`.
- [ ] `agent-ready fix --dry-run` prints the plan; `agent-ready fix` executes it.
- [ ] User-action steps work over stdin (for agent piping) and over a simple prompt (for CLI users).

## Phase 1 Exit Criterion

≥3 alpha users complete one full failed-task → `trace-eval` → `agent-ready fix` → succeeded-retry → `trace-eval` confirms improvement, without manual intervention beyond approvals.

---

## Non-Goals

Same as trace-eval — no hosted service, no SaaS, no multi-tenant registries through Phase 3.
