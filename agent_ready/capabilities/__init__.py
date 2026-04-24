"""Capability lifecycle modules.

Each module implements: detect(), install(), auth(), verify(), undo().
"""

from __future__ import annotations

from agent_ready.capabilities.vercel_cli import (
    auth,
    detect,
    install,
    undo,
    verify,
)

__all__ = [
    "auth",
    "detect",
    "install",
    "undo",
    "verify",
]
