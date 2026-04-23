# agent-ready — Agent Rules

> For AI agents working on this repo.

## Repo Map

```
README.md             product overview
CONTRIBUTING.md       contributor rules (capabilities, safety review, tests)
LICENSE               MIT
pyproject.toml        package: agent-ready, module: agent_ready
agent_ready/          implementation (Phase 1+)
tests/                pytest suite
docs/
  ARCHITECTURE.md     system design
  DESIGN.md           non-dev UX
  CAPABILITY_REGISTRY.md  Phase 1 capability set
  AGENT_INTERFACE.md  how AI agents call agent-ready
  ROADMAP.md          local summary (source of truth: trace-eval)
schema/               internal contracts (all canonical in agent-ready)
  capability.v1.json       JSON-Schema for registry entries
  capabilities.v1.json     the actual Phase 1 registry
  error-patterns.v1.json   regex catalog (missing-capability detection)
  trace.v1.json            simplified input format (DRAFT — see docs/INTEGRATION.md)
```

## Before You Edit

1. Read `README.md`, `docs/ARCHITECTURE.md`, and `docs/DESIGN.md`.
2. Every capability-adding PR needs a **Safety review** block — see `CONTRIBUTING.md`.
3. **Read `docs/INTEGRATION.md`** to understand how agent-ready relates to the real trace-eval (v0.5.0) — there's an adapter gap to close in Phase 2.

## Repo Hygiene

- Only `README.md`, `CONTRIBUTING.md`, `LICENSE` at root. All other docs go in `docs/`.
- Never commit: `dist/`, `build/`, `__pycache__/`, `.venv/`, `.DS_Store`, `*.egg-info/`.
- Never commit secrets or credentials — even fake ones (they get copy-pasted).

## Development

```bash
pip install -e ".[dev]"
pytest tests/ -q
ruff check .
```

## Safety Posture

`agent-ready fix` runs installers. It is always HIGH-RISK lane. Enforce:

- **Approval per capability**, not blanket.
- **No network install without `--dry-run` first**.
- **Every install has an `undo`**.
- **Never `sudo` without explicit user consent**.
- **Never store credentials in-repo state**.

## Phase 1 Gate

Implementation is gated on real alpha data from `trace-eval`. Capability modules land one at a time (start with `vercel_cli`), each with full detect/install/auth/verify/undo + tests.
