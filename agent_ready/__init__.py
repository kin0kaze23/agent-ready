"""agent-ready: Detect what your AI agent is missing. Install it. Get ready.

v0.4.0 status:
  * `detect` is live — text / session report / task phrase.
  * `fix` / `verify` / `undo` are live — generic executor, schema-driven.
  * MCP server is live — 5 tools via `vibedev.ready.*` namespace.
"""

from __future__ import annotations

__version__ = "0.4.0"

from agent_ready.adapters import (
    is_trace_eval_scorecard,
    plan_from_text,
    plan_from_trace_eval_json,
    scan_text,
)
from agent_ready.executor import execute_plan, undo_capability, verify_capability
from agent_ready.mapper import (
    plan_from_diagnose,
    plan_from_pattern_hits,
    plan_from_task,
)
from agent_ready.models import Capability, Plan, PlanStep
from agent_ready.plan import render_human, render_machine
from agent_ready.registry import by_error_pattern, by_id, load_registry

__all__ = [
    "__version__",
    "Capability",
    "Plan",
    "PlanStep",
    "by_error_pattern",
    "by_id",
    "execute_plan",
    "is_trace_eval_scorecard",
    "load_registry",
    "plan_from_diagnose",
    "plan_from_pattern_hits",
    "plan_from_task",
    "plan_from_text",
    "plan_from_trace_eval_json",
    "render_human",
    "render_machine",
    "scan_text",
    "undo_capability",
    "verify_capability",
]
