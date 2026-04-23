# Integration with trace-eval (v0.5.0)

> How `agent-ready` relates to the real `trace-eval` today, what the adapter covers, and what still needs to close the loop.

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

Neither tool can do the other's job without this bridge.

---

## What trace-eval Does (v0.5.0)

- 5 deterministic judges: `reliability`, `efficiency`, `retrieval`, `tool_discipline`, `context`.
- Emits `friction_flags` with IDs like `reliability_errors`, `efficiency_high_tokens`, `tool_redundant`.
- Emits `RemediationAction`s from a fixed catalog: `reduce_retries`, `reduce_prompt_size`, `fix_errors`, `switch_profile`, `reduce_tool_calls`, `improve_retrieval`, `add_ci_gate`.
- `--apply-safe` generates config/CI artifacts for user review; does not install software.

trace-eval **does not** install CLIs, create accounts, or manage API keys. That's deliberately out of scope.

---

## What agent-ready Does Today (Phase 2.A live)

- **Auto-detects input format** — raw text / JSONL / trace-eval scorecard JSON / synthetic diagnose / task phrase.
- Matches against `schema/error-patterns.v1.json` (canonical here — trace-eval uses a different, event-based model).
- Emits a `Plan` — the sequence of install / account / auth / verify steps.
- `fix` / `verify` / `undo` are intentional stubs pending security review.

### The three input surfaces

| Input | How | When to use |
|-------|-----|------------|
| **Raw trace text** | `cat session.jsonl \| agent-ready detect` | Simplest. Works with any agent surface that emits readable error text. **Highest recall today.** |
| **trace-eval scorecard** | `trace-eval run ... --format json \| agent-ready detect` | When you already ran trace-eval and want to double-dip. Note: scorecards summarize errors by event index, so pattern matching has lower recall than raw text. See "Known Limits" below. |
| **Task phrase** | `agent-ready detect --task "deploy my site"` | Preemptive. No trace needed. Matches against `related_tasks` on each capability. |

---

## Known Limits — Real Scorecard Precision

`trace-eval`'s scorecard `friction_flags[].suggestion` often reads like:

> "Review 90 error(s) at event indices [23, 32, 61, ...]"

The **actual error text** (`command not found: vercel`) lives in the trace events themselves, referenced by index. The scorecard-only adapter (`plan_from_trace_eval_json`) will match patterns that appear verbatim in suggestions, but will miss patterns that are only in the underlying trace.

Two ways to get full precision:

1. **`plan_from_trace_eval_with_trace(scorecard, trace_path)`** (Python API) — combines scorecard with the raw trace file.
2. **Raw-text adapter** (CLI) — skip the scorecard entirely: `cat trace.jsonl | agent-ready detect`. Higher recall with one less moving part.

---

## Further Cross-Repo Integration (Phase 2.B+)

### Option A — trace-eval adds an `install_capability` action type

Cleanest architecture. `trace_eval.remediation.ACTION_TYPES` gains a new entry that emits `agent-ready`-compatible capability IDs. trace-eval's `loop --apply-safe` could invoke `agent-ready fix` for the user.

**Scope:** modify trace-eval's `remediation.py`, add reliability-judge hook that triggers when command-not-found patterns are detected. Coordinated PR in both repos.

### Option B — agent-ready reads trace-eval's event stream directly

Add an adapter that reads trace-eval's canonical event schema (from `trace_eval/schema.py`) and scans individual event payloads for error patterns. More robust than the scorecard path.

**Scope:** `agent_ready/adapters/trace_eval_events.py`. Requires parsing trace-eval's JSONL event format.

### Option C — status quo

Keep the raw-text adapter as the primary path. It works today and has the highest recall.

---

## How to Pick This Up (for Agents Continuing This Work)

Phase 2.A is **complete**. The next priorities are:

1. **Phase 2.B — Security review** of the install path. Required before any `fix` code lands. See `docs/ARCHITECTURE.md § Safety`.
2. **Phase 2.C — First capability module**: `agent_ready/capabilities/vercel_cli.py` implementing `detect`, `install`, `auth`, `verify`, `undo`. One capability end-to-end before adding more.
3. **Phase 2.D — MCP server** wrapping `detect` (and eventually `fix`).

---

## Status Summary

| Component | Status |
|-----------|--------|
| Capability registry (5 capabilities) | ✅ Working |
| Pattern catalog | ✅ Working |
| `plan_from_task` (task-phrase → plan) | ✅ Working |
| `plan_from_diagnose` (synthetic schema → plan) | ✅ Working |
| **Text adapter (raw trace → plan)** | ✅ **Phase 2.A — live** |
| **trace-eval scorecard adapter** | ✅ **Phase 2.A — live** (with documented recall limit) |
| CLI auto-detection of input format | ✅ Live |
| `fix` / `verify` / `undo` | ❌ Stubs — awaiting security review (Phase 2.B) |
| First capability module (e.g. `vercel_cli`) | ❌ Phase 2.C |
| MCP server | ❌ Phase 2.D |
