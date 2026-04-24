"""Tests for the vercel_cli capability module.

Tests verify command strings and ordering, not actual installs.
CI cannot install software, so subprocess is mocked throughout.
"""

from __future__ import annotations

import subprocess
from unittest.mock import patch

from agent_ready.capabilities import vercel_cli


# --- detect ----------------------------------------------------------------


def _ok(returncode=0, stdout="1.0.0", stderr=""):
    return subprocess.CompletedProcess(
        args=[],
        returncode=returncode,
        stdout=stdout,
        stderr=stderr,
    )


def test_detect_returns_true_when_installed():
    with patch("agent_ready.sandbox.subprocess.run", return_value=_ok()):
        assert vercel_cli.detect() is True


def test_detect_returns_false_when_missing():
    with patch("agent_ready.sandbox.subprocess.run", return_value=_ok(returncode=127)):
        assert vercel_cli.detect() is False


# --- install ---------------------------------------------------------------


def test_install_runs_brew_on_mac():
    with (
        patch("agent_ready.capabilities.vercel_cli.get_os", return_value="mac"),
        patch("agent_ready.sandbox.subprocess.run", return_value=_ok()) as mock_run,
    ):
        assert vercel_cli.install() is True
        mock_run.assert_called_once()
        assert "brew install vercel-cli" in mock_run.call_args[0][0]


def test_install_runs_npm_on_linux():
    with (
        patch("agent_ready.capabilities.vercel_cli.get_os", return_value="linux"),
        patch("agent_ready.sandbox.subprocess.run", return_value=_ok()) as mock_run,
    ):
        assert vercel_cli.install() is True
        mock_run.assert_called_once()
        assert "npm install -g vercel" in mock_run.call_args[0][0]


def test_install_runs_npm_on_windows():
    with (
        patch("agent_ready.capabilities.vercel_cli.get_os", return_value="windows"),
        patch("agent_ready.sandbox.subprocess.run", return_value=_ok()) as mock_run,
    ):
        assert vercel_cli.install() is True
        mock_run.assert_called_once()
        assert "npm install -g vercel" in mock_run.call_args[0][0]


def test_install_returns_false_on_failure():
    with (
        patch("agent_ready.capabilities.vercel_cli.get_os", return_value="mac"),
        patch("agent_ready.sandbox.subprocess.run", return_value=_ok(returncode=1)),
    ):
        assert vercel_cli.install() is False


# --- auth ------------------------------------------------------------------


def test_auth_runs_vercel_login():
    with patch("agent_ready.sandbox.subprocess.run", return_value=_ok()) as mock_run:
        assert vercel_cli.auth() is True
        mock_run.assert_called_once()
        assert "vercel login" in mock_run.call_args[0][0]


def test_auth_returns_false_on_failure():
    with patch("agent_ready.sandbox.subprocess.run", return_value=_ok(returncode=1)):
        assert vercel_cli.auth() is False


# --- verify ----------------------------------------------------------------


def test_verify_runs_vercel_whoami():
    with patch("agent_ready.sandbox.subprocess.run", return_value=_ok()) as mock_run:
        assert vercel_cli.verify() is True
        mock_run.assert_called_once()
        assert "vercel whoami" in mock_run.call_args[0][0]


def test_verify_returns_false_when_not_authenticated():
    with patch("agent_ready.sandbox.subprocess.run", return_value=_ok(returncode=1)):
        assert vercel_cli.verify() is False


# --- undo ------------------------------------------------------------------


def test_undo_runs_brew_uninstall_on_mac():
    with (
        patch("agent_ready.capabilities.vercel_cli.get_os", return_value="mac"),
        patch("agent_ready.sandbox.subprocess.run") as mock_run,
    ):
        # First call: uninstall (succeeds), second call: detect (fails = tool removed)
        mock_run.side_effect = [
            _ok(),  # brew uninstall succeeds
            _ok(returncode=127),  # vercel --version fails (tool removed)
        ]
        assert vercel_cli.undo() is True
        calls = [c[0][0] for c in mock_run.call_args_list]
        assert "brew uninstall vercel-cli" in calls[0]


def test_undo_runs_npm_uninstall_on_linux():
    with (
        patch("agent_ready.capabilities.vercel_cli.get_os", return_value="linux"),
        patch("agent_ready.sandbox.subprocess.run") as mock_run,
    ):
        mock_run.side_effect = [
            _ok(),
            _ok(returncode=127),
        ]
        assert vercel_cli.undo() is True
        calls = [c[0][0] for c in mock_run.call_args_list]
        assert "npm uninstall -g vercel" in calls[0]


def test_undo_returns_false_if_uninstall_fails():
    with (
        patch("agent_ready.capabilities.vercel_cli.get_os", return_value="mac"),
        patch("agent_ready.sandbox.subprocess.run", return_value=_ok(returncode=1)),
    ):
        assert vercel_cli.undo() is False


def test_undo_returns_false_if_tool_still_present():
    with (
        patch("agent_ready.capabilities.vercel_cli.get_os", return_value="mac"),
        patch("agent_ready.sandbox.subprocess.run") as mock_run,
    ):
        mock_run.side_effect = [
            _ok(),  # uninstall succeeds
            _ok(),  # but detect also succeeds (tool still there!)
        ]
        assert vercel_cli.undo() is False
