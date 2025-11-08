"""Wrapper around the OpenAI API with graceful degradation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List

import importlib
import os

from ..core.context import ConversationContext


@dataclass
class ChatMessage:
    role: str
    content: str


class ChatModel:
    """Minimal interface for chat-completion style models."""

    def generate(self, messages: List[ChatMessage]) -> str:
        raise NotImplementedError


class OpenAIChatModel(ChatModel):
    """Thin wrapper around the OpenAI Python SDK."""

    def __init__(self, model: str, temperature: float = 0.7, max_output_tokens: int = 512) -> None:
        if importlib.util.find_spec("openai") is None:
            raise RuntimeError(
                "The 'openai' package is not installed. Install it or use the "
                "LocalEchoModel."
            )
        from openai import OpenAI  # type: ignore

        self._client = OpenAI()
        self._model = model
        self._temperature = temperature
        self._max_output_tokens = max_output_tokens

    def generate(self, messages: List[ChatMessage]) -> str:
        response = self._client.chat.completions.create(
            model=self._model,
            temperature=self._temperature,
            max_tokens=self._max_output_tokens,
            messages=[m.__dict__ for m in messages],
        )
        choice = response.choices[0].message
        return choice.content or ""


class LocalEchoModel(ChatModel):
    """Fallback model that simply echoes requests with a persona."""

    def __init__(self, persona: str) -> None:
        self._persona = persona

    def generate(self, messages: List[ChatMessage]) -> str:
        last_user = next((m.content for m in reversed(messages) if m.role == "user"), "")
        return (
            f"{self._persona}\n\n"
            f"I am operating in fallback mode because no language model is configured. "
            f"You asked: '{last_user}'. I recommend configuring an OpenAI API key "
            f"or another backend for richer responses."
        )


def build_chat_model(provider: str, model: str, temperature: float, max_output_tokens: int, persona: str) -> ChatModel:
    provider = provider.lower()
    if provider == "openai":
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY environment variable is required for OpenAI provider")
        return OpenAIChatModel(model=model, temperature=temperature, max_output_tokens=max_output_tokens)
    if provider == "local-echo":
        return LocalEchoModel(persona=persona)
    raise ValueError(f"Unknown model provider '{provider}'")


def context_to_messages(context: ConversationContext) -> List[ChatMessage]:
    return [ChatMessage(role=m.role, content=m.content) for m in context.messages()]
