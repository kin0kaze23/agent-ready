# agent-ready — Architecture & Integration Design

> **Product:** Detect what your AI agent is missing. Install it. Guide the user through setup.
> **Pair:** [trace-eval](https://github.com/kin0kaze23/trace-eval) — evaluates sessions, finds errors.
> **Together:** trace-eval diagnoses what went wrong. agent-ready fixes why it went wrong.

---

## The User Story (Non-Dev First)

Sarah is a designer who uses Claude Code to build her portfolio. She asks Claude to deploy it. Claude fails — it doesn't have Vercel CLI, isn't authenticated, and has no project config. Sarah doesn't know what any of that means.

**Without agent-ready:** Claude tells Sarah "install Vercel CLI" and gives terminal commands. Sarah is lost. She gives up.

**With agent-ready:** Claude detects the gap, runs agent-ready, and guides Sarah through a simple setup flow. Sarah clicks "yes" to prompts. Everything gets configured. Claude retries. It works.

This is the entire product. **Make the agent handle the complexity so the user doesn't have to.**

---

## How trace-eval and agent-ready Work Together

```
User task: "Deploy my portfolio"
    │
    ▼
┌─────────────────────────────────────────┐
│  AI Agent (Claude Code, Cursor, etc.)   │
│  Tries to deploy → fails repeatedly     │
└────────────────┬────────────────────────┘
                 │
    ┌────────────┴─────────────┐
    │                          │
    ▼                          ▼
┌──────────────┐      ┌──────────────────┐
│ trace-eval   │      │ (agent detects   │
│ --json       │      │  "command not     │
│              │      │   found" errors)  │
│ Score: 22/100│      │                  │
│ 12 errors:   │      └────────┬─────────┘
│ "command not │               │
│  found: vercel"│             │
└──────┬───────┘               │
       │                       │
       └───────────┬───────────┘
                   │
                   ▼
       ┌───────────────────────┐
       │ agent-ready detect    │
       │                       │
       │ Missing capabilities: │
       │ ✗ Vercel CLI          │
       │ ✗ Vercel account      │
       │ ✗ Project linked      │
       └───────────┬───────────┘
                   │
                   ▼
       ┌───────────────────────┐
       │ agent-ready fix       │
       │                       │
       │ Guided setup flow:    │
       │ 1. Install CLI → ✓    │
       │ 2. Create account → ✓ │
       │ 3. Link project → ✓   │
       └───────────┬───────────┘
                   │
                   ▼
       ┌───────────────────────┐
       │ Agent retries task    │
       │ Deploy succeeds       │
       └───────────┬───────────┘
                   │
                   ▼
       ┌───────────────────────┐
       │ trace-eval --json     │
       │                       │
       │ Score: 89/100 ✓       │
       │ Clean deployment      │
       └───────────────────────┘
```

---

## Core Architecture

### 1. Capability Registry

A structured database of tools, services, and capabilities that AI agents commonly need.

```yaml
capabilities:
  - id: vercel_cli
    name: Vercel CLI
    category: deployment
    detect:
      command: vercel --version
      exit_code: 0
    install:
      mac: brew install vercel-cli
      linux: npm install -g vercel
    requires_account: true
    account_url: https://vercel.com/signup
    requires_auth: true
    auth_command: vercel login
    errors_that_reveal_missing:
      - pattern: "command not found: vercel"
      - pattern: "vercel: command not found"
```

### 2. Error Pattern Mapper

Maps trace-eval error patterns to missing capabilities.

**Input from trace-eval:** `{"score": 22, "error_summary": {"unknown": 12}}`
**Output:** `[{"capability": "vercel_cli", "confidence": 0.95}]`

### 3. Setup Orchestrator

Interactive flows that guide users through capability setup. For non-devs, the agent handles all terminal work. The user only sees:
1. **"Here's what's missing"** — plain English
2. **"Want me to set it up?"** — approval prompt
3. **"Step 1 of 3: Installing Vercel CLI..."** — progress
4. **"Done! Your agent can now deploy."** — confirmation

### 4. Agent Protocol Updater

After setup, the agent's capability list is updated so it knows what it can now do.

### 5. Verification Layer

Before reporting success, verify everything actually works.

---

## Non-Dev UX Principles

1. **Zero terminal exposure** — The agent handles all commands.
2. **Plain English only** — No "CLI", "auth token", "MCP". Use "tool", "login", "connection".
3. **Progressive disclosure** — Show one step at a time.
4. **Safe defaults** — Ask before installing.
5. **Clear progress** — "Step 2 of 4: Creating your Vercel account..."
6. **Undo available** — "Want to remove what we just set up?"

---

## Phase 1 Scope (Data-Driven)

Phase 1 is built from trace-eval alpha data. **Phase 1 will cover the top 3-5 missing capabilities from alpha data.** Not everything. The most common ones.

---

## Development Guidelines for AI Agents

1. **Start with the capability registry.** The registry is the foundation.
2. **Build detect before fix.** Detecting what's missing is easier than installing it.
3. **Test with real error patterns.** Use trace-eval example traces.
4. **Design for the agent, not the terminal.** The primary user is another AI agent.
5. **Keep the CLI minimal.** The real product is the agent-facing API.
