# NOW — agent-ready

> Current focused work. Provides immediate context for the next agent picking up this repo.

## Strategic Context

This repo is one engine in the **AI Workstation Suite** (Pulse · trace-eval · agent-ready). The suite-level strategy lives at `/Users/jonathannugroho/Developer/PersonalProjects/AI_WORKSTATION_SUITE.md`.

**agent-ready's role:** the capability layer — detect missing tools/keys/skills, install them with per-action approval, verify they work, and undo cleanly. The long-term moat is the community capability manifest (§6 of the strategy doc).

## Status

**v0.3.0 — Phase 2.C + 2.D complete.** 67 tests pass, ruff clean. MCP server live.

AI agents can now call agent-ready natively via MCP (`vibedev.ready.detect`, `fix`, `verify`, `undo`, `status`). The CLI remains available for humans who want to type commands.

## What Works Today

- **MCP Server** (primary interface): 5 tools exposed to AI agents via stdio
- `agent-ready detect --task "deploy my site"` — intent-based, no trace needed
- `agent-ready fix --task "deploy my site"` — installs and configures with approval
- `agent-ready fix --dry-run --task "deploy my site"` — previews what would happen
- `agent-ready verify vercel_cli` — checks a capability is working
- `agent-ready undo vercel_cli` — removes what was installed and confirms removal
- `agent-ready status` — lists all tools in the registry
- Python API: `from agent_ready import execute_plan, verify_capability, undo_capability`

## What Does NOT Work Yet

- ❌ Additional capability installers — only `vercel_cli` has real code. `github_cli`, `nodejs`, `python` are in the schema but have no Python modules.
- ❌ Error pattern expansion — still only 9 English "command not found" patterns.
- ❌ Shared state (`~/.config/vibedev/state.json`) and audit log.
- ❌ Bootstrap script (`curl get.vibedev.sh | sh`).

## Immediate Next Steps (per strategy doc §10)

1. **Ship 3 more capability installers** — `github_cli`, `nodejs`, `python` (P0, days 0–30)
2. **Expand error patterns** — zsh, PowerShell, permission denied, OAuth expiry (P0)
3. **Vocabulary sweep** — replace forbidden words across CLI output (P0, half-day)
4. **Shared state + audit log** — `~/.config/vibedev/` coordination with Pulse and trace-eval (P1)

## For Other AI Agents Picking This Up

Start here:
- `AI_WORKSTATION_SUITE.md` (parent directory) — the strategic frame
- `AGENT_PICKUP.md` — focused pickup guide
- `docs/ARCHITECTURE.md` — system design
- `docs/DESIGN.md` — non-dev UX principles (read before changing any user-facing text)
- `CONTRIBUTING.md` — safety-review block is mandatory for installer PRs
- `docs/SECURITY_REVIEW.md` — the security policy all installers must follow

## Resolved Design Decisions (via Phase 2.B Security Review)

- **Sandboxing model for `fix`**: controlled subshell on the user's host. (See `docs/SECURITY_REVIEW.md` § 1)
- **Credential storage**: delegate to each tool's native store; agent-ready never touches credentials. (See `docs/SECURITY_REVIEW.md` § 2)
- **Sudo policy**: never auto-sudo; user-scope installs only; manual sudo if no alternative. (See `docs/SECURITY_REVIEW.md` § 3)
- **Approval cadence**: per-capability (one yes = all steps for that capability only). (See `docs/SECURITY_REVIEW.md` § 6)

## Still Open

- **User-action unblock signal**: MCP server uses non-interactive mode; the human sees approval prompts through their AI agent's UI, not through agent-ready directly.
- **Error pattern expansion**: current 9 patterns are narrow (English "command not found" only). Need Windows PowerShell, zsh, permission denied, network timeout variants.
