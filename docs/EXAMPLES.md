# agent-ready — Usage Examples

Phase 1 + 2.A are live: `detect` auto-detects input format. `fix` / `verify` / `undo` are intentionally stubbed pending security review.

## 1. From a task phrase (zero setup — no trace needed)

```bash
agent-ready detect --task "deploy my portfolio to production"
```

```
agent-ready • 1 thing to set up:
  • Vercel CLI — The tool that puts your website on the internet.

Some steps need your input (account signup, sign-in, or an API key).

Next: review with `agent-ready fix --dry-run` before anything is installed.
```

Exit codes: `0` = nothing to do, `1` = one or more capabilities to set up.

## 2. From a raw agent trace (highest recall)

```bash
cat session.jsonl | agent-ready detect
# or
agent-ready detect --from session.jsonl
```

Scans the raw text against `schema/error-patterns.v1.json` and maps matches to capabilities. Works with **any** agent surface that emits readable error text (Claude Code, Cursor, OpenClaw, Hermes, plain shell logs).

## 3. From trace-eval's scorecard output

```bash
trace-eval run session.jsonl --format json | agent-ready detect
```

Lower recall than raw text — see [docs/INTEGRATION.md § Known Limits](INTEGRATION.md#known-limits--real-scorecard-precision). For full precision, use the Python API:

```python
import json
from pathlib import Path
from agent_ready.adapters.trace_eval import plan_from_trace_eval_with_trace

scorecard = json.loads(Path("scorecard.json").read_text())
plan = plan_from_trace_eval_with_trace(scorecard, Path("session.jsonl"))
```

## 4. Machine-readable Plan for agents

```bash
cat session.jsonl | agent-ready detect --json
```

Output conforms to the Plan shape — capability list + step list + user-action flag.

## 5. Inspect what the registry knows

```bash
agent-ready status
```

```
agent-ready 0.2.0 — 5 capabilities in registry:
  • vercel_cli           Vercel CLI
  • github_cli           GitHub CLI
  • nodejs               Node.js
  • python               Python
  • api_key_config       API Key Configuration
```

## 6. Call from Python

```python
from agent_ready import plan_from_text, render_human

raw = open("session.jsonl").read()
plan = plan_from_text(raw)
print(render_human(plan))
for cap in plan.capabilities:
    print(f"→ {cap.name}: {cap.install.get('mac', '(no install command)')}")
```

## 7. Extending the registry (for contributors / AI agents)

To add a new capability:

1. Edit `schema/capabilities.v1.json` — add a new entry conforming to `capability.v1.json`.
2. If a new error pattern is needed, edit `schema/error-patterns.v1.json`.
3. Add a fixture in `tests/fixtures/` and a test in `tests/test_adapters.py` or `test_mapper.py`.
4. `pytest tests/ -q` + `ruff check .` must pass.
5. Follow `CONTRIBUTING.md` — capability-adding PRs need a safety-review block once `fix` is unstubbed.

Only `detect` is wired today. Capability install modules (`agent_ready/capabilities/<id>.py`) are the Phase 2.C target — they need the safety review first.
