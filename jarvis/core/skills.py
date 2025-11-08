"""Skill loading and management."""

from __future__ import annotations

from dataclasses import dataclass
from importlib import import_module
from typing import Iterable, List, Optional, Protocol

from .context import ConversationContext
from .nlu import Intent


class Skill(Protocol):
    """Protocol that all skills must implement."""

    name: str
    description: str

    def can_handle(self, intent: Optional[Intent], text: str) -> bool:
        ...

    def handle(self, intent: Optional[Intent], text: str, context: ConversationContext) -> str:
        ...

    def tool_spec(self) -> Optional[dict]:
        return None


@dataclass
class SkillLoader:
    """Utility to dynamically import skills from dotted paths."""

    module_path: str

    def load(self) -> Skill:
        module_name, _, attr = self.module_path.partition(":")
        if not attr:
            raise ValueError(
                "Skill definition must be of the form 'module:ClassName', "
                f"got {self.module_path}"
            )
        module = import_module(module_name)
        skill_cls = getattr(module, attr)
        return skill_cls()


def load_skills(paths: Iterable[str]) -> List[Skill]:
    return [SkillLoader(path).load() for path in paths]
