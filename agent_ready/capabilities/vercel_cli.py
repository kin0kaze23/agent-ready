"""Vercel CLI capability module.

Implements the five lifecycle functions for the Vercel deployment tool.
Follows the security model from docs/SECURITY_REVIEW.md.
"""

from __future__ import annotations

from agent_ready.sandbox import get_os, run_step


def detect() -> bool:
    """Check if the Vercel deployment tool is already installed."""
    result = run_step("vercel --version", timeout=10)
    return result["exit_code"] == 0


def install() -> bool:
    """Install the Vercel deployment tool for the current OS."""
    os_name = get_os()
    commands = {
        "mac": "brew install vercel-cli",
        "linux": "npm install -g vercel",
        "windows": "npm install -g vercel",
    }
    command = commands.get(os_name)
    if not command:
        return False
    result = run_step(command, timeout=300)
    return result["exit_code"] == 0


def auth() -> bool:
    """Guide the user through signing in to their Vercel account.

    This opens an interactive login flow. The user must complete it
    in their browser. Returns True when the login command exits cleanly.
    """
    result = run_step("vercel login", timeout=300)
    return result["exit_code"] == 0


def verify() -> bool:
    """Prove the Vercel deployment tool is actually working.

    Runs 'vercel whoami' and checks that it returns successfully.
    A non-zero exit code means the tool is installed but not signed in.
    """
    result = run_step("vercel whoami", timeout=30)
    return result["exit_code"] == 0


def undo() -> bool:
    """Remove the Vercel deployment tool and clean up."""
    os_name = get_os()
    commands = {
        "mac": "brew uninstall vercel-cli",
        "linux": "npm uninstall -g vercel",
        "windows": "npm uninstall -g vercel",
    }
    command = commands.get(os_name)
    if not command:
        return False
    result = run_step(command, timeout=120)
    if result["exit_code"] != 0:
        return False
    # Prove removal: detect should now return False
    return not detect()
