# agent-ready

> Detect what your AI agent is missing. Install it. Get ready. In plain English.

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

**Primary:** Non-developers using Claude Code, Cursor, Codex, Gemini, OpenClaw — anyone whose AI agent keeps hitting "missing thing" walls.

**Secondary:** Developers who want a single, auditable layer between their agents and the OS.

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

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the full picture and [docs/DESIGN.md](docs/DESIGN.md) for the non-dev UX principles.

---

## Status: **Phase 1 read-only path — live**

`detect` is implemented end-to-end: it reads trace-eval `diagnose.json` (or a plain-English task phrase) and returns a capability Plan. 28 tests pass, ruff clean. `fix` / `verify` / `undo` are intentionally stubbed pending the security review of the install path — see `docs/ARCHITECTURE.md § Safety`.

Try it:

```bash
agent-ready detect --task "deploy my portfolio"
agent-ready status
```

> **Heads-up:** the real `trace-eval` (v0.5.0) emits a richer JSON shape than our mapper reads today. Piping `trace-eval run ... --format json | agent-ready detect` requires a thin adapter that's the **Phase 2.A task** — see [docs/INTEGRATION.md](docs/INTEGRATION.md). Until that lands, use `--task` mode or the synthetic fixtures under `tests/fixtures/`.

See [docs/EXAMPLES.md](docs/EXAMPLES.md) for the full usage flow and [docs/CAPABILITY_REGISTRY.md](docs/CAPABILITY_REGISTRY.md) for the 5 Phase 1 capabilities.

---

## Agent-Facing Surface

Two users, two surfaces:

| User | Interface | Contract |
|------|-----------|----------|
| The AI agent | `agent-ready detect --from diagnose.json` (and future MCP server) | `schema/trace.v1.json` (input), `schema/capability.v1.json` (output) |
| The human | Approval prompts, plain-English progress, one-line success/failure | English |

See [docs/AGENT_INTERFACE.md](docs/AGENT_INTERFACE.md).

---

## Safety Posture

`agent-ready fix` installs software and writes configuration. It is a HIGH-RISK tool by design.

- **Never installs without approval** — one approval per capability, not one blanket yes.
- **Never stores credentials** — secrets go to the user's keychain / `.env` / the tool's native store.
- **Every action is reversible** — `agent-ready undo <capability>` removes what was installed.
- **Verify after install** — never report success based on a return code alone.

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md#safety-verification-layer).

---

## License

MIT — see [LICENSE](LICENSE).
