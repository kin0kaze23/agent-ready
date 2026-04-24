# Roadmap

> `agent-ready` and `trace-eval` share a roadmap. Source of truth: [trace-eval/docs/ROADMAP.md](https://github.com/kin0kaze23/trace-eval/blob/main/docs/ROADMAP.md).
> When the two drift, trace-eval wins.

---

## Where We Are

**v0.2.0 — Phase 1 + Phase 2.A complete.** Phase 2.B security review in progress.

## Phase 0 — Contract ✅ Done

- [x] Schemas drafted and stable
- [x] Docs in both repos
- [x] CI green, no implementation code

## Phase 1 — Detection Path ✅ Done

- [x] `agent-ready detect --from diagnose.json` — reads trace-eval output, emits a capability plan.
- [x] `agent-ready detect --task "deploy my site"` — plain-English task detection, no trace needed.
- [x] Capability registry: 5 capabilities (vercel_cli, github_cli, nodejs, python, api_key_config).
- [x] Error pattern catalog: 9 patterns covering command-not-found and auth failures.
- [x] Plan rendering: human-readable + JSON output.
- [x] Auto-detection of input format: raw text / trace-eval scorecard / synthetic diagnose / task phrase.
- [x] 41 tests passing, ruff clean, CI green.

## Phase 2 — Installer Path (in progress)

### Phase 2.A — Input adapters ✅ Done

- [x] `plan_from_text(raw)` — scan any raw log for missing-capability signals.
- [x] `plan_from_trace_eval_json(scorecard)` — consume real trace-eval v0.5.0 scorecard JSON.
- [x] `plan_from_trace_eval_with_trace(scorecard, trace_path)` — higher precision with combined scorecard + raw trace.
- [x] CLI auto-detection of input format on `detect --from` / stdin.

### Phase 2.B — Security review 🟡 In progress

- [x] Security review document drafted (PR #3)
- [ ] Owner approval and merge

### Phase 2.C — First capability module 🔒 Blocked on 2.B

- [ ] `agent_ready/capabilities/vercel_cli.py` — detect, install, auth, verify, undo.
- [ ] Tests against disposable environment.
- [ ] `agent-ready fix --capability vercel_cli` works end-to-end.

### Phase 2.D — MCP server 🔒 After 2.C

- [ ] MCP server exposing `agent_ready.detect`, `agent_ready.fix`, `agent_ready.verify`, `agent_ready.undo`.
- [ ] Integration with Claude Code, Cursor, Codex as native tools.

## Phase 1 Exit Criterion

≥3 alpha users complete one full failed-task → `trace-eval` → `agent-ready fix` → succeeded-retry → `trace-eval` confirms improvement, without manual intervention beyond approvals.

---

## Non-Goals

Same as trace-eval — no hosted service, no SaaS, no multi-tenant registries through Phase 3.
