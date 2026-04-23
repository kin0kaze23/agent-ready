"""Plan rendering — human three-liner + JSON schema shape."""

from __future__ import annotations

import json
from pathlib import Path

from agent_ready.mapper import plan_from_diagnose
from agent_ready.plan import render_human, render_machine

FIXTURES = Path(__file__).parent / "fixtures"


def _plan(name: str):
    return plan_from_diagnose(json.loads((FIXTURES / name).read_text()))


def test_human_output_lists_every_capability():
    plan = _plan("diagnose_multi.json")
    rendered = render_human(plan)
    for cap in plan.capabilities:
        assert cap.name in rendered


def test_human_output_empty_plan_is_reassuring():
    plan = _plan("diagnose_clean.json")
    rendered = render_human(plan)
    assert "nothing to do" in rendered.lower()


def test_machine_output_is_json_serializable():
    plan = _plan("diagnose_vercel_missing.json")
    data = render_machine(plan)
    reserialized = json.loads(json.dumps(data))
    assert reserialized["capabilities"][0]["id"] == "vercel_cli"


def test_machine_output_has_required_fields():
    plan = _plan("diagnose_vercel_missing.json")
    data = render_machine(plan)
    assert data["schema_version"] == "1.0"
    assert "capabilities" in data
    assert "steps" in data
    assert "requires_user_action" in data


def test_user_action_flag_propagates():
    plan = _plan("diagnose_vercel_missing.json")  # Vercel needs signup
    data = render_machine(plan)
    assert data["requires_user_action"] is True
