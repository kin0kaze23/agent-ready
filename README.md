# agent-ready

> Detect what your AI agent is missing. Install it. Get ready. In plain English.

[![CI](https://github.com/kin0kaze23/agent-ready/actions/workflows/ci.yml/badge.svg)](https://github.com/kin0kaze23/agent-ready/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

**Pairs with:** [trace-eval](https://github.com/kin0kaze23/trace-eval) — `trace-eval` finds the gap, `agent-ready` fixes it.

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
# agent-ready 0.2.0 — 5 capabilities in registry:
#   • vercel_cli           Vercel CLI
#   • github_cli           GitHub CLI
#   • nodejs               Node.js
#   • python               Python
#   • api_key_config       API Key Configuration
```

---

## Quick Start

### 1. Detect from a plain-English task (no trace needed)

```bash
agent-ready detect --task "deploy my portfolio to production"
```

```
agent-ready • 1 thing to set up:
  • Vercel CLI — The tool that puts your website on the internet.

Some steps need your input (account signup, sign-in, or an API key).

Next: review with `agent-ready fix --dry-run` before anything is installed.
```

### 2. Detect from a real agent session log

```bash
cat session.log | agent-ready detect
```

Scans the raw text against known error patterns and maps them to missing capabilities. Works with any agent that outputs readable error text.

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
  ┌────────────────┐   diagnose.json   ┌──────────────────┐
  │   trace-eval   │ ─────────────────▶│   agent-ready    │
  │   diagnose     │                   │   detect + fix   │
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

**v0.2.0 — Phase 1 + Phase 2.A complete.** 41 tests passing, CI green.

| Feature | Status |
|---------|--------|
| Capability registry (5 capabilities) | ✅ Live |
| Error pattern detection (9 patterns) | ✅ Live |
| `detect` from task phrase | ✅ Live |
| `detect` from raw trace text | ✅ Live |
| `detect` from trace-eval scorecard | ✅ Live (see [known limits](docs/INTEGRATION.md#known-limits--real-scorecard-precision)) |
| `detect` from synthetic diagnose | ✅ Live |
| `fix` / `verify` / `undo` | 🟡 Security review in progress (PR #3) |
| Real capability installers | 🔒 Blocked on security review merge |
| MCP server | 🔒 Phase 2.D (after installers ship) |

---

## Safety Posture

`agent-ready fix` installs software and writes configuration. It is a HIGH-RISK tool by design.

- **Never installs without approval** — one approval per capability, not one blanket yes.
- **Never stores credentials** — secrets go to the user's keychain / `.env` / the tool's native store.
- **Every action is reversible** — `agent-ready undo <capability>` removes what was installed.
- **Verify after install** — never report success based on a return code alone.

See [SECURITY.md](SECURITY.md) for our full security policy and [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the verification layer design.

---

## Contributing

We welcome contributions! Read [CONTRIBUTING.md](CONTRIBUTING.md) to get started. Every capability-adding PR requires a safety review — see the template.

### Adding a capability

1. Open a [capability-gap issue](https://github.com/kin0kaze23/agent-ready/issues/new?template=capability-gap.yml).
2. Add the capability entry to `schema/capabilities.v1.json`.
3. Add matching error patterns to `schema/error-patterns.v1.json`.
4. Write tests, run `pytest tests/ -q` and `ruff check .`.
5. Open a PR with the required `## Safety review` block.

See [docs/EXAMPLES.md § Extending the registry](docs/EXAMPLES.md#7-extending-the-registry-for-contributors--ai-agents) for the full walkthrough.

---

## Roadmap

Source of truth: [docs/ROADMAP.md](docs/ROADMAP.md). High-level priorities:

- **Phase 2.C** — Real installers (starting with `vercel_cli`): detect → install → auth → verify → undo.
- **Phase 2.D** — MCP server so AI agents can call agent-ready as native tools.
- **Phase 2.B+** — More capabilities, more error patterns, broader OS support.

---

## License

MIT — see [LICENSE](LICENSE).
