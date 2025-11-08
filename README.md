# Cyberskeleton Jarvis Assistant

A modular, voice-ready AI assistant inspired by Marvel's Jarvis and modern tools like Pika AI. The project ships with a flexible Python architecture, opt-in voice controls, and a small library of skills that can be extended with custom behaviours.

## Features

- **Conversational core** powered by configurable language models (OpenAI or local fallback).
- **Voice I/O** via `speech_recognition` and `pyttsx3` with wake-word support and graceful degradation when devices or dependencies are missing.
- **Skill routing** for specialised behaviours including task management, local knowledge lookup, weather reports, and safe system diagnostics.
- **Persistent memory** for tasks and user-provided knowledge snippets.
- **Configurable** through a YAML file (`jarvis.yaml`) and environment overrides.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m jarvis.app
```

By default the assistant runs in text mode with a local-echo model that demonstrates the routing stack without needing any API keys. To unlock rich LLM responses:

1. Set `OPENAI_API_KEY` in your environment.
2. Update `jarvis.yaml` to use the `openai` provider.

```yaml
model:
  provider: openai
  model: gpt-4o-mini
  temperature: 0.7
```

## Voice mode

Enable voice input/output either by passing `--voice` to the launcher or setting `audio.enable_voice: true` in `jarvis.yaml`.

```bash
python -m jarvis.app --voice
```

Dependencies for voice mode (`speech_recognition`, `pyttsx3`, microphone drivers) must be installed and configured on your system. The assistant listens for the wake word (default `jarvis`) before recording a command.

## Skills and extensibility

Skills are Python classes registered through dotted paths in `jarvis.yaml`. Each skill receives parsed intents and can respond before the LLM is invoked.

| Skill | Module | Capabilities |
| --- | --- | --- |
| System diagnostics | `jarvis.skills.system:SystemSkill` | Provide basic system info and run a safe list of commands (`list`, `status`, `open logs`). |
| Task management | `jarvis.skills.tasks:TaskSkill` | Persist todos/reminders under `~/.jarvis/tasks.json`. |
| Knowledge base | `jarvis.skills.knowledge:KnowledgeSkill` | Answer from a user-maintained JSON file (`~/.jarvis/knowledge.json`). |
| Weather | `jarvis.skills.weather:WeatherSkill` | Query Open-Meteo for current weather using built-in geocoding. |

To add a new skill, create a module that implements the `Skill` protocol (see existing skills for reference) and append the dotted path to `skill_modules`.

## Configuration reference

All settings can be overridden via environment variables prefixed with `JARVIS_`. Nested values use double underscores. Examples:

```bash
export JARVIS_MODEL__PROVIDER=openai
export JARVIS_AUDIO__ENABLE_VOICE=true
```

## Requirements

Python 3.10+ is recommended. Install dependencies with:

```bash
pip install -r requirements.txt
```

The default `requirements.txt` includes optional packages for voice and HTTP integrations. Feel free to trim it if you only need text interactions.

## Roadmap ideas

- Integrate local embedding search for richer knowledge grounding.
- Support streaming responses and hands-free follow-up interactions.
- Expand the skill ecosystem (calendar, smart home, media control).

Contributions are welcome—open an issue or submit a PR with enhancements!
