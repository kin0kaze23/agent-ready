"""Text adapter — scan any raw log / JSONL / JSON trace for missing-capability signals.

Produces a Plan without requiring trace-eval. Works against any agent surface that
emits human-readable error text (which is all of them, in practice).
"""

from __future__ import annotations

from agent_ready.adapters.patterns import PatternHit, match_patterns
from agent_ready.mapper import plan_from_pattern_hits
from agent_ready.models import Plan


def scan_text(raw: str) -> list[PatternHit]:
    """Public: scan arbitrary text for error-catalog matches."""

    return match_patterns(raw)


def plan_from_text(raw: str) -> Plan:
    """Scan raw trace text, map hits to capabilities, return a Plan."""

    hits = scan_text(raw)
    return plan_from_pattern_hits(hits)
