"""Simple terminal based interface for Jarvis."""

from __future__ import annotations

from typing import Iterable


def text_conversation(prompt: str = ">>> ") -> Iterable[str]:
    """Yield user inputs from stdin until EOF."""

    try:
        while True:
            yield input(prompt)
    except (EOFError, KeyboardInterrupt):  # pragma: no cover - interactive
        return
