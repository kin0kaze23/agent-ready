"""Mapping trace-eval output → capability Plan."""

from __future__ import annotations

import json
from pathlib import Path

from agent_ready.mapper import plan_from_diagnose, plan_from_task

FIXTURES = Path(__file__).parent / "fixtures"


def _load(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text())


def test_single_blocker_produces_one_capability():
    plan = plan_from_diagnose(_load("diagnose_vercel_missing.json"))
    assert [c.id for c in plan.capabilities] == ["vercel_cli"]
    assert plan.requires_user_action is True  # Vercel signup


def test_multi_blocker_produces_capabilities_in_diagnose_order():
    plan = plan_from_diagnose(_load("diagnose_multi.json"))
    assert [c.id for c in plan.capabilities] == ["vercel_cli", "github_cli", "python"]


def test_multi_blocker_dedups_repeated_capabilities():
    diagnose = _load("diagnose_multi.json")
    diagnose["errors"].append(
        {
            "pattern_id": "vercel_not_logged_in",
            "occurrences": 1,
            "evidence": ["vercel: not logged in"],
            "confidence": 0.9,
            "maps_to_capability": "vercel_cli",
        }
    )
    plan = plan_from_diagnose(diagnose)
    ids = [c.id for c in plan.capabilities]
    assert ids.count("vercel_cli") == 1


def test_clean_diagnose_produces_empty_plan():
    plan = plan_from_diagnose(_load("diagnose_clean.json"))
    assert plan.capabilities == []
    assert plan.steps == []


def test_unknown_capability_id_is_dropped_safely():
    plan = plan_from_diagnose(
        {
            "schema_version": "1.0",
            "score": 50,
            "verdict": "blocked_by_missing_capability",
            "errors": [
                {
                    "pattern_id": "some_future_pattern",
                    "occurrences": 1,
                    "confidence": 0.8,
                    "maps_to_capability": "future_capability_xyz",
                }
            ],
        }
    )
    assert plan.capabilities == []


def test_fallback_uses_pattern_id_when_capability_not_mapped():
    plan = plan_from_diagnose(
        {
            "schema_version": "1.0",
            "score": 50,
            "verdict": "blocked_by_missing_capability",
            "errors": [
                {
                    "pattern_id": "cmd_not_found_vercel",
                    "occurrences": 1,
                    "confidence": 0.95,
                    "maps_to_capability": None,
                }
            ],
        }
    )
    assert [c.id for c in plan.capabilities] == ["vercel_cli"]


def test_plan_from_task_matches_related_tasks():
    plan = plan_from_task("help me deploy my site")
    ids = [c.id for c in plan.capabilities]
    assert "vercel_cli" in ids


def test_plan_from_task_no_match_returns_empty():
    plan = plan_from_task("bake a cake")
    assert plan.capabilities == []
