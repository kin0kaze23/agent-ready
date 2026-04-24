"""End-to-end CLI tests."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

FIXTURES = Path(__file__).parent / "fixtures"


def _run(args: list[str], stdin: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "agent_ready.cli", *args],
        capture_output=True,
        text=True,
        input=stdin,
    )


def test_help_runs():
    r = _run(["--help"])
    assert r.returncode == 0
    assert "Detect what your AI agent is missing" in r.stdout


def test_detect_from_file_prints_plan():
    r = _run(["detect", "--from", str(FIXTURES / "diagnose_vercel_missing.json")])
    assert r.returncode == 1  # non-zero — there's something to fix
    assert "Vercel CLI" in r.stdout


def test_detect_from_stdin():
    raw = (FIXTURES / "diagnose_vercel_missing.json").read_text()
    r = _run(["detect", "--json"], stdin=raw)
    assert r.returncode == 1
    payload = json.loads(r.stdout)
    assert payload["capabilities"][0]["id"] == "vercel_cli"


def test_detect_from_task_phrase():
    r = _run(["detect", "--task", "deploy the portfolio"])
    assert r.returncode == 1
    assert "Vercel" in r.stdout


def test_detect_clean_diagnose_returns_zero():
    r = _run(["detect", "--from", str(FIXTURES / "diagnose_clean.json")])
    assert r.returncode == 0
    assert "nothing to do" in r.stdout.lower()


def test_status_lists_registry():
    r = _run(["status"])
    assert r.returncode == 0
    assert "vercel_cli" in r.stdout
    assert "github_cli" in r.stdout


def test_schema_prints_paths():
    r = _run(["schema"])
    assert r.returncode == 0
    assert "capability.v1.json" in r.stdout


def test_fix_requires_task_or_from():
    r = _run(["fix"])
    assert r.returncode == 1
    assert "specify --task or --from" in r.stderr


def test_verify_requires_capability_arg():
    r = _run(["verify"])
    assert r.returncode == 1
    assert "specify a capability ID" in r.stderr


def test_undo_requires_capability_arg():
    r = _run(["undo"])
    assert r.returncode == 1
    assert "specify a capability ID" in r.stderr
