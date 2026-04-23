"""Render a Plan for humans (CLI output) and for machines (JSON)."""

from __future__ import annotations

from typing import Any

from agent_ready.models import Plan


def render_human(plan: Plan) -> str:
    if not plan.capabilities:
        return "agent-ready • nothing to do — no missing capabilities detected."

    header_count = len(plan.capabilities)
    noun = "thing" if header_count == 1 else "things"
    lines = [
        f"agent-ready • {header_count} {noun} to set up:",
    ]
    for cap in plan.capabilities:
        lines.append(f"  • {cap.name} — {cap.plain_english}")

    if plan.requires_user_action:
        lines.append("")
        lines.append("Some steps need your input (account signup, sign-in, or an API key).")

    lines.append("")
    lines.append("Next: review with `agent-ready fix --dry-run` before anything is installed.")
    return "\n".join(lines)


def render_machine(plan: Plan) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "capabilities": [
            {
                "id": cap.id,
                "name": cap.name,
                "plain_english": cap.plain_english,
                "category": cap.category,
                "requires_user_action": cap.requires_user_action,
                "error_patterns": cap.error_patterns,
            }
            for cap in plan.capabilities
        ],
        "steps": [
            {
                "kind": s.kind,
                "capability_id": s.capability_id,
                "human_prompt": s.human_prompt,
                "needs_user_action": s.needs_user_action,
                "status": s.status,
            }
            for s in plan.steps
        ],
        "requires_user_action": plan.requires_user_action,
    }
