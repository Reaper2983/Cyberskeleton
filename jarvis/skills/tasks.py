"""Simple persistent task manager skill."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from ..config import AssistantConfig
from ..core.context import ConversationContext
from ..core.nlu import Intent


@dataclass
class TaskManager:
    storage_path: Path
    tasks: List[str] = field(default_factory=list)

    def load(self) -> None:
        if self.storage_path.exists():
            with self.storage_path.open("r", encoding="utf-8") as handle:
                data = json.load(handle)
            if isinstance(data, list):
                self.tasks = [str(item) for item in data]

    def save(self) -> None:
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        with self.storage_path.open("w", encoding="utf-8") as handle:
            json.dump(self.tasks, handle, indent=2)

    def add(self, description: str) -> None:
        if description:
            self.tasks.append(description)
            self.save()

    def list_tasks(self) -> List[str]:
        return list(self.tasks)


class TaskSkill:
    name = "tasks"
    description = "Manage reminders and todos."

    def __init__(self, storage_path: Optional[Path] = None) -> None:
        if storage_path is None:
            storage_path = AssistantConfig().memory.persistent_tasks_path
        self._manager = TaskManager(storage_path=storage_path)
        try:
            self._manager.load()
        except json.JSONDecodeError:
            self._manager.tasks = []

    def can_handle(self, intent: Optional[Intent], text: str) -> bool:
        return bool(intent and intent.name.startswith("tasks."))

    def handle(self, intent: Optional[Intent], text: str, context: ConversationContext) -> str:
        if not intent:
            return "I need more detail to manage tasks."
        if intent.name == "tasks.add":
            task = intent.entities.get("task") or text
            self._manager.add(task.strip())
            return f"Task recorded: {task.strip()}"
        if intent.name == "tasks.list":
            tasks = self._manager.list_tasks()
            if not tasks:
                return "You have no tasks yet."
            return "Here are your tasks:\n" + "\n".join(f"- {task}" for task in tasks)
        return "I couldn't process that task request."
