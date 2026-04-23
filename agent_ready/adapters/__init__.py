"""Input adapters for agent-ready.

Two surfaces today:
  * `text` — scan any raw log / trace text with the error-pattern catalog.
  * `trace_eval` — consume real trace-eval v0.5.0 scorecard JSON output.

Both paths funnel into the same `Plan` construction in `agent_ready.mapper`.
"""

from __future__ import annotations

from agent_ready.adapters.text import plan_from_text, scan_text
from agent_ready.adapters.trace_eval import (
    is_trace_eval_scorecard,
    plan_from_trace_eval_json,
)

__all__ = [
    "plan_from_text",
    "scan_text",
    "plan_from_trace_eval_json",
    "is_trace_eval_scorecard",
]
