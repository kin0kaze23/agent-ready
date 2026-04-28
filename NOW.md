# NOW — agent-ready

> Current focused work. Provides immediate context for the next agent picking up this repo.

## Strategic Context

This repo is one engine in the **AI Workstation Suite** (Pulse · trace-eval · agent-ready). The suite-level strategy lives at `/Users/jonathannugroho/Developer/PersonalProjects/AI_WORKSTATION_SUITE.md`.

**agent-ready's role:** the tool library — detect missing tools/keys/skills, install them with per-action approval, verify they work, and undo cleanly. The long-term moat is the community tool manifest (§6 of the strategy doc).

## Status

**v0.4.0 — MCP server live, generic executor active, vocabulary clean.** 82 tests pass, ruff clean.

AI agents call agent-ready natively via MCP (`vibedev.ready.*` namespace). All 5 tools in the library work via the schema-driven generic executor — adding a new tool = JSON entry, zero Python code.

## What Works Today

- **MCP Server** (primary interface): 5 tools — `detect`, `fix`, `verify`, `undo`, `status`
- **Generic executor**: all lifecycle functions driven from schema data — no per-tool Python code
- **5 tools functional**: vercel_cli, github_cli, nodejs, python, api_key_config
- `agent-ready detect --task "deploy my site"` — plain English, no session log needed
- `agent-ready fix --task "deploy my site"` — installs and configures with approval
- `agent-ready fix --dry-run --task "deploy my site"` — previews without running
- `agent-ready verify <tool>` — checks a tool is working
- `agent-ready undo <tool>` — removes what was installed and confirms removal
- `agent-ready status` — lists all tools with install status
- Python API: `from agent_ready import execute_plan, verify_capability, undo_capability`

## What Does NOT Work Yet

- ❌ Error pattern expansion — still only 9 English "command not found" patterns.
- ❌ Shared state (`~/.config/vibedev/state.json`) and audit log.
- ❌ Bootstrap script (`curl get.vibedev.sh | sh`).
- ❌ Credential-flow guidance (browser signup detection, .env creation).

## Immediate Next Steps (per strategy doc §10)

1. **Expand error patterns** — zsh, PowerShell, permission denied, OAuth expiry (9 → 30+). P0.
2. **Bootstrap script** — `curl get.vibedev.sh | sh` installs all three suite products. P0.
3. **Shared state + audit log** — `~/.config/vibedev/` coordination with Pulse and trace-eval. P1.

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
- **Approval cadence**: per-tool (one yes = all steps for that tool only). (See `docs/SECURITY_REVIEW.md` § 6)
- **Schema IS implementation**: generic executor reads lifecycle commands from schema — zero Python per new tool.

## Still Open

- **User-action unblock signal**: MCP server uses non-interactive mode; the human sees approval prompts through their AI agent's UI, not through agent-ready directly.
- **Error pattern expansion**: current 9 patterns are narrow (English "command not found" only). Need Windows PowerShell, zsh, permission denied, network timeout variants.
