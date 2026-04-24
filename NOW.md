# NOW — agent-ready

> Current focused work. Provides immediate context for the next agent picking up this repo.

## Status

**v0.3.0 — Phase 2.C complete.** 55 tests pass, ruff clean. `fix` / `verify` / `undo` are live.

CLI auto-detects input format across raw text, trace-eval scorecard JSON, synthetic diagnose, and task phrases. The Vercel deployment tool can now be installed, configured, verified, and removed end-to-end.

## What Works Today (Phase 1 + 2.A + 2.C)

- `agent-ready detect --task "deploy my site"` — intent-based, no trace needed.
- `cat session.jsonl | agent-ready detect` — raw trace text, highest recall path.
- `trace-eval run ... --format json | agent-ready detect` — trace-eval scorecard (lower recall — see `docs/INTEGRATION.md § Known Limits`).
- `agent-ready fix --task "deploy my site"` — installs and configures missing capabilities with per-capability approval.
- `agent-ready fix --dry-run --task "deploy my site"` — previews what would happen.
- `agent-ready verify vercel_cli` — checks a capability is actually working.
- `agent-ready undo vercel_cli` — removes what was installed and confirms removal.
- `agent-ready status` / `agent_ready schema` — introspection.
- Python API: `from agent_ready import execute_plan, verify_capability, undo_capability`.

## What Does NOT Work Yet

- ❌ Additional capability modules (github_cli, nodejs, python, etc.) — only `vercel_cli` is implemented.
- ❌ MCP server — Phase 2.D.
- ❌ `trace-eval`-side integration (`install_capability` action type) — optional future work, see `docs/INTEGRATION.md`.

## Immediate Next Steps (in order)

1. **Phase 2.C — Second capability module** — `github_cli` or `nodejs`. Same lifecycle: detect → install → auth → verify → undo. One more capability proves the pattern scales.
2. **Phase 2.D — MCP server** — wrap `detect`, `fix`, `verify`, `undo` as MCP tools for Claude Code, Cursor, Codex. Interface spec in `docs/AGENT_INTERFACE.md`.
3. **Error pattern expansion** — add Windows PowerShell, zsh, permission denied, network timeout variants.

## For Other AI Agents Picking This Up

Start here:
- `AGENT_PICKUP.md` — focused pickup guide, what to do first.
- `docs/INTEGRATION.md` — how we relate to trace-eval v0.5.0.
- `docs/ARCHITECTURE.md` — system design.
- `docs/DESIGN.md` — non-dev UX principles (read before changing any user-facing text).
- `CONTRIBUTING.md` — safety-review block is mandatory for installer PRs.
- `docs/SECURITY_REVIEW.md` — the security policy all installers must follow.

## Resolved Design Decisions (via Phase 2.B Security Review)

- **Sandboxing model for `fix`**: controlled subshell on the user's host. (See `docs/SECURITY_REVIEW.md` § 1)
- **Credential storage**: delegate to each tool's native store; agent-ready never touches credentials. (See `docs/SECURITY_REVIEW.md` § 2)
- **Sudo policy**: never auto-sudo; user-scope installs only; manual sudo if no alternative. (See `docs/SECURITY_REVIEW.md` § 3)
- **Approval cadence**: per-capability (one yes = all steps for that capability only). (See `docs/SECURITY_REVIEW.md` § 6)

## Still Open

- **User-action unblock signal**: stdin line vs. sentinel file (for async agents)? — Phase 2.C uses `input()` for now; MCP server will need a different pattern.
- **Error pattern expansion**: current 9 patterns are narrow (English "command not found" only). Need Windows PowerShell, zsh, permission denied, network timeout variants.
