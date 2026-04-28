"""Execute a capability remediation Plan.

Takes a Plan from `detect` and runs through each capability's lifecycle:
  install → account → auth → verify

Per-capability approval, interruption handling, and best-effort rollback.
All user-facing output is plain English — no technical jargon.

Lifecycle functions are driven generically from schema data — no per-capability
Python code needed. Adding a new capability = just a JSON registry entry.
"""

from __future__ import annotations

import webbrowser
from dataclasses import dataclass, field

from agent_ready.models import Capability, Plan
from agent_ready.capabilities.generic import (
    lifecycle_detect,
    lifecycle_install,
    lifecycle_auth,
    lifecycle_verify,
    lifecycle_undo,
)


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
    """Orchestrates the full install → auth → verify flow for a capability.

    Uses the generic lifecycle executor — no per-capability code needed.
    """

    def __init__(self, capability: Capability, interactive: bool = True):
        self.capability = capability
        self.interactive = interactive
        self.tracker = StepTracker()
        self._interrupted = False

    def run(self) -> bool:
        """Execute all steps for this capability. Returns True if all succeeded."""
        # Step 1: Install (skip if already installed)
        if self.capability.install:
            already_installed = lifecycle_detect(self.capability)
            if already_installed:
                label = self.capability.plain_english.rstrip(".")
                print(f"  ✓ {label} is already installed.")
            elif not lifecycle_install(self.capability):
                return False

        # Step 2: Account (open URL for user)
        if self.capability.requires_account:
            if not self._run_account():
                return False

        # Step 3: Auth (run the auth command)
        if self.capability.requires_auth:
            if not lifecycle_auth(self.capability):
                return False

        # Step 4: Verify
        if self.capability.verify:
            if not lifecycle_verify(self.capability):
                return False

        return True

    def _run_account(self) -> bool:
        url = self.capability.account_url or ""
        if url:
            label = self.capability.plain_english.rstrip(".")
            print(f"  Opening {label.lower()} signup page in your browser...")
            webbrowser.open(url)
        if self.interactive:
            input("  Press Enter once you've signed up...")
        self.tracker.record("account", f"opened {url}", {"exit_code": 0})
        return True


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
        steps_summary.append("confirm it works")

    description = ", ".join(steps_summary) if steps_summary else "set things up"
    label = cap.plain_english.rstrip(".")
    prompt = (
        f"I can set up {label.lower()} for you.\nThis will: {description}.\nWant me to? [Yes] No: "
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
    """Verify a single capability is working using the generic executor."""
    label = capability.plain_english.rstrip(".")
    print(f"Checking {label.lower()}...")
    return lifecycle_verify(capability)


def undo_capability(capability: Capability) -> bool:
    """Undo (reverse) the installation of a single capability using the generic executor."""
    label = capability.plain_english.rstrip(".")
    print(f"Removing {label.lower()}...")
    result = lifecycle_undo(capability)
    if result:
        print(f"✓ {label} has been removed.")
    else:
        print(f"✗ Couldn't remove {label.lower()}.")
    return result
