"""CLI entrypoint for agent-ready. Placeholder — no implementation yet."""

from __future__ import annotations

import argparse
import sys

from agent_ready import __version__


def main():
    parser = argparse.ArgumentParser(
        prog="agent-ready",
        description="Detect what your AI agent is missing. Install it. Get ready.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # check
    sub.add_parser("check", help="Detect missing capabilities for your tasks")

    # fix
    sub.add_parser("fix", help="Install missing tools and guide setup")

    # status
    sub.add_parser("status", help="Show current agent capabilities")

    args = parser.parse_args()

    print("agent-ready is pre-alpha. No implementation yet.", file=sys.stderr)
    print("Phase 1 will be built based on trace-eval alpha user data.", file=sys.stderr)
    print(f"Version: {__version__}")

    sys.exit(1)


if __name__ == "__main__":
    main()
