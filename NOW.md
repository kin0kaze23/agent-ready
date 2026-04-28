# NOW — agent-ready

> Current focused work. Provides immediate context for the next agent picking up this repo.

## Strategic Context

This repo is one engine in the **AI Workstation Suite** (Pulse · trace-eval · agent-ready). The suite-level strategy lives at `/Users/jonathannugroho/Developer/PersonalProjects/AI_WORKSTATION_SUITE.md`.

**agent-ready's role:** the tool library — detect missing tools/keys/skills, install them with per-action approval, verify they work, and undo cleanly. The long-term moat is the community tool manifest (§6 of the strategy doc).

## Status

**v0.5.0 — 36 error patterns, 100% detection on real-world errors.** 82 tests pass, ruff clean.

Detection works for Mac, Linux, and Windows users across bash, zsh, and PowerShell. All 5 tools in the library work via the schema-driven generic executor. MCP server exposes 5 tools via `vibedev.ready.*` namespace.

## What Works Today

- **Detection**: 36 error patterns covering command-not-found, auth errors, network errors, rate limits, version mismatches, permission errors, SSL errors, Docker errors, and git errors
- **Installation**: Generic executor — all lifecycle functions driven from schema data, zero Python per tool
- **5 tools functional**: vercel_cli, github_cli, nodejs, python, api_key_config
- **MCP Server**: 5 tools (`detect`, `fix`, `verify`, `undo`, `status`) via stdio transport
- **CLI**: Clean vocabulary, plain English throughout
- **Undo**: Reversible installations with removal verification
- **Security**: Per-tool approval, no sudo, no credential storage, sandboxed execution

## What Does NOT Work Yet

- ❌ Shared state (`~/.config/vibedev/state.json`) and audit log
- ❌ Bootstrap script (`curl get.vibedev.sh | sh`)
- ❌ Credential-flow guidance (browser signup detection, .env creation)
- ❌ Pre-flight check (`agent-ready check` — scan all tools before starting)

## Immediate Next Steps

1. **Bootstrap script** — `curl get.vibedev.sh | sh` installs all three suite products (P0)
2. **Pre-flight check** — `agent-ready check` scans environment before agent starts working (P0)
3. **Shared state + audit log** — `~/.config/vibedev/` coordination with Pulse and trace-eval (P1)
4. **More tools** — docker, supabase, bun (P1)

## For Other AI Agents Picking This Up

Start here:
- `AI_WORKSTATION_SUITE.md` (parent directory) — the strategic frame
- `AGENT_PICKUP.md` — focused pickup guide
- `docs/ARCHITECTURE.md` — system design
- `docs/DESIGN.md` — non-dev UX principles (read before changing any user-facing text)
- `CONTRIBUTING.md` — safety-review block is mandatory for installer PRs
- `docs/SECURITY_REVIEW.md` — the security policy all installers must follow

## Resolved Design Decisions

- **Sandboxing model for `fix`**: controlled subshell on the user's host. (See `docs/SECURITY_REVIEW.md` § 1)
- **Credential storage**: delegate to each tool's native store; agent-ready never touches credentials. (See `docs/SECURITY_REVIEW.md` § 2)
- **Sudo policy**: never auto-sudo; user-scope installs only; manual sudo if no alternative. (See `docs/SECURITY_REVIEW.md` § 3)
- **Approval cadence**: per-tool (one yes = all steps for that tool only). (See `docs/SECURITY_REVIEW.md` § 6)
- **Schema IS implementation**: generic executor reads lifecycle commands from schema — zero Python per new tool.

## Still Open

- **User-action unblock signal**: MCP server uses non-interactive mode; the human sees approval prompts through their AI agent's UI, not through agent-ready directly.
- **Error pattern expansion**: 36 patterns cover ~80% of common errors. Edge cases (custom shells, rare package managers) still need coverage.
