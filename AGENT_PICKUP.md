# Agent Pickup Guide — agent-ready

> **Read this first.** You're an AI agent being spawned into this repo to continue development. Everything below is oriented to getting you productive in 5 minutes.

## TL;DR — What This Repo Is

`agent-ready` detects what a user's AI agent is **missing from its environment** (CLIs, accounts, API keys) and guides a **non-developer** through installing and configuring it. Plain English; the agent does the work, the user clicks approvals.

Pairs with `trace-eval` (scoring / friction analysis) — together they form a diagnose → remediate loop. `trace-eval` fixes agent behavior. `agent-ready` fixes the user's environment.

## Current State (as of 2026-04-23)

- **v0.2.0.** Phase 1 + Phase 2.A are live. 41 tests pass. CI green.
- `detect` works against: raw trace text, trace-eval scorecard JSON, synthetic diagnose, task phrase.
- `fix` / `verify` / `undo` are **intentional stubs** pending security review.

## Your Task (Pick One)

### Task A — Phase 2.B: Security Review (blocker for any installer code)

**Deliverable:** `docs/SECURITY_REVIEW.md` answering:

1. **Sandboxing model** — does `fix` run installers in a subshell, a container, or directly on the user's host? Trade-offs?
2. **Credential storage** — where do API keys go? OS keychain, `.env`, each tool's native store? Never in agent-ready's own state.
3. **Sudo policy** — when, if ever, do we `sudo`? How do we ask the user first?
4. **Rollback guarantees** — if `install` fails halfway, what state does the system end in? How does `undo` prove the removal worked?
5. **Interruption handling** — if the user Ctrl+C's mid-install, what's the recovery?
6. **Approval cadence** — per-capability (one yes = all steps for that capability), per-session, or per-step?

Format: answer each question as a section with a chosen approach, a rationale, and a concrete implementation sketch (what files / what shape of code).

**Estimated effort:** 0.5 day of focused analysis. No code changes yet — this is the gate that lets Phase 2.C begin.

### Task B — Phase 2.C: First Capability Module (blocked on Task A landing)

**Deliverable:** `agent_ready/capabilities/vercel_cli.py` implementing:
- `detect() -> bool` — already installed? (use `vercel --version`)
- `install()` — run the install command for the current OS.
- `auth()` — run `vercel login` if not authed.
- `verify() -> bool` — `vercel whoami` succeeds.
- `undo()` — reverse the install.

Plus tests in `tests/test_capability_vercel.py`. Prefer subprocess tests that verify *command strings and ordering*, not actual installs (which can't run in CI).

**Scope guardrails:** one capability fully working. Do not add a second until Vercel ships end-to-end. Study `schema/capabilities.v1.json` entry for `vercel_cli` — it already has the commands and verify shape.

### Task C — Phase 2.D: MCP Server

**Deliverable:** `agent_ready/mcp/` exposing tools `agent_ready.detect`, `agent_ready.fix`, `agent_ready.verify`, `agent_ready.undo`. Phase 2.D is only useful once Phase 2.C ships a real installer.

### Task D — `trace-eval` cross-repo PR

See `docs/INTEGRATION.md § Further Cross-Repo Integration`. Option A (add `install_capability` action type to `trace_eval/remediation.py`) is the cleanest architectural move but is optional — raw text piping already works end-to-end.

## Non-Negotiables

1. **Read `docs/DESIGN.md` before touching any user-facing text.** Non-dev UX is the whole product.
2. **Never commit `fix` code without a completed Phase 2.B security review document.** Hard gate.
3. **Ruff + pytest must pass.** Pre-commit hook enforces this.
4. **Plain-English only in user-facing output.** No "CLI", "MCP", "auth token" — use "tool", "sign-in", "secret key".
5. **Approval per capability, not blanket.** Never `yes-to-all`.
6. **Never store credentials in the repo or in agent-ready's own state.** Delegate to OS keychain / `.env` / the tool.

## Fast Orientation

```
agent-ready/
├── AGENT_PICKUP.md         ← you are here
├── NOW.md                  ← current work state (more detail than this file)
├── README.md               ← product overview
├── CHANGELOG.md            ← what shipped when
├── CONTRIBUTING.md         ← contributor rules; safety-review block is mandatory
├── docs/
│   ├── ARCHITECTURE.md     ← system design
│   ├── DESIGN.md           ← non-dev UX principles
│   ├── INTEGRATION.md      ← how we relate to trace-eval v0.5.0
│   ├── EXAMPLES.md         ← usage
│   ├── AGENT_INTERFACE.md  ← agent-facing surface (CLI + future MCP)
│   ├── CAPABILITY_REGISTRY.md
│   └── ROADMAP.md
├── schema/                 ← JSON contracts (canonical)
├── agent_ready/
│   ├── adapters/           ← input surfaces (text, trace_eval, patterns)
│   ├── mapper.py           ← pattern hits → Plan
│   ├── registry.py         ← capability registry loader
│   ├── plan.py             ← Plan renderers (human + JSON)
│   ├── models.py           ← dataclasses
│   └── cli.py              ← the entrypoint
└── tests/                  ← 41 tests + fixtures
```

## Verify Your Environment Before You Start

```bash
cd ~/Developer/PersonalProjects/agent-ready
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest tests/ -q           # expect: 41 passed
ruff check .               # expect: All checks passed!
agent-ready status         # expect: 5 capabilities listed
```

If any of those fail, **stop and file an issue**. Do not proceed until green.

## When You Commit

- Conventional commits: `feat:` / `fix:` / `docs:` / `chore:`.
- Pre-commit hook will block: internal working docs, secret shapes, missing `plain_english`.
- Every `agent_ready/capabilities/*.py` PR needs a `## Safety review` block per `CONTRIBUTING.md`.
- Never `--no-verify`. If the hook fails, fix the underlying issue.

## Handoff Back

When you finish your task:
1. Update `NOW.md` with new status and next-agent notes.
2. Update `CHANGELOG.md` with what you shipped.
3. Bump version in `pyproject.toml` and `__init__.py` if user-visible behavior changed.
4. Commit + push + make sure CI is green.
5. Leave `AGENT_PICKUP.md` pointing at the next task.
