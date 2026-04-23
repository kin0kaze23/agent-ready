# agent-ready — Usage Examples

Phase 1 supports `detect` (read-only, safe). `fix` / `verify` / `undo` are intentionally stubbed — they wait on the security review of the install path.

## 1. From a task phrase (fully working today — no trace needed)

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

## 2. From a synthetic diagnose JSON (today — uses internal format)

```bash
agent-ready detect --from tests/fixtures/diagnose_vercel_missing.json --json
```

> **Phase 2 task:** consume real `trace-eval run ... --format json` output via an adapter. See `docs/INTEGRATION.md`.

Machine output conforms to the Plan shape — capability list + step list + user-action flag.

## 3. From a plain-English task phrase (no trace needed)

```bash
agent-ready detect --task "deploy my portfolio to production"
```

The mapper matches against each capability's `related_tasks` and pre-flights what would be needed.

## 4. Inspect what the registry knows

```bash
agent-ready status
```

```
agent-ready 0.1.0 — 5 capabilities in registry:
  • vercel_cli           Vercel CLI
  • github_cli           GitHub CLI
  • nodejs               Node.js
  • python               Python
  • api_key_config       API Key Configuration
```

## 5. Call from Python

```python
import json
from agent_ready import plan_from_diagnose, render_human

with open("diagnose.json") as f:
    diagnose = json.load(f)

plan = plan_from_diagnose(diagnose)
print(render_human(plan))
for cap in plan.capabilities:
    print("→", cap.name, cap.install.get("mac"))
```

## 6. Extending the registry (for contributors / AI agents)

To add a new capability:

1. Edit `schema/capabilities.v1.json` — add a new entry conforming to `capability.v1.json`.
2. Confirm a matching error pattern in `schema/error-patterns.v1.json` (mirror from trace-eval).
3. Add a fixture in `tests/fixtures/` and a test in `tests/test_mapper.py`.
4. Run `pytest tests/ -q` + `ruff check .`.
5. Follow `CONTRIBUTING.md` — schema changes require coordinated PR with trace-eval.

Only `detect` is wired today. Capability install modules (`agent_ready/capabilities/<id>.py`) are the Phase 2 target — they need the safety review first.
