"""Conversation state tracking for the Jarvis assistant."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, List, Literal, Sequence


Role = Literal["system", "user", "assistant"]


@dataclass
class Message:
    """A single message exchanged during the conversation."""

    role: Role
    content: str


@dataclass
class ConversationContext:
    """Maintains the rolling conversation history for Jarvis."""

    system_prompt: str
    max_messages: int = 8
    history: List[Message] = field(default_factory=list)

    def add_user_message(self, content: str) -> None:
        self._append(Message("user", content))

    def add_assistant_message(self, content: str) -> None:
        self._append(Message("assistant", content))

    def _append(self, message: Message) -> None:
        self.history.append(message)
        overflow = len(self.history) - self.max_messages
        if overflow > 0:
            del self.history[0:overflow]

    def clear(self) -> None:
        self.history.clear()

    def messages(self) -> List[Message]:
        return [Message("system", self.system_prompt), *self.history]

    def as_openai(self) -> List[dict]:
        return [{"role": m.role, "content": m.content} for m in self.messages()]

    def last_message(self) -> Message | None:
        return self.history[-1] if self.history else None
