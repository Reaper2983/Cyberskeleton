"""Command line interface for the Jarvis assistant."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Optional

from .config import load_config
from .core.assistant import JarvisAssistant
from .io import speech as speech_io
from .io.text import text_conversation


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Interact with the Jarvis AI assistant")
    parser.add_argument("--config", type=str, help="Path to a custom jarvis.yaml file", default=None)
    parser.add_argument("--voice", action="store_true", help="Enable experimental voice mode")
    parser.add_argument("--wake-word", type=str, default=None, help="Custom wake word for voice mode")
    return parser


def run_voice_mode(assistant: JarvisAssistant) -> None:
    config = assistant.config
    try:
        interfaces = speech_io.setup_speech_interfaces(
            input_device=config.audio.input_device,
            output_device=config.audio.output_device,
        )
    except speech_io.SpeechUnavailable as exc:
        print(f"Voice mode is unavailable: {exc}")
        return

    wake_word = (config.audio.wake_word or "jarvis").lower()
    print(f"Listening for wake word '{wake_word}'. Press Ctrl+C to stop.")

    while True:
        heard = speech_io.listen_once(interfaces)
        if not heard:
            continue
        if wake_word and wake_word not in heard.lower():
            continue
        print("Wake word detected. Please speak your request...")
        query = speech_io.listen_once(interfaces)
        if not query:
            print("I didn't catch that.")
            continue
        print(f"You said: {query}")
        response = assistant.handle_text(query)
        print(f"Jarvis: {response}")
        try:
            speech_io.speak(interfaces, response)
        except speech_io.SpeechUnavailable:
            pass


def run_text_mode(assistant: JarvisAssistant) -> None:
    print("Jarvis ready. Type your requests (Ctrl+D to exit).")
    for user_input in text_conversation():
        if not user_input.strip():
            continue
        response = assistant.handle_text(user_input)
        print(f"Jarvis: {response}")


def main(argv: Optional[list[str]] = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    config_path = args.config
    config = load_config(Path(config_path)) if config_path else load_config()
    assistant = JarvisAssistant(config=config)
    if args.voice or assistant.config.audio.enable_voice:
        run_voice_mode(assistant)
    else:
        run_text_mode(assistant)


if __name__ == "__main__":
    main()
