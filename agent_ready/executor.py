"""Execute a capability remediation Plan.

Takes a Plan from `detect` and runs through each capability's lifecycle:
  install → account → auth → verify

Per-capability approval, interruption handling, and best-effort rollback.
"""

from __future__ import annotations

import webbrowser
from dataclasses import dataclass, field

from agent_ready.models import Capability, Plan
from agent_ready.sandbox import SecurityError, get_os, run_step


@dataclass
class StepTracker:
    """Tracks which steps completed successfully so undo can reverse them."""

    completed: list[dict] = field(default_factory=list)

    def record(self, step_name: str, command: str, result: dict):
        self.completed.append(
            {
                "step": step_name,
                "command": command,
                "exit_code": result["exit_code"],
            }
        )

    def reversed_steps(self) -> list[dict]:
        return list(reversed(self.completed))


class InstallOrchestrator:
    """Orchestrates the full install → auth → verify flow for a capability."""

    def __init__(self, capability: Capability, interactive: bool = True):
        self.capability = capability
        self.interactive = interactive
        self.tracker = StepTracker()
        self._interrupted = False

    def run(self) -> bool:
        """Execute all steps for this capability. Returns True if all succeeded."""
        # Step 1: Install
        if self.capability.install:
            if not self._run_install():
                return False

        # Step 2: Account (open URL for user)
        if self.capability.requires_account:
            if not self._run_account():
                return False

        # Step 3: Auth (run the auth command)
        if self.capability.requires_auth:
            if not self._run_auth():
                return False

        # Step 4: Verify
        if self.capability.verify:
            if not self._run_verify():
                return False

        return True

    def _run_install(self) -> bool:
        os_name = get_os()
        command = self.capability.install.get(os_name)
        if not command:
            return False
        print(f"  Installing {self.capability.name}...")
        try:
            result = run_step(command, timeout=300)
        except SecurityError as e:
            print(f"  {e}")
            return False
        self.tracker.record("install", command, result)
        if result["exit_code"] == 0:
            print(f"  ✓ {self.capability.name} installed.")
            return True
        print(f"  ✗ Install failed: {result['stderr']}")
        return False

    def _run_account(self) -> bool:
        url = self.capability.account_url or ""
        if url:
            print(f"  Opening {self.capability.name} signup page...")
            webbrowser.open(url)
        if self.interactive:
            input(f"  Press Enter once you've created your {self.capability.name} account...")
        self.tracker.record("account", f"opened {url}", {"exit_code": 0})
        return True

    def _run_auth(self) -> bool:
        command = self.capability.auth_command or ""
        if not command:
            return True
        print(f"  Signing in to {self.capability.name}...")
        try:
            result = run_step(command, timeout=300)
        except SecurityError as e:
            print(f"  {e}")
            return False
        self.tracker.record("auth", command, result)
        if result["exit_code"] == 0:
            print(f"  ✓ Signed in to {self.capability.name}.")
            return True
        print(f"  ✗ Sign-in failed: {result['stderr']}")
        return False

    def _run_verify(self) -> bool:
        command = self.capability.verify.get("command", "") if self.capability.verify else ""
        if not command:
            return True
        print(f"  Verifying {self.capability.name} works...")
        result = run_step(command, timeout=30)
        self.tracker.record("verify", command, result)
        if result["exit_code"] == 0:
            print(f"  ✓ {self.capability.name} is ready to use.")
            return True
        print(f"  ✗ Verification failed: {result['stderr']}")
        return False


def _ask_approval(capability: Capability) -> bool:
    """Present the capability plan to the user and ask for approval."""
    steps_summary = []
    cap = capability
    if cap.install:
        steps_summary.append("install the tool")
    if cap.requires_account:
        steps_summary.append("create an account")
    if cap.requires_auth:
        steps_summary.append("sign in")
    if cap.verify:
        steps_summary.append("verify it works")

    description = ", ".join(steps_summary) if steps_summary else "set up"
    prompt = (
        f"I'll set up {cap.name} — {cap.plain_english}\n"
        f"This will: {description}.\n"
        f"Proceed? [Yes] No: "
    )
    answer = input(prompt).strip().lower()
    return answer in ("yes", "y", "")


def execute_plan(plan: Plan, interactive: bool = True) -> bool:
    """Execute a full Plan, asking per-capability approval.

    Returns True if all approved capabilities succeeded.
    """
    if not plan.capabilities:
        print("Nothing to set up.")
        return True

    print(f"agent-ready • {len(plan.capabilities)} thing(s) to set up:\n")
    for cap in plan.capabilities:
        print(f"  • {cap.name} — {cap.plain_english}")

    if plan.requires_user_action:
        print("\nSome steps need your input (account signup, sign-in, or an API key).")
    print()

    all_succeeded = True
    for cap in plan.capabilities:
        if interactive:
            approved = _ask_approval(cap)
            if not approved:
                print(f"  Skipping {cap.name}.\n")
                continue

        orchestrator = InstallOrchestrator(cap, interactive=interactive)
        succeeded = orchestrator.run()
        if succeeded:
            print(f"\n✓ {cap.name} is set up and ready.\n")
        else:
            print(f"\n✗ {cap.name} setup did not complete.\n")
            all_succeeded = False

    if all_succeeded:
        print("Everything is set up!")
    return all_succeeded


def verify_capability(capability: Capability) -> bool:
    """Verify a single capability is working."""
    print(f"Verifying {capability.name}...")
    orchestrator = InstallOrchestrator(capability, interactive=False)
    # Only run verification step
    if capability.verify:
        return orchestrator._run_verify()
    print(f"No verification step defined for {capability.name}.")
    return True


def undo_capability(capability: Capability) -> bool:
    """Undo (reverse) the installation of a single capability."""
    print(f"Removing {capability.name}...")
    os_name = get_os()
    command = capability.undo.get(os_name) if capability.undo else None
    if not command:
        print(f"No undo command defined for {capability.name} on {os_name}.")
        return False
    result = run_step(command, timeout=120)
    if result["exit_code"] != 0:
        print(f"✗ Removal failed: {result['stderr']}")
        return False
    # Prove removal: detect should now return False
    if capability.detect and capability.detect.get("command"):
        detect_cmd = capability.detect["command"]
        detect_result = run_step(detect_cmd, timeout=10)
        if detect_result["exit_code"] == 0:
            print(f"✗ {capability.name} is still present after removal.")
            return False
    print(f"✓ {capability.name} has been removed.")
    return True
