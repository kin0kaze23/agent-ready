"""Execute a capability remediation Plan.

Takes a Plan from `detect` and runs through each capability's lifecycle:
  install → account → auth → verify

Per-capability approval, interruption handling, and best-effort rollback.
All user-facing output is plain English — no technical jargon.
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
        # Step 1: Install (skip if already installed)
        if self.capability.install:
            already_installed = self._check_installed()
            if already_installed:
                print(f"  ✓ {self.capability.name} is already installed.")
            elif not self._run_install():
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

    def _check_installed(self) -> bool:
        """Check if the capability is already installed."""
        from agent_ready.sandbox import run_step

        cmd = self.capability.detect.get("command", "")
        if not cmd:
            return False
        result = run_step(cmd, timeout=10)
        return result["exit_code"] == 0

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
            print(f"  Opening {self.capability.name} signup page in your browser...")
            webbrowser.open(url)
        if self.interactive:
            input("  Press Enter once you've signed up...")
        self.tracker.record("account", f"opened {url}", {"exit_code": 0})
        return True

    def _run_auth(self) -> bool:
        command = self.capability.auth_command or ""
        if not command:
            return True
        print(f"  Signing in to your {self.capability.name} account...")
        try:
            result = run_step(command, timeout=300)
        except SecurityError as e:
            print(f"  {e}")
            return False
        self.tracker.record("auth", command, result)
        if result["exit_code"] == 0:
            print("  ✓ Signed in.")
            return True
        print(f"  ✗ Sign-in didn't complete: {result['stderr']}")
        return False

    def _run_verify(self) -> bool:
        command = self.capability.verify.get("command", "") if self.capability.verify else ""
        if not command:
            return True
        print("  Checking everything works...")
        result = run_step(command, timeout=30)
        self.tracker.record("verify", command, result)
        if result["exit_code"] == 0:
            print(f"  ✓ All good — {self.capability.name} is ready to use.")
            return True
        print(f"  ✗ Something isn't right yet: {result['stderr']}")
        return False


def _ask_approval(capability: Capability) -> bool:
    """Present the capability plan to the user and ask for approval."""
    steps_summary = []
    cap = capability
    if cap.install:
        steps_summary.append("install the deployment tool")
    if cap.requires_account:
        steps_summary.append("create an account")
    if cap.requires_auth:
        steps_summary.append("sign in")
    if cap.verify:
        steps_summary.append("confirm it works")

    description = ", ".join(steps_summary) if steps_summary else "set things up"
    prompt = (
        f"I can set up {cap.plain_english.lower()} for you.\n"
        f"This will: {description}.\n"
        f"Want me to? [Yes] No: "
    )
    answer = input(prompt).strip().lower()
    return answer in ("yes", "y", "")


def execute_plan(plan: Plan, interactive: bool = True) -> bool:
    """Execute a full Plan, asking per-capability approval.

    Returns True if all approved capabilities succeeded.
    """
    if not plan.capabilities:
        print("Everything looks good — nothing to set up.")
        return True

    count = len(plan.capabilities)
    noun = "thing" if count == 1 else "things"
    print(f"I found {count} {noun} to set up:\n")
    for cap in plan.capabilities:
        label = cap.plain_english.rstrip(".")
        print(f"  • {label}")

    if plan.requires_user_action:
        print(
            "\nA few steps need your help (like signing up or signing in). "
            "I'll guide you through each one."
        )
    print()

    all_succeeded = True
    for cap in plan.capabilities:
        if interactive:
            approved = _ask_approval(cap)
            if not approved:
                label = cap.plain_english.rstrip(".").lower()
                print(f"  No problem — skipping {label}.\n")
                continue

        orchestrator = InstallOrchestrator(cap, interactive=interactive)
        succeeded = orchestrator.run()
        if succeeded:
            label = cap.plain_english.rstrip(".")
            print(f"\n✓ {label} is all set.\n")
        else:
            label = cap.plain_english.rstrip(".")
            print(f"\n✗ {label} didn't finish setting up.\n")
            all_succeeded = False

    if all_succeeded:
        print("Everything is set up! Your AI agent should be able to continue now.")
    return all_succeeded


def verify_capability(capability: Capability) -> bool:
    """Verify a single capability is working."""
    label = capability.plain_english.rstrip(".")
    print(f"Checking {label.lower()}...")
    orchestrator = InstallOrchestrator(capability, interactive=False)
    # Only run verification step
    if capability.verify:
        return orchestrator._run_verify()
    print(f"No check defined for {label.lower()}.")
    return True


def undo_capability(capability: Capability) -> bool:
    """Undo (reverse) the installation of a single capability."""
    label = capability.plain_english.rstrip(".")
    print(f"Removing {label.lower()}...")
    os_name = get_os()
    command = capability.undo.get(os_name) if capability.undo else None
    if not command:
        print(
            f"I can't automatically remove {label.lower()}. You may need to uninstall it manually."
        )
        return False
    result = run_step(command, timeout=120)
    if result["exit_code"] != 0:
        print(f"✗ Couldn't remove it: {result['stderr']}")
        return False
    # Prove removal: detect should now return False
    if capability.detect and capability.detect.get("command"):
        detect_cmd = capability.detect["command"]
        detect_result = run_step(detect_cmd, timeout=10)
        if detect_result["exit_code"] == 0:
            print(f"✗ {label} is still there after removal.")
            return False
    print(f"✓ {label} has been removed.")
    return True
