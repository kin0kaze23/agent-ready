"""Tests for the MCP server tools.

Tests verify that each tool returns the correct shape and data,
without actually starting the MCP server process.
"""

from __future__ import annotations

from agent_ready.mcp_server import detect, fix, verify, undo, status


# --- detect ----------------------------------------------------------------


def test_detect_from_task_finds_vercel():
    result = detect(task="deploy my portfolio to production")
    assert result["found"] >= 1
    ids = [item["id"] for item in result["items"]]
    assert "vercel_cli" in ids


def test_detect_from_task_returns_empty_for_unknown():
    result = detect(task="bake a chocolate cake")
    assert result["found"] == 0
    assert result["items"] == []


def test_detect_from_log_finds_tools():
    result = detect(log="command not found: vercel\ncommand not found: gh")
    assert result["found"] >= 1


def test_detect_with_no_args_returns_message():
    result = detect()
    assert result["found"] == 0
    assert "Provide a task" in result["message"]


# --- fix -------------------------------------------------------------------


def test_fix_preview_returns_steps():
    result = fix(task="deploy my portfolio", approve=False)
    assert result["status"] == "preview"
    assert len(result["capabilities"]) >= 1
    # Each tool should have a list of steps
    for tool in result["capabilities"]:
        assert isinstance(tool["steps"], list)


def test_fix_empty_returns_ok():
    result = fix(task="bake a chocolate cake", approve=False)
    assert result["status"] == "ok"
    assert "Nothing to set up" in result["message"]


def test_fix_requires_task_or_log():
    result = fix()
    assert result["status"] == "error"
    assert "Provide a task" in result["message"]


# --- verify ----------------------------------------------------------------


def test_verify_vercel_returns_working_status():
    result = verify("vercel_cli")
    assert "tool_id" in result
    assert result["tool_id"] == "vercel_cli"
    assert "working" in result
    assert "message" in result


def test_verify_unknown_tool_returns_error():
    result = verify("not_a_real_tool")
    assert result["status"] == "error"
    assert "don't know about" in result["message"]


# --- undo ------------------------------------------------------------------


def test_undo_unknown_tool_returns_error():
    result = undo("not_a_real_tool")
    assert result["status"] == "error"
    assert "don't know about" in result["message"]


# --- status ----------------------------------------------------------------


def test_status_returns_library_count():
    result = status()
    assert result["total"] >= 5
    assert "installed" in result
    assert "tools" in result
    assert len(result["tools"]) == result["total"]


def test_status_each_tool_has_required_fields():
    result = status()
    for tool in result["tools"]:
        assert "id" in tool
        assert "description" in tool
        assert "installed" in tool
        assert isinstance(tool["installed"], bool)
