"""Map error signals to a capability remediation Plan.

Read-only: JSON / text in, Plan out. No shell commands, no network, no installers.
Adapters (agent_ready.adapters.*) feed into `plan_from_pattern_hits` — the single
capability-resolution path shared across every input surface.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from agent_ready.models import Capability, Plan, PlanStep
from agent_ready.registry import by_error_pattern, by_id, load_registry

if TYPE_CHECKING:
    from agent_ready.adapters.patterns import PatternHit


def _steps_for_capability(cap: Capability) -> list[PlanStep]:
    steps: list[PlanStep] = []

    if cap.install:
        steps.append(
            PlanStep(
                kind="install",
                capability_id=cap.id,
                human_prompt=f"Install {cap.name} — {cap.plain_english}",
            )
        )

    if cap.requires_account:
        steps.append(
            PlanStep(
                kind="account",
                capability_id=cap.id,
                human_prompt=(
                    f"Create a {cap.name} account at {cap.account_url}. "
                    "I'll open the page for you."
                ),
                needs_user_action=True,
            )
        )

    if cap.requires_auth:
        steps.append(
            PlanStep(
                kind="auth",
                capability_id=cap.id,
                human_prompt=f"Sign in to {cap.name} (I'll run `{cap.auth_command}`).",
                needs_user_action=cap.requires_user_action,
            )
        )

    if cap.requires_user_action and not cap.requires_auth and not cap.requires_account:
        steps.append(
            PlanStep(
                kind="user_action_required",
                capability_id=cap.id,
                human_prompt=f"I need you to help set up {cap.name}.",
                needs_user_action=True,
            )
        )

    if cap.verify:
        steps.append(
            PlanStep(
                kind="verify",
                capability_id=cap.id,
                human_prompt=f"Verify {cap.name} works.",
            )
        )

    if not steps:
        steps.append(
            PlanStep(
                kind="noop",
                capability_id=cap.id,
                human_prompt=f"Nothing to install for {cap.name}.",
            )
        )

    return steps


def plan_from_diagnose(diagnose: dict[str, Any]) -> Plan:
    """Given a schema/trace.v1.json payload, return a capability remediation Plan."""

    errors = diagnose.get("errors") or []
    seen_cap_ids: list[str] = []
    capabilities: list[Capability] = []

    for err in errors:
        cap_id = err.get("maps_to_capability")
        if cap_id:
            cap = by_id(cap_id)
            if cap and cap.id not in seen_cap_ids:
                capabilities.append(cap)
                seen_cap_ids.append(cap.id)
            continue

        # Fallback: pattern_id → capabilities that claim it.
        pattern_id = err.get("pattern_id")
        if pattern_id:
            for cap in by_error_pattern(pattern_id):
                if cap.id not in seen_cap_ids:
                    capabilities.append(cap)
                    seen_cap_ids.append(cap.id)

    steps: list[PlanStep] = []
    for cap in capabilities:
        steps.extend(_steps_for_capability(cap))

    return Plan(capabilities=capabilities, steps=steps, source_diagnose=diagnose)


def plan_from_pattern_hits(hits: list[PatternHit]) -> Plan:
    """Single resolution path: pattern hits → capabilities → Plan.

    Every adapter (text, trace_eval, synthetic diagnose) funnels into here so
    capability-resolution logic stays in one place.
    """

    seen_cap_ids: list[str] = []
    capabilities: list[Capability] = []

    for hit in hits:
        cap_id = hit.pattern.maps_to_capability
        if cap_id:
            cap = by_id(cap_id)
            if cap and cap.id not in seen_cap_ids:
                capabilities.append(cap)
                seen_cap_ids.append(cap.id)
            continue
        # Fallback: pattern owners from registry.
        for cap in by_error_pattern(hit.pattern.id):
            if cap.id not in seen_cap_ids:
                capabilities.append(cap)
                seen_cap_ids.append(cap.id)

    steps: list[PlanStep] = []
    for cap in capabilities:
        steps.extend(_steps_for_capability(cap))

    return Plan(capabilities=capabilities, steps=steps, source_diagnose=None)


def plan_from_task(task_phrase: str) -> Plan:
    """Given a plain-English task phrase, return a Plan based on related_tasks keywords.

    This is the 'no trace available' path — the agent just knows what the user asked for
    and wants to preempt the failure.
    """

    phrase = task_phrase.lower().strip()
    matched: list[Capability] = []
    seen: set[str] = set()
    for cap in load_registry().values():
        for task in cap.related_tasks:
            if task.lower() in phrase and cap.id not in seen:
                matched.append(cap)
                seen.add(cap.id)
                break

    steps: list[PlanStep] = []
    for cap in matched:
        steps.extend(_steps_for_capability(cap))

    return Plan(capabilities=matched, steps=steps, source_diagnose=None)
