"""Generic capability lifecycle executor.

All 5 lifecycle functions (detect, install, auth, verify, undo) are driven
entirely from the schema data in capabilities.v1.json. Adding a new capability
requires NO Python code — just a JSON entry in the registry.

This makes agent-ready self-extending: the schema IS the implementation.
"""

from __future__ import annotations

from agent_ready.models import Capability
from agent_ready.sandbox import get_os, run_step


def lifecycle_detect(cap: Capability) -> bool:
    """Check if a capability is already installed, using its schema detect config."""
    detect_cfg = cap.detect
    strategy = detect_cfg.get("strategy", "command_exit_zero")

    if strategy == "command_exit_zero":
        command = detect_cfg.get("command")
        if not command:
            return False
        result = run_step(command, timeout=10)
        return result["exit_code"] == 0

    if strategy == "env_var_set":
        env_var = detect_cfg.get("env_var")
        if not env_var:
            return False
        import os

        return bool(os.environ.get(env_var))

    if strategy == "file_exists":
        from pathlib import Path

        path = detect_cfg.get("path")
        if not path:
            return False
        return Path(path).exists()

    if strategy == "http_200":
        url = detect_cfg.get("url")
        if not url:
            return False
        try:
            import urllib.request

            resp = urllib.request.urlopen(url, timeout=5)
            return resp.status == 200
        except Exception:
            return False

    # Unknown strategy — fall back to command check
    return False


def lifecycle_install(cap: Capability) -> bool:
    """Install a capability using its schema install commands for the current OS."""
    install_cfg = cap.install
    if not install_cfg:
        return False
    os_name = get_os()
    command = install_cfg.get(os_name)
    if not command:
        return False
    result = run_step(command, timeout=300)
    return result["exit_code"] == 0


def lifecycle_auth(cap: Capability) -> bool:
    """Run the authentication flow for a capability using its schema auth_command."""
    command = cap.auth_command
    if not command:
        return True  # No auth needed
    result = run_step(command, timeout=300)
    return result["exit_code"] == 0


def lifecycle_verify(cap: Capability) -> bool:
    """Verify a capability is working using its schema verify config."""
    verify_cfg = cap.verify
    if not verify_cfg:
        return True  # No verification defined
    command = verify_cfg.get("command")
    if not command:
        return True
    result = run_step(command, timeout=30)
    expected_code = verify_cfg.get("exit_code", 0)
    return result["exit_code"] == expected_code


def lifecycle_undo(cap: Capability) -> bool:
    """Undo a capability installation using its schema undo commands for the current OS."""
    undo_cfg = cap.undo
    if not undo_cfg:
        return False
    os_name = get_os()
    command = undo_cfg.get(os_name)
    if not command:
        return False
    result = run_step(command, timeout=120)
    if result["exit_code"] != 0:
        return False
    # Prove removal: detect should now return False
    return not lifecycle_detect(cap)
