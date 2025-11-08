"""Knowledge base skill for Jarvis."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional

from ..core.context import ConversationContext
from ..core.nlu import Intent


class KnowledgeSkill:
    name = "knowledge"
    description = "Answer questions using a lightweight local knowledge base."

    def __init__(self, knowledge_path: Optional[Path] = None) -> None:
        self._knowledge_path = knowledge_path or Path.home() / ".jarvis" / "knowledge.json"
        self._entries: Dict[str, str] = {}
        self._load()

    def _load(self) -> None:
        if self._knowledge_path.exists():
            try:
                with self._knowledge_path.open("r", encoding="utf-8") as handle:
                    data = json.load(handle)
                if isinstance(data, dict):
                    self._entries = {str(k).lower(): str(v) for k, v in data.items()}
            except json.JSONDecodeError:
                self._entries = {}

    def can_handle(self, intent: Optional[Intent], text: str) -> bool:
        return bool(intent and intent.name == "knowledge.lookup")

    def handle(self, intent: Optional[Intent], text: str, context: ConversationContext) -> str:
        if not intent:
            return "What would you like to know?"
        query = intent.entities.get("query") or text
        cleaned = query.strip().lower()
        if not cleaned:
            return "Please tell me what you would like to know."

        response = self._match(cleaned)
        if response:
            return response
        return (
            "I don't have that in my knowledge base yet. "
            "You can teach me by editing the JSON file at "
            f"{self._knowledge_path}"
        )

    def _match(self, cleaned: str) -> Optional[str]:
        if cleaned in self._entries:
            return self._entries[cleaned]
        for key, value in self._entries.items():
            if cleaned in key:
                return value
        return None
