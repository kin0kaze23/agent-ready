"""Adapter for real trace-eval v0.5.0 scorecard JSON output.

trace-eval emits a scorecard of the shape:

  {
    "total_score": 28.29,
    "dimension_scores": {"reliability": 0.0, ...},
    "dimension_confidence": {...},
    "friction_flags": [
      {"id": "reliability_errors", "severity": "medium",
       "dimension": "reliability", "event_index": 23,
       "suggestion": "Review 90 error(s) at event indices [...]"}
    ],
    "adapter_capability_report": {...},
    ...
  }

This adapter does NOT re-score. It extracts every text surface in the scorecard
that might contain an error message (friction_flag.suggestion, adapter reports),
runs them through the shared error-pattern catalog, and emits a Plan.

For higher precision, pair this with the raw trace file via `plan_from_trace_eval_with_trace`.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from agent_ready.adapters.text import plan_from_text
from agent_ready.models import Plan

_SCORECARD_MARKERS = ("total_score", "dimension_scores", "friction_flags")


def is_trace_eval_scorecard(payload: Any) -> bool:
    """True if the payload looks like trace-eval v0.5.0 scorecard JSON."""

    return isinstance(payload, dict) and all(m in payload for m in _SCORECARD_MARKERS)


def _flatten_scorecard_text(scorecard: dict) -> str:
    """Collect every textual surface from a scorecard that could contain error signals."""

    lines: list[str] = []

    for flag in scorecard.get("friction_flags") or []:
        if isinstance(flag, dict):
            suggestion = flag.get("suggestion")
            if suggestion:
                lines.append(str(suggestion))
            flag_id = flag.get("id")
            if flag_id:
                lines.append(str(flag_id))

    report = scorecard.get("adapter_capability_report")
    if isinstance(report, dict):
        for k, v in report.items():
            lines.append(f"{k}: {v}")

    return "\n".join(lines)


def plan_from_trace_eval_json(scorecard: dict) -> Plan:
    """Primary entry point — scorecard-only, no raw trace required.

    Works today even without the underlying trace file. Lower precision than
    `plan_from_trace_eval_with_trace` because trace-eval's scorecard summarizes
    errors by event index rather than quoting them verbatim.
    """

    text = _flatten_scorecard_text(scorecard)
    plan = plan_from_text(text)
    plan.source_diagnose = scorecard
    return plan


def plan_from_trace_eval_with_trace(scorecard: dict, trace_path: Path | str) -> Plan:
    """Higher precision — combine scorecard with the raw trace file.

    Scans the raw trace text too, capturing the actual error lines that flags
    only reference by event_index.
    """

    scorecard_text = _flatten_scorecard_text(scorecard)
    raw_trace = Path(trace_path).read_text()
    combined = f"{scorecard_text}\n{raw_trace}"
    plan = plan_from_text(combined)
    plan.source_diagnose = scorecard
    return plan
