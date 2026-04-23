"""Load the error-pattern catalog.

The catalog lives in schema/error-patterns.v1.json and is canonical in agent-ready.
It is NOT mirrored from trace-eval — trace-eval uses a different, event-based model.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

_CATALOG_PATH = Path(__file__).parent.parent.parent / "schema" / "error-patterns.v1.json"


@dataclass(frozen=True)
class ErrorPattern:
    id: str
    category: str
    regex: str
    human: str
    maps_to_capability: str | None
    confidence_base: float


@lru_cache(maxsize=1)
def load_patterns(path: Path | None = None) -> list[ErrorPattern]:
    catalog_path = path or _CATALOG_PATH
    data = json.loads(catalog_path.read_text())
    return [
        ErrorPattern(
            id=p["id"],
            category=p["category"],
            regex=p["regex"],
            human=p["human"],
            maps_to_capability=p.get("maps_to_capability"),
            confidence_base=float(p["confidence_base"]),
        )
        for p in data["patterns"]
    ]


@dataclass
class PatternHit:
    pattern: ErrorPattern
    occurrences: int


def match_patterns(text: str) -> list[PatternHit]:
    """Scan text line-by-line for every catalog pattern. Deterministic, catalog-ordered."""

    hits: list[PatternHit] = []
    for pattern in load_patterns():
        compiled = re.compile(pattern.regex)
        occurrences = sum(1 for line in text.splitlines() if compiled.search(line))
        if occurrences > 0:
            hits.append(PatternHit(pattern=pattern, occurrences=occurrences))
    return hits
