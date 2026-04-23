"""CLI for agent-ready.

`detect` is implemented. `fix`, `verify`, `undo` print a "pending security review"
message and exit non-zero — intentional, do not wire them to installers without review.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from agent_ready import __version__
from agent_ready.mapper import plan_from_diagnose, plan_from_task
from agent_ready.plan import render_human, render_machine


def _load_diagnose(source: str | None) -> dict:
    if source is None or source == "-":
        return json.loads(sys.stdin.read())
    return json.loads(Path(source).read_text())


def _cmd_detect(args: argparse.Namespace) -> int:
    if args.task:
        plan = plan_from_task(args.task)
    else:
        diagnose = _load_diagnose(args.source)
        plan = plan_from_diagnose(diagnose)

    if args.json:
        print(json.dumps(render_machine(plan), indent=2))
    else:
        print(render_human(plan))

    return 0 if not plan.capabilities else 1


def _cmd_schema(_: argparse.Namespace) -> int:
    schema_dir = Path(__file__).parent.parent / "schema"
    print("agent-ready schemas:")
    print(f"  capability (canonical): {schema_dir / 'capability.v1.json'}")
    print(f"  capabilities (registry): {schema_dir / 'capabilities.v1.json'}")
    print(f"  trace (mirrored from trace-eval): {schema_dir / 'trace.v1.json'}")
    print(f"  error-patterns (mirrored): {schema_dir / 'error-patterns.v1.json'}")
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
        print(
            f"agent-ready {cmd}: pending security review.",
            file=sys.stderr,
        )
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
        "detect", help="Read a trace-eval diagnose.json and emit a capability plan"
    )
    detect_p.add_argument("--from", dest="source", help="Path to diagnose.json (default: stdin)")
    detect_p.add_argument(
        "--task",
        help="Plain-English task description, e.g. 'deploy my site' (alternative to --from)",
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
