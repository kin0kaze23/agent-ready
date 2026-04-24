"""CLI for agent-ready.

`detect` is live — auto-detects text / trace-eval scorecard / synthetic diagnose.
`fix` / `verify` / `undo` are implemented — gated by per-capability approval.
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
from agent_ready.registry import by_id


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


def _cmd_fix(args: argparse.Namespace) -> int:
    from agent_ready.executor import execute_plan

    if args.task:
        plan = plan_from_task(args.task)
    elif args.source:
        raw = _read_source(args.source)
        plan = _detect_and_plan(raw)
    else:
        print("agent-ready fix: specify --task or --from <file>.", file=sys.stderr)
        return 1

    if not plan.capabilities:
        print("Nothing to set up.")
        return 0

    if args.dry_run:
        print("agent-ready (dry-run) — this is what I would do:\n")
        print(render_human(plan))
        return 0

    succeeded = execute_plan(plan, interactive=not args.non_interactive)
    return 0 if succeeded else 1


def _cmd_verify(args: argparse.Namespace) -> int:
    from agent_ready.executor import verify_capability

    if not args.capability:
        print("agent-ready verify: specify a capability ID.", file=sys.stderr)
        print("  e.g. agent-ready verify vercel_cli", file=sys.stderr)
        return 1

    cap = by_id(args.capability)
    if not cap:
        print(f"agent-ready verify: unknown capability '{args.capability}'.", file=sys.stderr)
        return 1

    ok = verify_capability(cap)
    return 0 if ok else 1


def _cmd_undo(args: argparse.Namespace) -> int:
    from agent_ready.executor import undo_capability

    if not args.capability:
        print("agent-ready undo: specify a capability ID.", file=sys.stderr)
        print("  e.g. agent-ready undo vercel_cli", file=sys.stderr)
        return 1

    cap = by_id(args.capability)
    if not cap:
        print(f"agent-ready undo: unknown capability '{args.capability}'.", file=sys.stderr)
        return 1

    ok = undo_capability(cap)
    return 0 if ok else 1


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

    fix_p = sub.add_parser("fix", help="Install and configure missing capabilities")
    fix_p.add_argument(
        "--from", dest="source", help="Path to trace / scorecard / log (default: stdin)"
    )
    fix_p.add_argument("--task", help="Plain-English task, e.g. 'deploy my site'")
    fix_p.add_argument(
        "--dry-run", action="store_true", help="Show the plan without running anything"
    )
    fix_p.add_argument(
        "--non-interactive", action="store_true", help="Skip user prompts (for scripting)"
    )
    fix_p.set_defaults(func=_cmd_fix)

    verify_p = sub.add_parser("verify", help="Verify a capability is working")
    verify_p.add_argument("capability", nargs="?", help="Capability ID, e.g. vercel_cli")
    verify_p.set_defaults(func=_cmd_verify)

    undo_p = sub.add_parser("undo", help="Remove what was installed")
    undo_p.add_argument("capability", nargs="?", help="Capability ID, e.g. vercel_cli")
    undo_p.set_defaults(func=_cmd_undo)

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
