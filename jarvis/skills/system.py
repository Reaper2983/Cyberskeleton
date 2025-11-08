"""System level skills such as executing safe commands."""

from __future__ import annotations

import platform
import subprocess
from pathlib import Path
from typing import Optional

from ..core.context import ConversationContext
from ..core.nlu import Intent


class SystemSkill:
    """Skill that can execute a small allow list of commands."""

    name = "system"
    description = "Execute safe local commands and report system status."

    ALLOWLIST = {
        "list": {"command": ["ls"], "description": "List files in the current directory."},
        "status": {
            "command": ["uptime"],
            "description": "Show system uptime (Linux/macOS).",
        },
        "open logs": {
            "command": ["tail", "-n", "50", "system.log"],
            "description": "Tail a generic log file (if present).",
        },
    }

    def can_handle(self, intent: Optional[Intent], text: str) -> bool:
        if intent and intent.name == "system.run":
            return True
        lowered = text.lower()
        return any(keyword in lowered for keyword in ["system", "computer", "status"])

    def handle(self, intent: Optional[Intent], text: str, context: ConversationContext) -> str:
        if intent and intent.name == "system.run":
            command_text = intent.entities.get("command", "").strip()
            return self._execute_custom_command(command_text)
        return self._system_status()

    def _execute_custom_command(self, command_text: str) -> str:
        if not command_text:
            return "I need a command to execute."

        for name, info in self.ALLOWLIST.items():
            if command_text.lower().startswith(name):
                try:
                    completed = subprocess.run(
                        info["command"],
                        capture_output=True,
                        text=True,
                        check=True,
                    )
                except FileNotFoundError:
                    return "Command is not available on this system."
                except subprocess.CalledProcessError as exc:
                    return f"The command exited with an error: {exc.stderr.strip()}"
                return completed.stdout.strip() or "Command executed successfully."

        return "For safety I only run predefined commands. Try 'list' or 'status'."

    def _system_status(self) -> str:
        system = platform.platform()
        cwd = Path.cwd()
        return (
            "System diagnostics:\n"
            f"- Platform: {system}\n"
            f"- Working directory: {cwd}\n"
            f"- Allowed commands: {', '.join(self.ALLOWLIST)}"
        )
