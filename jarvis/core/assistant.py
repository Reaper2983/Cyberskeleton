"""Jarvis-like assistant core orchestration."""

from __future__ import annotations

from typing import Optional

from ..config import AssistantConfig, ensure_data_dirs
from ..core.context import ConversationContext
from ..core.nlu import Intent, NLUPipeline
from ..core.skills import load_skills
from ..integrations.openai_client import build_chat_model, context_to_messages


class JarvisAssistant:
    """High level orchestrator gluing together NLU, skills and the LLM."""

    def __init__(self, config: Optional[AssistantConfig] = None) -> None:
        self.config = config or AssistantConfig()
        ensure_data_dirs(self.config)
        self.context = ConversationContext(
            system_prompt=self.config.persona,
            max_messages=self.config.memory.conversation_history,
        )
        self.nlu = NLUPipeline()
        self.skills = load_skills(self.config.skill_modules)
        provider = self.config.model.provider
        self.using_fallback_model = False
        try:
            self.model = build_chat_model(
                provider=provider,
                model=self.config.model.model,
                temperature=self.config.model.temperature,
                max_output_tokens=self.config.model.max_output_tokens,
                persona=self.config.persona,
            )
        except Exception:
            self.using_fallback_model = True
            self.model = build_chat_model(
                provider="local-echo",
                model=self.config.model.model,
                temperature=self.config.model.temperature,
                max_output_tokens=self.config.model.max_output_tokens,
                persona=self.config.persona,
            )

    def _route_to_skill(self, intent: Optional[Intent], text: str) -> Optional[str]:
        for skill in self.skills:
            if skill.can_handle(intent, text):
                return skill.handle(intent, text, self.context)
        return None

    def _llm_response(self, text: str) -> str:
        self.context.add_user_message(text)
        messages = context_to_messages(self.context)
        reply = self.model.generate(messages)
        self.context.add_assistant_message(reply)
        return reply

    def handle_text(self, text: str) -> str:
        intent = self.nlu.parse(text)
        skill_response = self._route_to_skill(intent, text)
        if skill_response:
            self.context.add_user_message(text)
            self.context.add_assistant_message(skill_response)
            return skill_response
        return self._llm_response(text)

    def reset(self) -> None:
        self.context.clear()
