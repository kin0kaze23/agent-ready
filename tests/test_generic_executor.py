"""Tests for the generic capability lifecycle executor.

Verifies that all lifecycle functions work correctly when driven
from schema data — no per-capability Python code needed.
"""

from __future__ import annotations

from unittest.mock import patch

from agent_ready.capabilities.generic import (
    lifecycle_detect,
    lifecycle_install,
    lifecycle_auth,
    lifecycle_verify,
    lifecycle_undo,
)
from agent_ready.registry import by_id


def _run_result(exit_code=0, stdout="1.0.0", stderr=""):
    """Return a dict like sandbox.run_step() does."""
    return {"exit_code": exit_code, "stdout": stdout, "stderr": stderr}


# --- detect ----------------------------------------------------------------


def test_detect_command_exit_zero_installed():
    cap = by_id("vercel_cli")
    with patch("agent_ready.capabilities.generic.run_step", return_value=_run_result()):
        assert lifecycle_detect(cap) is True


def test_detect_command_exit_zero_missing():
    cap = by_id("vercel_cli")
    with patch(
        "agent_ready.capabilities.generic.run_step", return_value=_run_result(exit_code=127)
    ):
        assert lifecycle_detect(cap) is False


def test_detect_env_var_set_missing():
    cap = by_id("api_key_config")
    # api_key_config uses env_var_set strategy but has empty env_var
    # so it returns False because env_var is empty string (falsy)
    assert lifecycle_detect(cap) is False


# --- install ---------------------------------------------------------------


def test_install_runs_os_specific_command():
    cap = by_id("github_cli")
    with (
        patch("agent_ready.capabilities.generic.get_os", return_value="mac"),
        patch("agent_ready.capabilities.generic.run_step", return_value=_run_result()) as mock_run,
    ):
        assert lifecycle_install(cap) is True
        assert "brew install gh" in mock_run.call_args[0][0]


def test_install_linux_command():
    cap = by_id("nodejs")
    with (
        patch("agent_ready.capabilities.generic.get_os", return_value="linux"),
        patch("agent_ready.capabilities.generic.run_step", return_value=_run_result()) as mock_run,
    ):
        assert lifecycle_install(cap) is True
        assert "sudo apt install nodejs npm" in mock_run.call_args[0][0]


def test_install_failure_returns_false():
    cap = by_id("vercel_cli")
    with (
        patch("agent_ready.capabilities.generic.get_os", return_value="mac"),
        patch("agent_ready.capabilities.generic.run_step", return_value=_run_result(exit_code=1)),
    ):
        assert lifecycle_install(cap) is False


def test_install_no_config_returns_false():
    cap = by_id("api_key_config")
    assert lifecycle_install(cap) is False  # api_key_config has no install config


# --- auth ------------------------------------------------------------------


def test_auth_runs_command():
    cap = by_id("github_cli")
    with patch("agent_ready.capabilities.generic.run_step", return_value=_run_result()) as mock_run:
        assert lifecycle_auth(cap) is True
        assert "gh auth login" in mock_run.call_args[0][0]


def test_auth_no_command_returns_true():
    cap = by_id("nodejs")
    assert lifecycle_auth(cap) is True  # nodejs has no auth_command


# --- verify ----------------------------------------------------------------


def test_verify_runs_command():
    cap = by_id("vercel_cli")
    with patch("agent_ready.capabilities.generic.run_step", return_value=_run_result()) as mock_run:
        assert lifecycle_verify(cap) is True
        assert "vercel whoami" in mock_run.call_args[0][0]


def test_verify_no_command_returns_true():
    cap = by_id("api_key_config")
    assert lifecycle_verify(cap) is True  # api_key_config has no verify command


def test_verify_failure_returns_false():
    cap = by_id("vercel_cli")
    with patch("agent_ready.capabilities.generic.run_step", return_value=_run_result(exit_code=1)):
        assert lifecycle_verify(cap) is False


# --- undo ------------------------------------------------------------------


def test_undo_runs_os_specific_command():
    cap = by_id("github_cli")
    with (
        patch("agent_ready.capabilities.generic.get_os", return_value="mac"),
        patch("agent_ready.capabilities.generic.run_step") as mock_run,
    ):
        mock_run.side_effect = [
            _run_result(),  # uninstall succeeds
            _run_result(exit_code=127),  # detect confirms removal
        ]
        assert lifecycle_undo(cap) is True
        assert "brew uninstall gh" in mock_run.call_args_list[0][0][0]


def test_undo_failure_returns_false():
    cap = by_id("vercel_cli")
    with (
        patch("agent_ready.capabilities.generic.get_os", return_value="mac"),
        patch("agent_ready.capabilities.generic.run_step", return_value=_run_result(exit_code=1)),
    ):
        assert lifecycle_undo(cap) is False


# --- all capabilities in registry work generically -------------------------


def test_all_capabilities_have_working_detect():
    """Every capability in the registry should have a working detect() call."""
    from agent_ready.registry import load_registry

    for cap in load_registry().values():
        with patch("agent_ready.capabilities.generic.run_step", return_value=_run_result()):
            result = lifecycle_detect(cap)
            assert isinstance(result, bool)
