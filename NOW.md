# NOW — agent-ready

> Current focused work. Replaces no other doc; provides immediate context.

## Status

**Phase 1 — detect path live against a synthetic trace shape.** 28 tests pass, ruff clean. `fix`/`verify`/`undo` are intentional stubs awaiting security review.

**Important reality check:** the real `trace-eval` is at v0.5.0 with a richer JSON output (scorecard + friction_flags) than our `schema/trace.v1.json` declares. Our mapper does NOT yet consume real trace-eval output. This is the Phase 2 top priority — see `docs/INTEGRATION.md`.

## What Works Today

- `agent-ready detect --task "deploy my site"` — plain-English task → Plan. **Most useful path today for non-devs.**
- `agent-ready detect --from <synthetic-diagnose.json>` — works against our internal format (see `tests/fixtures/` for examples).
- `agent-ready detect --json` — machine-readable Plan output.
- `agent-ready status` — lists the 5 Phase 1 capabilities.
- Python API: `from agent_ready import plan_from_task, plan_from_diagnose, render_human`.

## What Does NOT Work Yet

- ❌ Consuming real `trace-eval run <file> --format json` output — needs `agent_ready/adapters/trace_eval.py` (Phase 2, ~0.5–1 day).
- ❌ `fix` / `verify` / `undo` — pending security review of the install path.
- ❌ MCP server — Phase 2.

## Immediate Next Steps (in order)

1. **Commit + push** the Phase 1 scaffold. It's a solid base for Phase 2 agents.
2. **Phase 2.A — integration adapter**: build `agent_ready/adapters/trace_eval.py`. Spec in `docs/INTEGRATION.md`. Estimated 0.5–1 day.
3. **Phase 2.B — security review** of the install path before any `fix` code lands.
4. **Phase 2.C — first capability module**: `agent_ready/capabilities/vercel_cli.py` with real `detect`/`install`/`auth`/`verify`/`undo`.
5. **Phase 2.D — MCP server** wrapping `detect` (and eventually `fix`).

## For Other AI Agents Picking This Up

- `docs/INTEGRATION.md` is the "start here" doc — it names the exact file to create, what input it takes, what output it must produce, and how to test it.
- `docs/EXAMPLES.md` shows the working paths.
- `CONTRIBUTING.md` sets the bar for capability-adding PRs (safety review block is non-negotiable).

## Open Design Questions

- Sandboxing model for `fix`: subshell, container, or trust the user's env?
- User-action unblock signal: stdin line vs. sentinel file?
- Credential storage: OS keychain vs. `.env` vs. delegate to each tool's native store?
