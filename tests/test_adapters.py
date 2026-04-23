"""Tests for the Phase 2.A input adapters."""

from __future__ import annotations

import json
from pathlib import Path

from agent_ready.adapters import (
    is_trace_eval_scorecard,
    plan_from_text,
    plan_from_trace_eval_json,
    scan_text,
)
from agent_ready.adapters.trace_eval import plan_from_trace_eval_with_trace

FIXTURES = Path(__file__).parent / "fixtures"


# --- text adapter ---------------------------------------------------------


def test_scan_text_finds_vercel_and_gh():
    text = (FIXTURES / "raw_trace_text.log").read_text()
    hits = scan_text(text)
    ids = [h.pattern.id for h in hits]
    assert "cmd_not_found_vercel" in ids
    assert "cmd_not_found_gh" in ids


def test_plan_from_text_produces_capabilities():
    text = (FIXTURES / "raw_trace_text.log").read_text()
    plan = plan_from_text(text)
    ids = [c.id for c in plan.capabilities]
    assert "vercel_cli" in ids
    assert "github_cli" in ids


def test_plan_from_empty_text_is_empty():
    plan = plan_from_text("")
    assert plan.capabilities == []


# --- trace-eval scorecard adapter ----------------------------------------


def test_is_trace_eval_scorecard_recognizes_real_shape():
    data = json.loads((FIXTURES / "trace_eval_scorecard_real.json").read_text())
    assert is_trace_eval_scorecard(data) is True


def test_is_trace_eval_scorecard_rejects_other_shapes():
    synthetic_diagnose = json.loads((FIXTURES / "diagnose_vercel_missing.json").read_text())
    assert is_trace_eval_scorecard(synthetic_diagnose) is False
    assert is_trace_eval_scorecard({}) is False
    assert is_trace_eval_scorecard("not a dict") is False


def test_scorecard_with_verbatim_errors_in_suggestions_finds_capabilities():
    """Synthetic scorecard that DOES include the raw error text in its suggestions."""
    data = json.loads((FIXTURES / "trace_eval_scorecard_synthetic.json").read_text())
    plan = plan_from_trace_eval_json(data)
    ids = [c.id for c in plan.capabilities]
    assert "vercel_cli" in ids
    assert "github_cli" in ids


def test_real_scorecard_alone_may_return_empty_plan():
    """Document the limitation: real trace-eval scorecards summarize by event index.

    The `with_trace` variant is required for precise capability detection.
    """
    data = json.loads((FIXTURES / "trace_eval_scorecard_real.json").read_text())
    plan = plan_from_trace_eval_json(data)
    # We don't assert empty — some patterns may match flag suggestions. Assert that
    # we don't crash and that the source_diagnose is preserved.
    assert plan.source_diagnose == data


def test_with_trace_captures_errors_the_scorecard_summarized():
    scorecard = json.loads((FIXTURES / "trace_eval_scorecard_synthetic.json").read_text())
    trace_path = FIXTURES / "raw_trace_text.log"
    plan = plan_from_trace_eval_with_trace(scorecard, trace_path)
    ids = [c.id for c in plan.capabilities]
    assert "vercel_cli" in ids
    assert "github_cli" in ids
    assert plan.source_diagnose == scorecard
