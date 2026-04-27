"""MCP server for agent-ready.

Exposes four tools to AI agents:
  - vibedev.ready.detect  — scan a task or log for missing capabilities
  - vibedev.ready.fix     — install and configure missing capabilities
  - vibedev.ready.verify  — check if a capability is working
  - vibedev.ready.undo    — remove what was installed

Uses stdio transport so AI agents (Claude Code, Cursor, Codex CLI) can
call these tools natively as subprocess servers.
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from agent_ready.mapper import plan_from_task
from agent_ready.adapters.text import plan_from_text
from agent_ready.plan import render_machine
from agent_ready.executor import verify_capability, undo_capability
from agent_ready.registry import by_id, load_registry

mcp = FastMCP(
    "agent-ready",
    json_response=True,
)


@mcp.tool()
def detect(task: str = "", log: str = "") -> dict:
    """Find what's missing for a task or from an agent session log.

    Args:
        task: A plain-English description of what you're trying to do,
              e.g. "deploy my portfolio to production".
        log: Raw text from an agent session showing errors or failures.

    Provide one of task or log (not both). If both are provided, task takes priority.

    Returns:
        A dict with:
        - found: number of missing capabilities detected
        - items: list of missing capabilities with plain-English descriptions
        - needs_action: whether any user approval steps are needed
        - plan: the full machine-readable plan (for agent consumption)
    """
    if task:
        plan = plan_from_task(task)
    elif log:
        plan = plan_from_text(log)
    else:
        return {
            "found": 0,
            "items": [],
            "needs_action": False,
            "message": "Provide a task description or session log to scan.",
        }

    result = render_machine(plan)
    return {
        "found": len(result["capabilities"]),
        "items": [
            {
                "id": c["id"],
                "description": c["plain_english"],
                "needs_user_action": c["requires_user_action"],
            }
            for c in result["capabilities"]
        ],
        "needs_action": result["requires_user_action"],
        "plan": result,
    }


@mcp.tool()
def fix(task: str = "", log: str = "", approve: bool = False) -> dict:
    """Install and configure everything that's missing for a task.

    This is the full setup flow: install tools → create accounts → sign in → verify.

    Args:
        task: A plain-English description of what you're trying to do,
              e.g. "deploy my portfolio to production".
        log: Raw text from an agent session showing errors or failures.
        approve: Set to True to proceed with installation without interactive prompts.
                 When False, returns a preview of what would be installed instead.

    Provide one of task or log (not both). If both are provided, task takes priority.

    Returns:
        When approve=False: a preview of what would be set up.
        When approve=True: results for each capability with success/failure status.
    """
    if task:
        plan = plan_from_task(task)
    elif log:
        plan = plan_from_text(log)
    else:
        return {
            "status": "error",
            "message": "Provide a task description or session log.",
        }

    if not plan.capabilities:
        return {
            "status": "ok",
            "message": "Nothing to set up — everything is ready.",
            "capabilities": [],
        }

    if not approve:
        items = [
            {
                "id": c.id,
                "description": c.plain_english,
                "steps": _steps_for(c),
            }
            for c in plan.capabilities
        ]
        return {
            "status": "preview",
            "message": f"I can set up {len(plan.capabilities)} thing(s). Call fix again with approve=True to proceed.",
            "capabilities": items,
        }

    # Execute the full setup flow
    results = []
    all_succeeded = True
    for cap in plan.capabilities:
        from agent_ready.executor import InstallOrchestrator

        orchestrator = InstallOrchestrator(cap, interactive=False)
        succeeded = orchestrator.run()
        results.append(
            {
                "id": cap.id,
                "description": cap.plain_english,
                "status": "done" if succeeded else "failed",
                "steps_completed": len(orchestrator.tracker.completed),
            }
        )
        if not succeeded:
            all_succeeded = False

    return {
        "status": "done" if all_succeeded else "partial",
        "message": (
            "Everything is set up."
            if all_succeeded
            else "Some items did not finish setting up. Run verify to check."
        ),
        "capabilities": results,
    }


@mcp.tool()
def verify(capability_id: str) -> dict:
    """Check if a specific capability is installed and working.

    Args:
        capability_id: The tool identifier, e.g. "vercel_cli", "github_cli", "nodejs".

    Returns:
        A dict with:
        - capability_id: the tool that was checked
        - description: plain-English description of what it does
        - working: True if the tool is installed and verified
        - message: human-readable status
    """
    cap = by_id(capability_id)
    if not cap:
        available = list(load_registry().keys())
        return {
            "status": "error",
            "message": f"I don't know about '{capability_id}'. Available: {', '.join(available)}",
        }

    ok = verify_capability(cap)
    return {
        "capability_id": capability_id,
        "description": cap.plain_english,
        "working": ok,
        "message": f"{cap.plain_english} is working."
        if ok
        else f"{cap.plain_english} needs attention.",
    }


@mcp.tool()
def undo(capability_id: str) -> dict:
    """Remove a capability that was previously installed.

    This reverses the install, cleans up configuration, and verifies removal.

    Args:
        capability_id: The tool identifier, e.g. "vercel_cli", "github_cli".

    Returns:
        A dict with:
        - capability_id: the tool that was removed
        - description: plain-English description
        - removed: True if successfully removed
        - message: human-readable status
    """
    cap = by_id(capability_id)
    if not cap:
        available = list(load_registry().keys())
        return {
            "status": "error",
            "message": f"I don't know about '{capability_id}'. Available: {', '.join(available)}",
        }

    ok = undo_capability(cap)
    return {
        "capability_id": capability_id,
        "description": cap.plain_english,
        "removed": ok,
        "message": f"{cap.plain_english} has been removed."
        if ok
        else f"Could not remove {cap.plain_english.lower()}.",
    }


@mcp.tool()
def status() -> dict:
    """List all available capabilities and whether they are installed.

    Returns:
        A dict with:
        - total: number of capabilities in the registry
        - installed: number of capabilities currently installed and working
        - capabilities: list of all capabilities with their install status
    """
    capabilities = []
    installed_count = 0
    for cap in load_registry().values():
        from agent_ready.sandbox import run_step

        cmd = cap.detect.get("command", "")
        if cmd:
            result = run_step(cmd, timeout=10)
            is_installed = result["exit_code"] == 0
        else:
            is_installed = False

        if is_installed:
            installed_count += 1

        capabilities.append(
            {
                "id": cap.id,
                "description": cap.plain_english,
                "installed": is_installed,
            }
        )

    return {
        "total": len(capabilities),
        "installed": installed_count,
        "capabilities": capabilities,
    }


def _steps_for(cap) -> list[str]:
    """Return the list of setup steps for a capability in plain English."""
    steps = []
    if cap.install:
        steps.append("install the tool")
    if cap.requires_account:
        steps.append("create an account")
    if cap.requires_auth:
        steps.append("sign in")
    if cap.verify:
        steps.append("verify it works")
    return steps


def main():
    """Entry point for running the MCP server via stdio."""
    mcp.run()


if __name__ == "__main__":
    main()
