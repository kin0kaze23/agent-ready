# Security Review — Phase 2.B Install Path

> This document answers the 7 security questions for the `agent-ready fix` install path. It is the gate that must be cleared before any capability installer code (Phase 2.C) lands.

---

## 1. Sandboxing Model

**Question:** Does `fix` run installers in a subshell, a container, or directly on the user's host? Trade-offs?

**Chosen approach:** Run installers in a **controlled subshell on the user's host**.

**Rationale:**

| Option | Pros | Cons |
|--------|------|------|
| Direct host execution | Simple; installers land where the user will actually use them | No isolation; a bad installer can do anything |
| Container (Docker) | Strong isolation; reproducible | Overkill for this product; the user needs the tool on their actual machine, not in a container; adds dependency on Docker |
| Controlled subshell | Can set environment, capture output, limit timeout, and present a clear yes/no to the user before each step | Not as strong as a container, but sufficient given the other safeguards below |

`agent-ready` is a tool that sets up the user's *actual* development environment. Installing inside a container defeats the purpose — the AI agent still won't have the tool on the host. The right trade-off is a controlled subshell with layered safeguards:

- Every command is logged before execution.
- The user sees a plain-English summary of what will happen and approves *before* anything runs.
- Each subprocess runs with a timeout and a restricted environment (no inherited secrets).
- Output is captured for error reporting and undo.

**Implementation sketch:**

New file: `agent_ready/sandbox.py`

```python
import subprocess
import os

def run_step(command: str, timeout: int = 120) -> dict:
    """Run a single installer command in a controlled subshell.

    Returns: {"exit_code": int, "stdout": str, "stderr": str}
    """
    # Clear inherited environment of sensitive values
    safe_env = {k: v for k, v in os.environ.items()
                if not _is_sensitive(k)}
    result = subprocess.run(
        command, shell=True, capture_output=True, text=True,
        timeout=timeout, env=safe_env,
    )
    return {
        "exit_code": result.returncode,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
    }
```

A capability module calls `run_step()` for each of its lifecycle steps. The higher-level orchestrator (`cli.py` or a new `orchestrator.py`) presents the plan to the user, collects approval, and sequences the steps.

---

## 2. Credential Storage

**Question:** Where do API keys, OAuth tokens, and session cookies live?

**Chosen approach:** **Delegate entirely to each tool's native store.** `agent-ready` never writes, reads, or stores credentials itself.

**Rationale:**

| Option | Pros | Cons |
|--------|------|------|
| agent-ready state file | Centralized; easy to manage | Massive security risk; credentials in a file agent-ready owns |
| `.env` files | Common pattern | Scatters credentials across the filesystem; easy to accidentally commit |
| OS keychain | Secure; OS-managed | Platform-specific APIs; adds complexity |
| Tool's native store | Each tool knows how to manage its own credentials securely; battle-tested | Varies by tool |

`agent-ready` should invoke each tool's own sign-in flow (e.g., `vercel login`, `gh auth login`). These tools already handle credential storage correctly — whether that's the OS keychain, a config file in the user's home directory, or an OAuth browser flow. `agent-ready` opens the flow, waits for it to complete, and moves on. It never touches the credentials.

**Implementation sketch:**

In each capability module, the `auth()` function runs the tool's own sign-in command:

```python
# agent_ready/capabilities/vercel_cli.py
def auth() -> bool:
    """Guide the user through signing in to their Vercel account."""
    result = subprocess.run(["vercel", "login"], timeout=300)
    return result.returncode == 0
```

No credential variables are set, no files are written by `agent-ready`. The tool stores its own token in its own way.

---

## 3. Sudo Policy

**Question:** When, if ever, do we use `sudo`? How do we ask the user first, and can we always fall back to user-scope installs?

**Chosen approach:** **Never invoke `sudo` automatically.** Always prefer user-scope installs. If elevated permissions are genuinely required, present the command to the user and let them run it manually.

**Rationale:**

- `sudo` grants full system access. A bug in `agent-ready` or a compromised installer could cause irreversible damage.
- Most common tools can be installed without `sudo`: Homebrew on Mac installs to `~/Homebrew` or `/opt/homebrew`; `pip install --user` and `npm install --prefix ~/.local` are user-scope alternatives.
- The target user is a non-developer. Running `sudo` commands manually is scary and error-prone. By preferring user-scope installs, we avoid this entirely for the common case.

**Policy rules:**

