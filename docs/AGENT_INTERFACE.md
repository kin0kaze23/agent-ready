# Agent Interface

> How AI agents drive agent-ready. The human CLI is secondary.

---

## Surfaces (priority order)

1. **MCP server** *(Phase 2 target)* — the primary surface for Claude Code, Cursor, Codex, Gemini. Tools:
   - `agent_ready.detect` → "What capabilities are missing for this task / from this trace?"
   - `agent_ready.fix` → "Install and configure; ask the human when needed."
   - `agent_ready.verify` → "Does this capability actually work right now?"
   - `agent_ready.undo` → "Remove what was installed."
2. **CLI `--json`** *(Phase 1)* — portable fallback.
3. **Python library** *(Phase 1)* — `from agent_ready import detect, fix, verify, undo`.

---

## Round-Trip with trace-eval

```
trace-eval diagnose --json > diagnose.json
agent-ready detect --from diagnose.json
  → emits capability plan: [{id, status, needs_user_action}, ...]
agent-ready fix --plan <plan.json>
  → for each step: install → (if needed) pause for user → auth → verify
agent-ready verify --capability vercel_cli
  → exit 0 if working, else structured failure
```

The agent never parses English. Every command has a `--json` mode that conforms to the schemas under `schema/`.

---

## User-in-the-Loop Pattern

Some steps a tool genuinely cannot automate — creating an account, clicking "authorize", pasting an API key the human must generate. `agent-ready` treats these as first-class:

```json
{
  "step": "create_vercel_account",
  "kind": "user_action_required",
  "human_prompt": "I've opened Vercel's signup page in your browser. Sign up with your GitHub account, then come back and say 'done'.",
  "unblock_signal": {"type": "stdin_line", "value": "done"},
  "verification": {"command": "vercel whoami", "exit_code": 0}
}
```

The agent's job is to surface the `human_prompt` to the user verbatim, wait for the `unblock_signal`, then call `verify`. Nothing more. This keeps the agent simple and the user in control.

---

## Approval Model

- **One approval per capability**, not one blanket "yes install everything".
- Approval is short-lived: a new session requires fresh approval.
- `agent-ready fix --dry-run` prints the plan without running anything. Agents should call this first and show the user the plan before calling the real `fix`.

---

## Error Categories

When `agent-ready` can't finish, it returns a structured failure:

| Reason | Meaning | What the agent should do |
|--------|---------|-------------------------|
| `user_declined` | User said no | Stop. Tell the user what won't work without it. |
| `user_timeout` | User didn't respond to prompt | Stop. Tell the user the step is still pending. |
| `install_failed` | Installer returned non-zero | Report with redacted logs. Suggest `agent-ready undo`. |
| `verify_failed` | Installed but doesn't work | Report. Do not claim success. |
| `no_fix_known` | Pattern mapped to `null` capability | Open a `capability-gap` issue automatically (opt-in). |

---

## Telemetry (opt-in, Phase 2)

If opted in, `agent-ready` emits a redacted record per run: `{capability_ids_attempted, outcomes, os, agent_name, duration}`. No file paths, no usernames, no tokens.
