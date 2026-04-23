"""CLI for agent-ready.

`detect` is implemented — auto-detects text / trace-eval scorecard / synthetic diagnose.
`fix` / `verify` / `undo` print a "pending security review" message (exit 2) —
intentional, do not wire them to installers without review.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from agent_ready import __version__
from agent_ready.adapters import (
    is_trace_eval_scorecard,
    plan_from_text,
    plan_from_trace_eval_json,
)
from agent_ready.mapper import plan_from_diagnose, plan_from_task
from agent_ready.plan import render_human, render_machine


def _read_source(source: str | None) -> str:
    if source is None or source == "-":
        return sys.stdin.read()
    return Path(source).read_text()


def _detect_and_plan(raw: str):
    """Auto-detect format. JSON → scorecard or synthetic diagnose; else raw text."""

    stripped = raw.strip()
    if stripped.startswith(("{", "[")):
        try:
            payload = json.loads(stripped)
        except json.JSONDecodeError:
            return plan_from_text(raw)
        if is_trace_eval_scorecard(payload):
            return plan_from_trace_eval_json(payload)
        if isinstance(payload, dict) and "errors" in payload and "verdict" in payload:
            return plan_from_diagnose(payload)
        # Fall back to flattening the JSON as text.
        return plan_from_text(raw)
    return plan_from_text(raw)


def _cmd_detect(args: argparse.Namespace) -> int:
    if args.task:
        plan = plan_from_task(args.task)
    else:
        raw = _read_source(args.source)
        plan = _detect_and_plan(raw)

    if args.json:
        print(json.dumps(render_machine(plan), indent=2))
    else:
        print(render_human(plan))

    return 0 if not plan.capabilities else 1


def _cmd_schema(_: argparse.Namespace) -> int:
    schema_dir = Path(__file__).parent.parent / "schema"
    print("agent-ready schemas:")
    print(f"  capability (JSON-Schema):      {schema_dir / 'capability.v1.json'}")
    print(f"  capabilities (registry data):  {schema_dir / 'capabilities.v1.json'}")
    print(f"  error-patterns (catalog):      {schema_dir / 'error-patterns.v1.json'}")
    print(f"  trace (internal input shape):  {schema_dir / 'trace.v1.json'}")
    return 0


def _cmd_status(_: argparse.Namespace) -> int:
    from agent_ready.registry import load_registry

    registry = load_registry()
    print(f"agent-ready {__version__} — {len(registry)} capabilities in registry:")
    for cap in registry.values():
        print(f"  • {cap.id:<20} {cap.name}")
    return 0


def _cmd_not_implemented(cmd: str):
    def inner(_: argparse.Namespace) -> int:
        print(f"agent-ready {cmd}: pending security review.", file=sys.stderr)
        print(
            "  This command runs installers and mutates the user's system. "
            "It is intentionally stubbed until the install path is reviewed. "
            "See docs/ARCHITECTURE.md § Safety.",
            file=sys.stderr,
        )
        return 2

    return inner


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="agent-ready",
        description="Detect what your AI agent is missing. Install it. Get ready.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    sub = parser.add_subparsers(dest="command", required=True)

    detect_p = sub.add_parser(
        "detect",
        help="Emit a capability plan from trace-eval scorecard, raw text, or a task phrase",
    )
    detect_p.add_argument(
        "--from", dest="source", help="Path to trace / scorecard / log (default: stdin)"
    )
    detect_p.add_argument(
        "--task", help="Plain-English task, e.g. 'deploy my site' (alternative to --from)"
    )
    detect_p.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    detect_p.set_defaults(func=_cmd_detect)

    fix_p = sub.add_parser("fix", help="(pending security review) Install and configure")
    fix_p.add_argument("--plan")
    fix_p.add_argument("--dry-run", action="store_true")
    fix_p.set_defaults(func=_cmd_not_implemented("fix"))

    verify_p = sub.add_parser("verify", help="(pending security review) Verify a capability")
    verify_p.add_argument("capability", nargs="?")
    verify_p.set_defaults(func=_cmd_not_implemented("verify"))

    undo_p = sub.add_parser("undo", help="(pending security review) Reverse an install")
    undo_p.add_argument("capability", nargs="?")
    undo_p.set_defaults(func=_cmd_not_implemented("undo"))

    status_p = sub.add_parser("status", help="List capabilities the registry knows about")
    status_p.set_defaults(func=_cmd_status)

    schema_p = sub.add_parser("schema", help="Print schema locations and versions")
    schema_p.set_defaults(func=_cmd_schema)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
