# NOW — agent-ready

> Current focused work. Provides immediate context for the next agent picking up this repo.

## Status

**Phase 2.B in review.** Security review PR (#3) is open against `main`. Phase 2.C unblocked after merge.
41 tests pass, ruff clean, v0.2.0. CLI auto-detects input format across raw text, trace-eval scorecard JSON, synthetic diagnose, and task phrases.

## What Works Today (Phase 1 + 2.A)

- `agent-ready detect --task "deploy my site"` — intent-based, no trace needed.
- `cat session.jsonl | agent-ready detect` — raw trace text, highest recall path.
- `trace-eval run ... --format json | agent-ready detect` — trace-eval scorecard (lower recall — see `docs/INTEGRATION.md § Known Limits`).
- `agent-ready detect --from tests/fixtures/diagnose_vercel_missing.json` — synthetic shape still supported.
- `agent-ready detect --json` — machine-readable Plan for agents.
- `agent-ready status` / `agent-ready schema` — introspection.
- Python API: `from agent_ready import plan_from_text, plan_from_task, plan_from_trace_eval_json, render_human`.

## What Does NOT Work Yet

- ⏳ `fix` / `verify` / `undo` — security review drafted (PR #3), awaiting owner approval and merge.
- ❌ First capability module (real installer code) — Phase 2.C (unblocked after PR #3 merges).
- ❌ MCP server — Phase 2.D.
- ❌ `trace-eval`-side integration (`install_capability` action type) — optional future work, see `docs/INTEGRATION.md`.

## Immediate Next Steps (in order, for the next agent)

1. **Merge PR #3** — owner approval needed for `docs/SECURITY_REVIEW.md`.
2. **Phase 2.C — First capability module** — `agent_ready/capabilities/vercel_cli.py`. Implement `detect`, `install`, `auth`, `verify`, `undo` following the security decisions in `docs/SECURITY_REVIEW.md`. Add tests against a disposable environment. One capability fully working is worth more than five half-working.
3. **Phase 2.D — MCP server** — wrap `detect` (and later `fix`) as MCP tools. Interface spec in `docs/AGENT_INTERFACE.md`.

## For Other AI Agents Picking This Up

Start here:
- `AGENT_PICKUP.md` — focused pickup guide, what to do first.
- `docs/INTEGRATION.md` — how we relate to trace-eval v0.5.0.
- `docs/ARCHITECTURE.md` — system design.
- `docs/DESIGN.md` — non-dev UX principles (read before changing any user-facing text).
- `CONTRIBUTING.md` — safety-review block is mandatory for installer PRs.

## Resolved Design Questions (via Phase 2.B Security Review)

- **Sandboxing model for `fix`**: controlled subshell on the user's host. (See `docs/SECURITY_REVIEW.md` § 1)
- **Credential storage**: delegate to each tool's native store; agent-ready never touches credentials. (See `docs/SECURITY_REVIEW.md` § 2)
- **Approval cadence**: per-capability (one yes = all steps for that capability only). (See `docs/SECURITY_REVIEW.md` § 6)

## Still Open

- **User-action unblock signal**: stdin line vs. sentinel file (for async agents)? — deferred to Phase 2.C implementation.
