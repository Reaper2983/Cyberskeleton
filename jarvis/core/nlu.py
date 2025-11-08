"""A light-weight natural language understanding pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

import re


@dataclass
class Intent:
    """Represents the parsed intent of a user utterance."""

    name: str
    confidence: float
    entities: Dict[str, str]


class NLUPipeline:
    """Extremely small intent recogniser inspired by Pika AI capabilities."""

    def __init__(self) -> None:
        self._patterns = {
            "system.run": re.compile(r"^(run|execute|launch)\s+(?P<command>.+)", re.I),
            "tasks.add": re.compile(
                r"\b(remember|remind|add task|todo)\b(?P<task>.*)", re.I
            ),
            "tasks.list": re.compile(r"\b(list|show)\s+(my\s+)?(tasks|todos)\b", re.I),
            "knowledge.lookup": re.compile(r"\b(what is|who is|define)\b(?P<query>.*)", re.I),
            "weather.get": re.compile(r"\b(weather|forecast)\b(?P<location>.*)", re.I),
        }

    def parse(self, text: str) -> Optional[Intent]:
        normalized = text.strip()
        if not normalized:
            return None

        for name, pattern in self._patterns.items():
            match = pattern.search(normalized)
            if match:
                entities = {k: v.strip() for k, v in match.groupdict().items() if v}
                return Intent(name=name, confidence=0.8, entities=entities)

        if any(word in normalized.lower() for word in ["hi", "hello", "hey", "thanks"]):
            return Intent(name="social.chat", confidence=0.5, entities={})

        return None
