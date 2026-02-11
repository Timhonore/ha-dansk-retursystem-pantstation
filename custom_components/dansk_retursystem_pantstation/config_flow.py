"""Config flow for Dansk Retursystem Pantstation."""

from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import (
    CONF_NAME,
    CONF_STATION,
    CONF_STATIONS,
    CONF_URL,
    DOMAIN,
    STATION_OPTIONS,
)


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
        """Add one station to the pending configuration from dropdown list."""
        errors: dict[str, str] = {}

        if user_input is not None:
            station_key = user_input[CONF_STATION]
            station = STATION_OPTIONS[station_key]

            if any(existing[CONF_URL] == station[CONF_URL] for existing in self._stations):
                errors["base"] = "duplicate_station"
            else:
                self._stations.append(dict(station))
                return await self.async_step_user()

        station_select = {
            key: f"{data[CONF_NAME]} ({data[CONF_URL]})" for key, data in STATION_OPTIONS.items()
        }
        schema = vol.Schema(
            {
                vol.Required(CONF_STATION): vol.In(station_select),
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
