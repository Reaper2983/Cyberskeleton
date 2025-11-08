"""Weather skill using the Open-Meteo API."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

try:
    import requests
except ImportError as exc:  # pragma: no cover - optional dependency
    requests = None  # type: ignore

from ..core.context import ConversationContext
from ..core.nlu import Intent


API_URL = "https://api.open-meteo.com/v1/forecast"


@dataclass
class WeatherResponse:
    summary: str


class WeatherSkill:
    name = "weather"
    description = "Provide quick weather reports using Open-Meteo."

    def __init__(self) -> None:
        self._last_location: Optional[str] = None

    def can_handle(self, intent: Optional[Intent], text: str) -> bool:
        return bool(intent and intent.name == "weather.get")

    def handle(self, intent: Optional[Intent], text: str, context: ConversationContext) -> str:
        if requests is None:
            return "Weather skill requires the 'requests' package. Please install it via pip."
        location = (intent.entities.get("location") if intent else None) or self._last_location or "New York"
        location = location.strip() or "New York"
        self._last_location = location
        try:
            forecast = self._fetch_forecast(location)
        except Exception as exc:  # pragma: no cover - network errors unpredictable
            return f"I couldn't retrieve the weather right now: {exc}"
        return forecast.summary

    def _fetch_forecast(self, location: str) -> WeatherResponse:
        if requests is None:  # pragma: no cover - guarded above
            raise RuntimeError("The requests package is not installed")
        geocode = self._geocode(location)
        if not geocode:
            raise RuntimeError("I couldn't determine that location.")
        params = {
            "latitude": geocode["latitude"],
            "longitude": geocode["longitude"],
            "current_weather": True,
        }
        response = requests.get(API_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        weather = data.get("current_weather", {})
        temperature = weather.get("temperature")
        windspeed = weather.get("windspeed")
        description = weather.get("weathercode", "clear skies")
        summary = (
            f"Weather for {location.title()}: {temperature}°C, wind {windspeed} km/h. "
            f"Weather code {description}."
        )
        return WeatherResponse(summary=summary)

    def _geocode(self, location: str) -> Optional[dict]:
        if requests is None:  # pragma: no cover - guarded above
            return None
        url = "https://geocoding-api.open-meteo.com/v1/search"
        response = requests.get(url, params={"name": location, "count": 1}, timeout=10)
        response.raise_for_status()
        data = response.json()
        results = data.get("results")
        if not results:
            return None
        return results[0]