1. First attempt: user-scope install (Homebrew, `--user` flag, etc.).
2. If that fails and `sudo` is the only option: show the user the exact command in plain English ("I need to make a change that requires your system password. Here's the command. Please paste it into your terminal yourself."). Do not execute `sudo` programmatically.
3. Never cache or store the `sudo` password.
4. Never use `sudo` without the user explicitly typing it themselves.

**Implementation sketch:**

In `sandbox.py`, add a guard:

```python
def run_step(command: str, ...) -> dict:
    if command.strip().startswith("sudo "):
        raise SecurityError(
            "This step needs system-level access. "
            "Please run this command yourself in your terminal:\n\n"
            f"  {command}"
        )
```

The capability module should define a user-scope install first, and only list `sudo` as a fallback in a separate field that triggers the "run it yourself" message.

---

## 4. Rollback Guarantees

**Question:** If install fails halfway, what state does the system end in? How does `undo` prove the removal worked?

**Chosen approach:** **Best-effort rollback with explicit verification.** Each step tracks what was done; on failure, `undo` reverses completed steps and verifies removal.

**Rationale:**

- Package managers (brew, npm, pip) are generally idempotent and transactional. A failed `brew install` typically leaves the system in the same state it started in (nothing installed).
- However, some steps may leave partial state (a config file was written, a directory was created). Each capability module is responsible for knowing how to reverse its own steps.
- `undo` must prove removal worked by running the same `detect()` check and confirming the tool is no longer present.

**Implementation sketch:**

Each capability module implements `undo()` that reverses its `install()` steps, then calls `detect()` to verify:

```python
# agent_ready/capabilities/vercel_cli.py
def undo() -> bool:
    """Remove the deployment tool and clean up."""
    result = subprocess.run(["brew", "uninstall", "vercel-cli"],
                            capture_output=True, text=True)
    if result.returncode != 0:
        return False
    # Prove removal: detect should now return False
    return not detect()
```

The orchestrator tracks step completion:

```python
class StepTracker:
    """Tracks which steps completed successfully so undo can reverse them."""

    def __init__(self):
        self.completed: list[dict] = []

    def record(self, step_name: str, command: str, result: dict):
        self.completed.append({
            "step": step_name,
            "command": command,
            "exit_code": result["exit_code"],
        })

    def reversed_steps(self) -> list[dict]:
        return list(reversed(self.completed))
```

If `install()` fails on step 3 of 5, `undo` only needs to reverse steps 1 and 2.

**Guarantee level:** Best effort, not absolute. We cannot guarantee that a partially-failed install leaves zero traces (e.g., a downloaded file that was never installed). But we guarantee that `undo` reverses every *completed* step and verifies the end state.

---

## 5. Interruption Handling

**Question:** If the user Ctrl+C's mid-install, what's the recovery?

**Chosen approach:** **Graceful shutdown with state preservation and recovery options.**

**Rationale:**

- When the user interrupts, the current subprocess should be killed immediately.
- The system must record what was completed before the interruption so that the next run knows where to resume from or what to undo.
- The user should be offered clear options: "Try again" or "Undo what was started."

**Implementation sketch:**

The orchestrator wraps step execution with signal handling:

```python
import signal
import sys

class InstallOrchestrator:
    def __init__(self, plan):
        self.plan = plan
        self.tracker = StepTracker()
        self._interrupted = False

    def _handle_interrupt(self, signum, frame):
        self._interrupted = True
        # Kill any running subprocess (tracked separately)
        if self._current_proc:
            self._current_proc.kill()
        self._save_state()
        print("\nSetup was interrupted.")
        self._offer_recovery()

    def _save_state(self):
        """Write a small state file so recovery knows what happened."""
        state = {
            "capability": self.plan.capability_id,
            "completed_steps": self.tracker.completed,
            "interrupted": True,
        }
        write_state_file(self.plan.capability_id, state)

    def _offer_recovery(self):
        """Present the user with recovery options."""
        # Plain English prompt — no jargon
        completed = len(self.tracker.completed)
        total = len(self.plan.steps)
        print(f"\n{completed} of {total} steps completed.")
        print("What would you like to do?")
        print("  1. Try again from where we left off")
        print("  2. Undo what was set up")
        print("  3. Stop and do nothing")
```

The state file lives in a temporary location (e.g., `~/.agent-ready/state/<capability>.json`) and is cleaned up after successful completion or successful undo.

---

## 6. Approval Cadence

**Question:** Per-capability (one yes = all steps for that capability), per-session (one yes = everything), or per-step (every action asks)?

