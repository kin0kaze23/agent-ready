# agent-ready

> Detect what your AI agent is missing. Install it. Get ready. In plain English.

[![CI](https://github.com/kin0kaze23/agent-ready/actions/workflows/ci.yml/badge.svg)](https://github.com/kin0kaze23/agent-ready/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

**Pairs with:** [trace-eval](https://github.com/kin0kaze23/trace-eval) — `trace-eval` scores the session, `agent-ready` fixes the gaps.

---

## What It Does

Your AI agent tried to do something and couldn't — it's missing a tool, not signed into an account, or lacks an API key. `agent-ready` detects the gap, asks you once for approval, and handles the rest. You never touch a terminal.

```
Agent: "I tried to deploy your site but couldn't — the deployment tool isn't
        installed and you're not signed in. I can set both up in about 2
        minutes. Want me to?"
You:    "Yes"
Agent:  *installs Vercel CLI*
        *opens the signup page for you*
        "I've opened Vercel in your browser. Click 'Continue with GitHub'
        and then come back here."
You:    *signs up*
Agent:  *links the project* "All set. Deploying now..."
        "Live at sarah.vercel.app."
```

That's the entire product. The agent carries the weight; you make decisions.

---

## Who It's For

**Primary:** Non-developers using Claude Code, Cursor, Codex, Gemini — anyone whose AI agent keeps hitting "missing thing" walls.

**Secondary:** Developers who want a single, auditable layer between their agents and the OS.

---

## Installation

```bash
pip install agent-ready
```

Or from source:

```bash
git clone https://github.com/kin0kaze23/agent-ready.git
cd agent-ready
pip install -e ".[dev]"
```

Verify it works:

```bash
agent-ready status
# agent-ready 0.4.0 — 5 tools:
#   • The tool that puts your website on the internet.
#   • The tool that connects your code to GitHub.
#   • The tool that runs JavaScript code on your computer.
#   • The tool that runs Python code on your computer.
#   • Secret keys so your app can connect to outside services.
```

---

## Quick Start

### 1. Detect from a plain-English task (no session log needed)

```bash
agent-ready detect --task "deploy my portfolio to production"
```

```
I found 1 thing to set up:
  • The tool that puts your website on the internet.

A few steps need your help (like signing up or signing in). I'll guide you through each one.

Run `agent-ready fix --task "..."` to set everything up.
```

### 2. Detect from a real agent session log

```bash
cat session.log | agent-ready detect
```

Scans the raw text against known error patterns and maps them to missing tools. Works with any agent that outputs readable error text.

### 3. Detect from trace-eval output

```bash
trace-eval run session.jsonl --format json | agent-ready detect
```

### 4. Machine-readable output (for AI agents)

```bash
cat session.log | agent-ready detect --json
```

See [docs/EXAMPLES.md](docs/EXAMPLES.md) for the full usage guide and [docs/AGENT_INTERFACE.md](docs/AGENT_INTERFACE.md) for how AI agents drive agent-ready.

---

## The Loop (with trace-eval)

```
  Agent tries a task → fails
        │
        ▼
  ┌────────────────┐   session report   ┌──────────────────┐
  │   trace-eval   │ ─────────────────▶│   agent-ready    │
  │   score        │                   │   detect + fix   │
  └────────────────┘                   └────────┬─────────┘
                                                │
                                                ▼
                                       User approves each step
                                       → install → account → auth → verify
                                                │
                                                ▼
                                       Agent retries → trace-eval confirms
                                       score improvement
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the full system design and [docs/DESIGN.md](docs/DESIGN.md) for the non-dev UX principles.

---

## Current Status

**v0.4.0 — MCP server live, generic executor active.** 82 tests passing, CI green.

| Feature | Status |
|---------|--------|
| Tool library (5 tools) | ✅ Live |
| Error pattern detection (9 patterns) | ✅ Live |
| `detect` from task phrase | ✅ Live |
| `detect` from session log | ✅ Live |
| `detect` from trace-eval report | ✅ Live |
| `fix` / `verify` / `undo` | ✅ Live — generic executor, schema-driven |
| MCP server (5 tools) | ✅ Live — `vibedev.ready.*` namespace |

---

## Safety Posture

`agent-ready fix` installs software and writes configuration. It is a HIGH-RISK tool by design.

- **Never installs without approval** — one approval per tool, not one blanket yes.
- **Never stores credentials** — secrets go to the user's keychain / `.env` / the tool's native store.
- **Every action is reversible** — `agent-ready undo <tool>` removes what was installed.
- **Verify after install** — never report success based on a return code alone.

See [SECURITY.md](SECURITY.md) for our full security policy and [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the verification layer design.

---

## Contributing

We welcome contributions! Read [CONTRIBUTING.md](CONTRIBUTING.md) to get started. Every tool-adding PR requires a safety review — see the template.

### Adding a tool

1. Open a [capability-gap issue](https://github.com/kin0kaze23/agent-ready/issues/new?template=capability-gap.yml).
2. Add the tool entry to `schema/capabilities.v1.json`.
3. Add matching error patterns to `schema/error-patterns.v1.json`.
4. Write tests, run `pytest tests/ -q` and `ruff check .`.
5. Open a PR with the required `## Safety review` block.

No Python code needed — the generic executor reads from schema data automatically.

See [docs/EXAMPLES.md § Extending the registry](docs/EXAMPLES.md#7-extending-the-registry-for-contributors--ai-agents) for the full walkthrough.

---

## Roadmap

Source of truth: [docs/ROADMAP.md](docs/ROADMAP.md). High-level priorities:

- **Expand error patterns** — zsh, PowerShell, permission denied, OAuth expiry (9 → 30+)
- **Bootstrap script** — `curl get.vibedev.sh | sh` one-command install for the full suite
- **Shared state** — `~/.config/vibedev/` coordination with Pulse and trace-eval

---

## License

MIT — see [LICENSE](LICENSE).
