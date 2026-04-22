# agent-ready — UX Design for Non-Devs

> **Target user:** Someone who uses AI agents but doesn't know terminal commands or how to set up development tools.
> **Goal:** When their agent can't do something, agent-ready detects the gap, installs what's needed, and guides the user through setup.

---

## The Non-Dev User Journey

### Before agent-ready
```
User: "Deploy my app"
Agent: "Run: brew install vercel-cli"
User: "What's brew?"
User: *gives up*
```

### After agent-ready
```
User: "Deploy my app"
Agent: "I'm missing some tools. I can set them up for you in 2 minutes. Want me to?"
User: "Yes"
Agent: *installs, configures, verifies* "All set! Deploying now..."
       *succeeds*
```

---

## Design Principles

1. **User never sees a terminal** — Agent handles all commands. User only sees prompts.
2. **Plain English only** — "Install the deployment tool" not "Install Vercel CLI".
3. **Progressive disclosure** — One step at a time. Never overwhelm.
4. **Safe defaults** — Always ask before installing. Never store credentials.
5. **Context-aware** — Only suggest setup relevant to the current task.

---

## The Setup Flow

1. **Detect** — `agent-ready detect --task "deploy"` → what's missing
2. **Approve** — Agent presents plan to user → user approves
3. **Execute** — Step-by-step installation with progress updates
4. **Verify** — Confirm everything works before retrying
5. **Retry** — Agent retries task, then runs trace-eval to confirm improvement

---

## Integration with trace-eval

### The Complete Loop

1. Agent tries task → fails
2. `trace-eval --json` → detects error patterns
3. `agent-ready detect` → maps errors to missing capabilities
4. User approves → `agent-ready fix` → installs, configures, verifies
5. Agent retries → succeeds
6. `trace-eval --json` → confirms improvement

### Error Pattern → Capability Mapping

| trace-eval Error | Missing Capability | Setup Flow |
|-----------------|-------------------|------------|
| "command not found: vercel" | Vercel CLI | Install → Login → Link |
| "command not found: gh" | GitHub CLI | Install → Auth → Configure |
| "not logged in" | Account needed | Open signup → Wait |
| "no API key found" | Credentials | Guide to create → Store |

---

## What the Agent Reports

### After Detection
```
I checked what's needed. You're missing 3 things,
but I can set them all up in about 2 minutes.
Want me to get everything ready? [Yes] [No]
```

### After Setup
```
Everything is set up!
✓ Vercel CLI — the deployment tool
✓ Vercel account — where your site lives
✓ Project link — connected your code
Want me to deploy now? [Yes] [Not yet]
```

### After Success
```
Deployed! ✓
URL: your-app.vercel.app
Session quality: 89/100 (was 22/100 before setup)
```

---

## For AI Agents Working on This Repo

1. **Start with detection** — build `agent-ready detect` first
2. **Build the capability registry** — the data layer foundation
3. **One capability end-to-end** — Vercel CLI is the best starting point
4. **Test with real traces** — use trace-eval/examples/
5. **Design for the agent** — JSON input/output, not terminal UX
6. **Keep it simple** — validate before expanding
