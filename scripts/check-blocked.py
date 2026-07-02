#!/usr/bin/env python3
"""Watchdog script: checks the kanban board for blocked tasks and prints them."""
import json
import subprocess
import sys
from pathlib import Path

HERMES = "/opt/hermes/.venv/bin/python /opt/hermes/hermes_cli/main.py"
BOARD = "interactive-python-tutorials"

def run_cmd(cmd: str) -> str:
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
    return result.stdout.strip()

def main():
    # Get blocked tasks
    output = run_cmd(
        f'{HERMES} kanban list --board {BOARD} --tenant {BOARD} --status blocked --json'
    )
    
    if not output or output == "[]":
        # No blocked tasks - silent exit (nothing to report)
        sys.exit(0)

    try:
        tasks = json.loads(output)
    except json.JSONDecodeError:
        # Non-JSON output or error - stay quiet to avoid false alarms
        sys.exit(0)

    if not tasks:
        sys.exit(0)

    # We have blocked tasks - compose the alert
    lines = ["🚫 **Kanban Alert: Blocked Tasks Found**", "", "The following tasks are blocked and need attention:", ""]

    for t in tasks:
        tid = t.get("id", "?")
        title = t.get("title", "Untitled")
        assignee = t.get("assignee", "unassigned")
        created = t.get("created_at", "?")

        lines.append(f"• **{title}**")
        lines.append(f"  ID: `{tid}` | Assignee: {assignee}")
        
        # Show most recent comments/events for context
        events_output = run_cmd(
            f'{HERMES} kanban show {tid} --board {BOARD} 2>&1 | tail -20'
        )
        if events_output:
            lines.append(f"  Recent: {events_output[:300]}")
        lines.append("")

    lines.append("---")
    lines.append(f"Check the board: `hermes kanban list --board {BOARD} --tenant {BOARD}`")
    lines.append("To unblock: `hermes kanban unblock <task-id>`")

    print("\n".join(lines))

if __name__ == "__main__":
    main()
