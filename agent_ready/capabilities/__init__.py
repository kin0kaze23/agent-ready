"""Capability lifecycle modules.

Two paths:
- Generic executor: reads lifecycle commands from schema data (works for ALL capabilities).
- Per-capability modules: custom logic for complex auth flows (optional override).
"""

from __future__ import annotations

from agent_ready.capabilities.generic import (
    lifecycle_auth,
    lifecycle_detect,
    lifecycle_install,
    lifecycle_undo,
    lifecycle_verify,
)

__all__ = [
    "lifecycle_auth",
    "lifecycle_detect",
    "lifecycle_install",
    "lifecycle_undo",
    "lifecycle_verify",
]
