"""CLI auto-detection: scorecard / synthetic diagnose / raw text."""

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


def test_autodetect_raw_text_from_stdin():
    raw = (FIXTURES / "raw_trace_text.log").read_text()
    r = _run(["detect", "--json"], stdin=raw)
    assert r.returncode == 1
    payload = json.loads(r.stdout)
    ids = [c["id"] for c in payload["capabilities"]]
    assert "vercel_cli" in ids


def test_autodetect_trace_eval_scorecard():
    raw = (FIXTURES / "trace_eval_scorecard_synthetic.json").read_text()
    r = _run(["detect", "--json"], stdin=raw)
    assert r.returncode == 1
    payload = json.loads(r.stdout)
    ids = [c["id"] for c in payload["capabilities"]]
    assert "vercel_cli" in ids
    assert "github_cli" in ids


def test_autodetect_synthetic_diagnose():
    raw = (FIXTURES / "diagnose_vercel_missing.json").read_text()
    r = _run(["detect", "--json"], stdin=raw)
    assert r.returncode == 1
    payload = json.loads(r.stdout)
    ids = [c["id"] for c in payload["capabilities"]]
    assert "vercel_cli" in ids


def test_autodetect_unrecognized_json_falls_back_to_text():
    raw = '{"random": "json", "log": "command not found: vercel"}'
    r = _run(["detect", "--json"], stdin=raw)
    assert r.returncode == 1
    payload = json.loads(r.stdout)
    ids = [c["id"] for c in payload["capabilities"]]
    assert "vercel_cli" in ids


def test_autodetect_clean_text_returns_empty_plan():
    r = _run(["detect"], stdin="all good here, no errors\n")
    assert r.returncode == 0
    assert "nothing to do" in r.stdout.lower()
