"""Speech input/output utilities with graceful fallbacks."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class SpeechInterfaces:
    recognizer: Optional["sr.Recognizer"]
    microphone: Optional["sr.Microphone"]
    tts_engine: Optional["pyttsx3.Engine"]


class SpeechUnavailable(RuntimeError):
    pass


try:
    import speech_recognition as sr  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    sr = None  # type: ignore

try:
    import pyttsx3  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    pyttsx3 = None  # type: ignore


def setup_speech_interfaces(input_device: Optional[str] = None, output_device: Optional[str] = None) -> SpeechInterfaces:
    recognizer = sr.Recognizer() if sr else None
    microphone = None
    if sr:
        try:
            microphone = sr.Microphone(device_index=None)
        except Exception as exc:  # pragma: no cover
            raise SpeechUnavailable(f"Microphone initialisation failed: {exc}")

    tts_engine = None
    if pyttsx3:
        tts_engine = pyttsx3.init()
        if output_device is not None:
            try:
                tts_engine.setProperty("outputDevice", output_device)
            except Exception:  # pragma: no cover
                pass
    return SpeechInterfaces(recognizer=recognizer, microphone=microphone, tts_engine=tts_engine)


def listen_once(interfaces: SpeechInterfaces, timeout: float = 5.0) -> Optional[str]:
    if not interfaces.recognizer or not interfaces.microphone:
        raise SpeechUnavailable("Speech recognition dependencies are not installed.")

    with interfaces.microphone as source:
        interfaces.recognizer.adjust_for_ambient_noise(source, duration=0.5)
        audio = interfaces.recognizer.listen(source, timeout=timeout)
    try:
        return interfaces.recognizer.recognize_google(audio)
    except Exception:
        return None


def speak(interfaces: SpeechInterfaces, text: str) -> None:
    if not interfaces.tts_engine:
        raise SpeechUnavailable("Text-to-speech dependency pyttsx3 is not installed.")
    interfaces.tts_engine.say(text)
    interfaces.tts_engine.runAndWait()
