"""Loader for the capability registry.

Source of truth: schema/capabilities.v1.json. Every entry must validate against
schema/capability.v1.json.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from agent_ready.models import Capability

_DEFAULT_PATH = Path(__file__).parent.parent / "schema" / "capabilities.v1.json"


@lru_cache(maxsize=1)
def load_registry(path: Path | None = None) -> dict[str, Capability]:
    registry_path = path or _DEFAULT_PATH
    data = json.loads(registry_path.read_text())
    capabilities: dict[str, Capability] = {}
    for entry in data["capabilities"]:
        cap = Capability(
            id=entry["id"],
            name=entry["name"],
            plain_english=entry["plain_english"],
            category=entry["category"],
            detect=entry["detect"],
            install=entry.get("install", {}),
            requires_account=entry.get("requires_account", False),
            account_url=entry.get("account_url"),
            requires_auth=entry.get("requires_auth", False),
            auth_command=entry.get("auth_command"),
            requires_user_action=entry.get("requires_user_action", False),
            verify=entry.get("verify"),
            undo=entry.get("undo", {}),
            provides=entry.get("provides", []),
            related_tasks=entry.get("related_tasks", []),
            error_patterns=entry.get("error_patterns", []),
        )
        capabilities[cap.id] = cap
    return capabilities


def by_error_pattern(pattern_id: str) -> list[Capability]:
    """Return every capability that claims this error pattern."""

    return [cap for cap in load_registry().values() if pattern_id in cap.error_patterns]


def by_id(cap_id: str) -> Capability | None:
    return load_registry().get(cap_id)