**Chosen approach:** **Per-capability approval.** One yes approves all steps for that capability only.

**Rationale:**

| Option | User Experience | Safety |
|--------|-----------------|--------|
| Per-step | Too many prompts; user fatigue; annoying for multi-step capabilities | Highest |
| Per-session | One prompt for everything | Too permissive; user may not understand what they approved |
| Per-capability | One prompt per tool; clear scope; manageable | Good balance |

Per-capability is the right balance:

- The user sees: "I need to set up the Vercel deployment tool. This will: install the tool, sign you into your account, and confirm it works. Want me to proceed? [Yes] [No]"
- They approve *one capability*, not all capabilities. If the plan includes Vercel *and* GitHub, the user approves each separately.
- This aligns with the existing non-negotiable: "Approval per capability, not blanket. Never yes-to-all."

**Implementation sketch:**

The orchestrator loops over capabilities in the plan, asking once per capability:

```python
def execute_plan(plan):
    for capability in plan.capabilities:
        # Show the user what will happen
        summary = capability.summary()  # plain English
        approved = ask_user(f"I'll set up {capability.name}. {summary} Proceed? [Yes] [No]")
        if not approved:
            print(f"Skipping {capability.name}.")
            continue
        # Run all steps for this capability
        run_capability(capability)
```

---

## 7. Network Install Risks

**Question:** `curl | sh` is common. Do we allow it? With what mitigations?

**Chosen approach:** **Never allow `curl | sh` directly. Always prefer trusted package managers. If no package manager exists, download the script first, show the user what it does, and require explicit approval before running.**

**Rationale:**

- `curl | sh` downloads and executes arbitrary code from the network with no opportunity for review. This is a well-known security anti-pattern.
- Most tools we care about (Vercel CLI, GitHub CLI, Node.js) are available through trusted package managers (Homebrew, npm, apt) that perform checksum verification.
- For the rare case where a network script is the *only* option, we add a gate: download to a temp file, show the user the script contents and source URL, and require an explicit "yes, run this script" before execution.

**Policy rules:**

1. **Preferred:** Use a package manager (Homebrew, npm, pip, apt). These have built-in integrity checks.
2. **If no package manager exists:** Download the script to a temporary file, compute its hash, show the user the URL and the first 20 lines of the script, and ask for explicit approval.
3. **Never:** Pipe a network URL directly into a shell. No exceptions.

**Implementation sketch:**

In `sandbox.py`:

```python
import hashlib
import tempfile
import urllib.request

def safe_network_install(url: str, description: str) -> bool:
    """Download an installer script, show it to the user, then run only if approved."""
    # Step 1: Download to temp file
    with tempfile.NamedTemporaryFile(suffix=".sh", delete=False) as f:
        urllib.request.urlretrieve(url, f.name)
        script_path = f.name

    # Step 2: Show user what they're about to run
    with open(script_path) as f:
        preview = "".join(f.readlines()[:20])
    file_hash = hashlib.sha256(open(script_path, "rb").read()).hexdigest()

    print(f"Source: {url}")
    print(f"SHA-256: {file_hash}")
    print(f"\nScript preview (first 20 lines):\n{preview}")
    approved = ask_user(f"Run this script to install {description}? [Yes] [No]")

    if not approved:
        os.unlink(script_path)
        return False

    # Step 3: Run the downloaded script
    result = run_step(f"bash {script_path}")
    os.unlink(script_path)
    return result["exit_code"] == 0
```

---

## Summary Table

| Question | Decision |
|----------|----------|
| Sandboxing model | Controlled subshell on the user's host |
| Credential storage | Delegate to each tool's native store; `agent-ready` never touches credentials |
| Sudo policy | Never auto-sudo; user-scope installs only; manual sudo if no alternative |
| Rollback guarantees | Best-effort; `undo` reverses completed steps and verifies removal via `detect()` |
| Interruption handling | Graceful shutdown; save state; offer "resume" or "undo" options |
| Approval cadence | Per-capability (one yes = all steps for that capability only) |
| Network install risks | No `curl | sh`; prefer package managers; download-review-run gate for scripts |

---

## Next Steps

1. This review gates Phase 2.C (`vercel_cli` capability module). Implementers must follow the decisions above.
2. New files needed in Phase 2.C: `agent_ready/sandbox.py` (subshell runner), `agent_ready/capabilities/vercel_cli.py` (first capability), `tests/test_capability_vercel.py`.
3. The orchestrator in `cli.py` needs to gain per-capability approval prompts and interruption handling before calling capability lifecycle functions.
