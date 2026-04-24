"""Controlled subprocess runner for capability installers.

All installer commands flow through here — never directly to the shell.
Implements the security model from docs/SECURITY_REVIEW.md:
  * Restricted environment (no inherited secrets)
  * Timeout on every command
  * sudo blocked (never automatic)
  * Captured output for logging and undo
"""

from __future__ import annotations

import os
import subprocess

# Environment variables that must never be passed to installer subprocesses.
_SENSITIVE_PREFIXES = (
    "API_KEY",
    "SECRET",
    "TOKEN",
    "PASSWORD",
    "CREDENTIAL",
    "PRIVATE_KEY",
    "AUTH",
)


def _is_sensitive(key: str) -> bool:
    upper = key.upper()
    return any(prefix in upper for prefix in _SENSITIVE_PREFIXES)


def _safe_env() -> dict[str, str]:
    """Return a copy of the current environment with sensitive variables removed."""
    return {k: v for k, v in os.environ.items() if not _is_sensitive(k)}


class SecurityError(Exception):
    """Raised when a command violates security policy (e.g. requires sudo)."""


def run_step(command: str, timeout: int = 120) -> dict:
    """Run a single installer command in a controlled subshell.

    Args:
        command: The shell command to run.
        timeout: Maximum seconds before the command is killed.

    Returns:
        dict with keys: exit_code, stdout, stderr

    Raises:
        SecurityError: If the command requires sudo (blocked by policy).
        subprocess.TimeoutExpired: If the command exceeds the timeout.
    """
    if command.strip().startswith("sudo "):
        raise SecurityError(
            "This step needs system-level access. "
            "agent-ready will not run sudo automatically. "
            f"Please run this command yourself in your terminal:\n\n  {command}"
        )

    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True,
        timeout=timeout,
        env=_safe_env(),
    )
    return {
        "exit_code": result.returncode,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
    }


def get_os() -> str:
    """Return the current OS identifier: 'mac', 'linux', or 'windows'."""
    import platform

    system = platform.system().lower()
    if system == "darwin":
        return "mac"
    if system == "linux":
        return "linux"
    return "windows"
