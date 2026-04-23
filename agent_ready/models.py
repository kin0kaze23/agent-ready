"""Core data structures for agent-ready. Pure dataclasses."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

Category = Literal["tool", "account", "auth", "credential", "runtime", "mcp_server", "other"]

StepKind = Literal["install", "account", "auth", "user_action_required", "verify", "noop"]

StepStatus = Literal["pending", "ok", "skipped", "failed"]


@dataclass(frozen=True)
class Capability:
    id: str
    name: str
    plain_english: str
    category: Category
    detect: dict
    install: dict[str, str] = field(default_factory=dict)
    requires_account: bool = False
    account_url: str | None = None
    requires_auth: bool = False
    auth_command: str | None = None
    requires_user_action: bool = False
    verify: dict | None = None
    undo: dict[str, str] = field(default_factory=dict)
    provides: list[str] = field(default_factory=list)
    related_tasks: list[str] = field(default_factory=list)
    error_patterns: list[str] = field(default_factory=list)


@dataclass
class PlanStep:
    kind: StepKind
    capability_id: str
    human_prompt: str
    status: StepStatus = "pending"
    needs_user_action: bool = False


@dataclass
class Plan:
    """A plan to remediate a set of missing capabilities.

    Emitted by `detect`, consumed by `fix`. `fix` is not implemented yet — this plan is
    read-only until the safety review lands.
    """

    capabilities: list[Capability]
    steps: list[PlanStep]
    source_diagnose: dict | None = None  # the trace-eval diagnose.json that produced this

    @property
    def requires_user_action(self) -> bool:
        return any(s.needs_user_action for s in self.steps)
