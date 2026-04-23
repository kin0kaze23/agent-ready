# OpenCode Agent Prompt — agent-ready

> Paste this into your OpenCode session when initializing an agent in this repo.

---

## Prompt (Lane A — Phase 2.B Security Review)

You are an AI coding agent working on the `agent-ready` repo. Your task is issue **#2 — Phase 2.B Security Review**.

**Read first** (in order):
1. `AGENT_PICKUP.md`
2. `docs/ARCHITECTURE.md`
3. `docs/DESIGN.md`
4. `docs/INTEGRATION.md`
5. `CONTRIBUTING.md` (pay attention to the `## Safety review` block requirement)
6. Issue #2 itself via `gh issue view 2`

**Your deliverable:** a new file `docs/SECURITY_REVIEW.md` answering all 7 questions in issue #2 with: chosen approach, rationale, concrete implementation sketch (what files, what shape of code).

**Work on a branch:** `phase-2b/security-review`.

**Non-negotiables:**
- No code changes in this PR — review doc only.
- Follow non-dev UX principles in `docs/DESIGN.md` — plain English everywhere.
- Never `--no-verify`. Pre-commit hook must pass.
- Ruff + pytest must stay green (should be unaffected since it's doc-only).
- Conventional commit style (`docs: add security review for Phase 2.B install path`).
- PR description must include a `## Safety review` block summarizing your decisions.

**Scope guardrails:**
- Do NOT modify `agent_ready/**`, `tests/**`, `schema/**`, or `.github/**`.
- Do NOT start Phase 2.C — that is a separate task blocked on this one landing.
- If you find issues in other docs while researching, note them in a separate comment on the PR — do not fix them in this PR.

**When done:**
1. Open a PR against `main`.
2. Update `NOW.md` to show "Phase 2.B in review; Phase 2.C unblocked after merge".
3. Do not merge yourself — wait for owner approval.

---

## Prompt (Lane C — Phase 2.C First Capability Module)

> **Only use this prompt AFTER Lane A's PR has merged** and `docs/SECURITY_REVIEW.md` is on `main`.

You are an AI coding agent working on the `agent-ready` repo. Your task is issue **#1 — Phase 2.C `vercel_cli` capability module**.

**Prerequisites you must confirm:**
- `docs/SECURITY_REVIEW.md` exists on `main`. If not, stop and tell the user.
- You've read it and will implement within its constraints.

**Read first:**
1. `AGENT_PICKUP.md`
2. `docs/SECURITY_REVIEW.md` (critical — this defines your boundaries)
3. `docs/ARCHITECTURE.md`, `docs/DESIGN.md`, `docs/CAPABILITY_REGISTRY.md`
4. `schema/capabilities.v1.json` — the `vercel_cli` entry
5. Issue #1 via `gh issue view 1`

**Your deliverable:** `agent_ready/capabilities/__init__.py` + `agent_ready/capabilities/vercel_cli.py` implementing the five lifecycle functions: `detect()`, `install()`, `auth()`, `verify()`, `undo()`. Plus `tests/test_capability_vercel.py` with subprocess-mocked tests.

**Work on a branch:** `phase-2c/vercel-cli`.

**Non-negotiables:**
- One capability only. Do not add `github_cli` or `nodejs` even if you have time.
- Tests verify *command strings and ordering*, not actual installs (CI can't install software). Mock subprocess.
- Plain-English user-facing prompts. Never say "CLI", "auth token", "PATH" — say "tool", "sign-in", "connection".
- PR description must include the `## Safety review` block per `CONTRIBUTING.md`.
- Never `--no-verify`. Pre-commit hook must pass.
- Ruff + pytest must be green.
- Bump `pyproject.toml` and `agent_ready/__init__.py` to `v0.3.0`. Update `CHANGELOG.md`.
- Update `NOW.md` to show "Phase 2.C complete; Phase 2.D (MCP) next".

**Scope guardrails:**
- Do NOT unstubb `verify` or `undo` in `cli.py` for other capabilities — only for `vercel_cli`.
- Do NOT modify `mapper.py`, `registry.py`, `plan.py`, or the adapters.
- Do NOT touch `schema/capabilities.v1.json` — the entry is already correct.

**When done:**
1. Test on a real Mac (manual): `agent-ready fix --capability vercel_cli --dry-run`, then `agent-ready fix --capability vercel_cli`, then `agent-ready verify vercel_cli`, then `agent-ready undo vercel_cli`. Document results in the PR description.
2. Open PR against `main`.
3. Wait for owner approval. Do not merge yourself.
