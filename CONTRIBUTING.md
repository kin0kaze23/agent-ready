# Contributing to agent-ready

## Before You Start

1. Read `README.md` and `docs/ARCHITECTURE.md`.
2. Read `docs/DESIGN.md` — this product is for non-devs, and that constrains almost every design choice.
3. Check open issues, especially `capability-gap` — those are backed by real alpha data.

## Development

```bash
pip install -e ".[dev]"
pytest tests/ -q
ruff check .
```

## Adding a Capability

A capability is a thing that can be detected, installed, authenticated, and verified. To add one:

1. Open an issue using the `capability-gap` template.
2. Add an entry to `docs/CAPABILITY_REGISTRY.md`.
3. Add/confirm the matching error pattern in `schema/error-patterns.v1.json` (mirrored from `trace-eval`).
4. Add an implementation module under `agent_ready/capabilities/<id>.py` with `detect`, `install`, `auth`, `verify` functions.
5. Add a test that runs `detect → install → verify` against a disposable environment (CI uses a container).
6. Update `docs/CAPABILITY_REGISTRY.md`.

## Schema Changes

`schema/trace.v1.json` and `schema/error-patterns.v1.json` are **mirrored from trace-eval**. Do not edit them here — open the PR in `trace-eval` first, then sync here in the same PR batch.

## Safety Review Required For

Any PR that:
- runs `sudo`, `brew install`, `npm install -g`, `curl | sh`, or any network installer,
- writes a file outside the repo,
- reads or writes a credential,
- opens a browser for auth,

must include a `## Safety review` section in the PR description that states:
- what state is mutated,
- how it is reversed,
- what happens if the step is interrupted.

## What Not to Commit

- Internal working docs, sprint notes, AI assistant transcripts.
- Build artifacts (`dist/`, `build/`, `__pycache__/`, `.venv/`).
- Any credentials, tokens, API keys, or personal paths.
