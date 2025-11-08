"""Configuration utilities for the Jarvis-like assistant."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

import os
import yaml


CONFIG_ENV_VAR = "JARVIS_CONFIG"
DEFAULT_CONFIG_PATH = Path("jarvis.yaml")


@dataclass
class ModelConfig:
    """Model configuration for the language model backend."""

    provider: str = "openai"
    model: str = "gpt-4o-mini"
    temperature: float = 0.6
    max_output_tokens: int = 512


@dataclass
class AudioConfig:
    """Audio input/output configuration."""

    enable_voice: bool = False
    wake_word: Optional[str] = "jarvis"
    input_device: Optional[str] = None
    output_device: Optional[str] = None
    rate: int = 16000
    volume: float = 1.0


@dataclass
class MemoryConfig:
    """Settings for how Jarvis stores and recalls information."""

    conversation_history: int = 8
    knowledge_base: Optional[Path] = None
    persistent_tasks_path: Path = Path.home() / ".jarvis" / "tasks.json"


PERSONA_PROMPT = (
    "You are Jarvis, a composed, helpful AI butler inspired by Marvel's Iron "
    "Man. You speak succinctly but with warmth, and always aim to provide "
    "actionable assistance."
)


@dataclass
class AssistantConfig:
    """Top level configuration for the Jarvis assistant."""

    name: str = "Jarvis"
    persona: str = PERSONA_PROMPT
    model: ModelConfig = field(default_factory=ModelConfig)
    audio: AudioConfig = field(default_factory=AudioConfig)
    memory: MemoryConfig = field(default_factory=MemoryConfig)
    skill_modules: List[str] = field(
        default_factory=lambda: [
            "jarvis.skills.system:SystemSkill",
            "jarvis.skills.tasks:TaskSkill",
            "jarvis.skills.knowledge:KnowledgeSkill",
            "jarvis.skills.weather:WeatherSkill",
        ]
    )
    tools_enabled: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "persona": self.persona,
            "model": vars(self.model),
            "audio": vars(self.audio),
            "memory": {
                "conversation_history": self.memory.conversation_history,
                "knowledge_base": str(self.memory.knowledge_base)
                if self.memory.knowledge_base
                else None,
                "persistent_tasks_path": str(self.memory.persistent_tasks_path),
            },
            "skill_modules": list(self.skill_modules),
            "tools_enabled": self.tools_enabled,
        }


def _merge_dict(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    result = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            result[key] = _merge_dict(base[key], value)
        else:
            result[key] = value
    return result


def _load_yaml(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Configuration file {path} must contain a mapping")
    return data


def _env_overrides(prefix: str = "JARVIS_") -> Dict[str, Any]:
    overrides: Dict[str, Any] = {}
    for key, value in os.environ.items():
        if not key.startswith(prefix):
            continue
        path = key[len(prefix) :].lower().split("__")
        cursor = overrides
        for part in path[:-1]:
            cursor = cursor.setdefault(part, {})
        cursor[path[-1]] = value
    return overrides


def load_config(path: Optional[Path] = None) -> AssistantConfig:
    """Load configuration from YAML and environment overrides."""

    if path is None:
        env_path = os.environ.get(CONFIG_ENV_VAR)
        if env_path:
            path = Path(env_path)
        else:
            path = DEFAULT_CONFIG_PATH

    file_data = _load_yaml(path)
    env_data = _env_overrides()
    combined = _merge_dict(file_data, env_data)

    model = ModelConfig(**combined.get("model", {}))
    audio_cfg = AudioConfig(**combined.get("audio", {}))
    memory_cfg_dict = combined.get("memory", {})
    memory_cfg = MemoryConfig(
        conversation_history=int(memory_cfg_dict.get("conversation_history", 8)),
        knowledge_base=Path(memory_cfg_dict["knowledge_base"])
        if memory_cfg_dict.get("knowledge_base")
        else None,
        persistent_tasks_path=Path(memory_cfg_dict.get("persistent_tasks_path", MemoryConfig().persistent_tasks_path)),
    )

    defaults = AssistantConfig()

    return AssistantConfig(
        name=combined.get("name", defaults.name),
        persona=combined.get("persona", defaults.persona),
        model=model,
        audio=audio_cfg,
        memory=memory_cfg,
        skill_modules=list(combined.get("skill_modules", defaults.skill_modules)),
        tools_enabled=bool(combined.get("tools_enabled", True)),
    )


def ensure_data_dirs(config: AssistantConfig) -> None:
    """Ensure that directories for persistent data exist."""

    tasks_dir = config.memory.persistent_tasks_path.parent
    tasks_dir.mkdir(parents=True, exist_ok=True)

    if config.memory.knowledge_base:
        config.memory.knowledge_base.parent.mkdir(parents=True, exist_ok=True)


def asdict(config: AssistantConfig) -> Dict[str, Any]:
    """Return a serialisable dictionary representation of the config."""

    return config.to_dict()
