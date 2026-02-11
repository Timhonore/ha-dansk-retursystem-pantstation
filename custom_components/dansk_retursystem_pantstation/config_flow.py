"""Config flow for Dansk Retursystem Pantstation."""

from __future__ import annotations

from urllib.parse import urlparse

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import CONF_NAME, CONF_STATIONS, CONF_URL, DOMAIN


class DanskRetursystemPantstationConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Dansk Retursystem Pantstation."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize flow."""
        self._stations: list[dict[str, str]] = []

    async def async_step_user(self, user_input: dict | None = None) -> FlowResult:
        """Show a menu for adding stations or finishing setup."""
        if user_input is not None and user_input.get("next_step_id") == "finish":
            return self.async_create_entry(
                title="Dansk Retursystem Pantstation",
                data={CONF_STATIONS: self._stations},
            )

        summary = self._station_summary()
        return self.async_show_menu(
            step_id="user",
            menu_options=["add_station", "finish"],
            description_placeholders={"stations": summary},
        )

    async def async_step_add_station(self, user_input: dict | None = None) -> FlowResult:
        """Add one station to the pending configuration."""
        errors: dict[str, str] = {}

        if user_input is not None:
            name = user_input[CONF_NAME].strip()
            normalized_url = _normalize_station_url(user_input[CONF_URL])

            if normalized_url is None:
                errors[CONF_URL] = "invalid_url"
            elif any(station[CONF_URL] == normalized_url for station in self._stations):
                errors[CONF_URL] = "duplicate_station"
            else:
                self._stations.append({CONF_NAME: name, CONF_URL: normalized_url})
                return await self.async_step_user()

        schema = vol.Schema(
            {
                vol.Required(CONF_NAME): str,
                vol.Required(CONF_URL, default=""): str,
            }
        )
        return self.async_show_form(step_id="add_station", data_schema=schema, errors=errors)

    async def async_step_finish(self, user_input: dict | None = None) -> FlowResult:
        """Finish setup and create config entry."""
        return self.async_create_entry(
            title="Dansk Retursystem Pantstation",
            data={CONF_STATIONS: self._stations},
        )

    def _station_summary(self) -> str:
        """Create a human-readable list of stations already added."""
        if not self._stations:
            return "-"
        return "\n".join(f"• {station[CONF_NAME]}" for station in self._stations)


def _normalize_station_url(url: str) -> str | None:
    """Validate station URL and enforce trailing slash."""
    normalized = url.strip()
    if not normalized:
        return None

    parsed = urlparse(normalized)
    if parsed.scheme != "https" or parsed.netloc != "danskretursystem.dk":
        return None

    if not parsed.path.startswith("/pantstation/"):
        return None

    if not normalized.endswith("/"):
        normalized = f"{normalized}/"

    return normalized
