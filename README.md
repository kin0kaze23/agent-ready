# agent-ready

> Detect what your AI agent is missing. Install it. Get ready.

**Pair with:** [trace-eval](https://github.com/kin0kaze23/trace-eval) — evaluate your agent's sessions.

---

## What It Does

When your AI agent can't complete a task because it's missing tools, accounts, or configuration — agent-ready detects the gap, installs what's needed, and guides you through setup. All in plain English. No terminal commands required.

```
User: "Deploy my portfolio to production"
Agent: *tries, fails* "I'm missing some tools. Let me check what you need..."
       *runs agent-ready detect*
       "To deploy, you need 3 things. I can set them up:
        1. Install Vercel CLI (the deployment tool)
        2. Create a Vercel account
        3. Link your project
        Want me to set everything up?"
User: "Yes"
       *installs, configures, verifies*
       "All set! Deploying your site now..."
       *succeeds*
```

---

## How It Works with trace-eval

| Tool | Purpose | When |
|------|---------|------|
| **trace-eval** | Diagnose what went wrong | After an agent session |
| **agent-ready** | Fix what's missing | Before or during a task |

The complete loop:
1. Agent tries a task → fails
2. `trace-eval --json` → detects error patterns
3. `agent-ready detect` → maps errors to missing capabilities
4. User approves setup → `agent-ready fix` → installs, configures, verifies
5. Agent retries → succeeds
6. `trace-eval --json` → confirms improvement

---

## Target Users

**Primary:** Non-developers who use AI agents (Claude Code, Codex, Gemini, Cursor, OpenClaw, etc.) but don't know terminal commands, package managers, or how to set up development tools.

**Secondary:** Developers who want a quick way to detect and fix missing capabilities across their agent workflows.

---

## Status

**Pre-alpha — scaffold only.** Phase 1 will be built based on real data from trace-eval alpha users.

See [ARCHITECTURE.md](ARCHITECTURE.md) for the full system design.
See [DESIGN.md](DESIGN.md) for the non-dev UX design.
See [CAPABILITY_REGISTRY.md](CAPABILITY_REGISTRY.md) for the capability data structure.

---

## Roadmap

| Phase | What | Trigger |
|-------|------|---------|
| **0 (now)** | Scaffold + design docs | — |
| **1** | Error-to-capability mapping + 3-5 capability setup flows | After trace-eval alpha data |
| **2** | Full setup orchestrator + verification layer | After Phase 1 validation |
| **3** | Agent protocol self-upgrade + task intent detection | After Phase 2 validation |

---

## For AI Agents Working on This Repo

When implementing agent-ready:

1. **Read ARCHITECTURE.md first** — understand how trace-eval and agent-ready work together
2. **Read DESIGN.md** — understand the non-dev UX principles
3. **Read CAPABILITY_REGISTRY.md** — understand the data structure
4. **Start with detection** — build `agent-ready detect` before `agent-ready fix`
5. **Implement one capability end-to-end** — Vercel CLI is the best starting point
6. **Test with real traces** — use trace-eval example traces to test the error mapper
7. **Design for the agent, not the terminal** — the primary interface is JSON for AI agents

**Never commit:** internal working documents, build artifacts, or credentials.
**Always ask before installing** — safe defaults, user approval required.
**Verify after setup** — never assume installation worked.

---

## License

MIT
