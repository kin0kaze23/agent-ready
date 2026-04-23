# Integration with trace-eval (v0.5.0)

> Honest accounting of how `agent-ready` relates to the real `trace-eval` today, and what still needs to be built.

---

## Division of Labor

`trace-eval` and `agent-ready` are **complementary**, not redundant:

| Layer | trace-eval | agent-ready |
|-------|-----------|-------------|
| Audience | Developers using agents | Non-developers using agents |
| Input | Raw agent trace (JSONL, various formats) | Trace text / trace-eval output / task phrase |
| Output | 5-dimensional scorecard + friction flags + remediation actions | Capability plan (installs, accounts, auth, keys) |
| Remediation scope | Prompt engineering, scoring profile, CI gate, fix errors in code | Install tools, create accounts, handle auth, paste API keys |
| Action safety | Most actions require approval; `--apply-safe` for config-only | All installs require approval; no blanket yes |

Neither tool can do the other's job without this gap.

---

## What trace-eval Does (v0.5.0)

- 5 deterministic judges: `reliability`, `efficiency`, `retrieval`, `tool_discipline`, `context`.
- Emits `friction_flags` with IDs like `reliability_errors`, `efficiency_high_tokens`, `tool_redundant`.
- Emits `RemediationAction`s from a fixed catalog: `reduce_retries`, `reduce_prompt_size`, `fix_errors`, `switch_profile`, `reduce_tool_calls`, `improve_retrieval`, `add_ci_gate`.
- `--apply-safe` generates config/CI artifacts for user review; does not install software.

trace-eval **does not** install CLIs, create accounts, or manage API keys. That's deliberately out of scope.

---

## What agent-ready Does Today (Phase 1)

- Reads a **simplified** trace-eval-shaped JSON (via `mapper.plan_from_diagnose`).
- Matches each error entry's `maps_to_capability` or `pattern_id` against the capability registry.
- Emits a `Plan` — the sequence of install / account / auth / verify steps needed.
- Can also be driven by a plain-English task phrase (`mapper.plan_from_task`).
- `fix` / `verify` / `undo` are intentional stubs pending security review.

---

## The Gap — What Phase 2 Must Close

The mapper reads a JSON shape that **does not match real trace-eval v0.5.0 output**.

### Real trace-eval output (abbreviated)

```json
{
  "total_score": 28.29,
  "dimension_scores": {"reliability": 0.0, "efficiency": 30.0, ...},
  "friction_flags": [
    {"id": "reliability_errors", "severity": "medium",
     "dimension": "reliability", "event_index": 23,
     "suggestion": "Review 90 error(s) at event indices [...]"}
  ],
  ...
}
```

### What agent-ready's mapper currently expects

```json
{
  "schema_version": "1.0",
  "score": 70,
  "verdict": "blocked_by_missing_capability",
  "errors": [
    {"pattern_id": "cmd_not_found_vercel", "maps_to_capability": "vercel_cli", ...}
  ]
}
```

### Phase 2 — Bridge Plan

Build `agent_ready/adapters/trace_eval.py`:

1. **Input**: real trace-eval scorecard JSON.
2. **Extract raw error lines** from the trace events referenced by `friction_flags[].event_index`.
3. **Match** those lines against `schema/error-patterns.v1.json` (agent-ready's catalog).
4. **Emit** the simplified shape our mapper already consumes.

Alternative: extend trace-eval with a new `RemediationAction` type (`install_capability`) that emits pattern IDs agent-ready understands. Needs coordinated PR.

---

## The Simplest Usable Path for Non-Devs (near-term)

Until the adapter exists, the realistic flow is:

```bash
# User's agent session produces a trace file session.jsonl
# The agent (or user) pipes the raw trace text to agent-ready:
cat session.jsonl | agent-ready detect --from -   # (requires the adapter work above)

# OR — use task-intent mode, which works today:
agent-ready detect --task "deploy my portfolio"
```

The `--task` path is fully functional today and is the primary value delivery for non-devs who haven't even run their agent yet: predict what will be missing, offer to set it up before the failure.

---

## How to Pick This Up (for the Next Agent in OpenCode)

1. Read this file and `docs/ARCHITECTURE.md`.
2. Read `trace_eval/schema.py` and `trace_eval/report.py` in the trace-eval repo to understand the real JSON shape.
3. Build `agent_ready/adapters/trace_eval.py`.
4. Add fixture: run `trace-eval run <sample> --format json` against one of its own examples and save the output under `tests/fixtures/trace_eval_scorecard_*.json`.
5. Add test: `plan = from_trace_eval_json(fixture)` produces the expected capability set.
6. Update `agent-ready detect --from <file>` to auto-detect real vs simplified format.
7. Remove the "draft" banner from `schema/trace.v1.json` once reconciled.

Estimated effort: **0.5–1 day** for a focused agent.

---

## Status Summary

| Component | Status |
|-----------|--------|
| Capability registry (5 capabilities) | ✅ Working |
| Pattern catalog | ✅ Working |
| `plan_from_task` (task-phrase → plan) | ✅ Working |
| `plan_from_diagnose` (synthetic schema → plan) | ✅ Working |
| **Adapter for real trace-eval output** | ❌ **Phase 2 task** |
| `fix` / `verify` / `undo` | ❌ Stubs — awaiting security review |
| MCP server | ❌ Phase 2 |
