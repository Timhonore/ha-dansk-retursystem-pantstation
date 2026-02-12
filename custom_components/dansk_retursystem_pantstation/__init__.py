"""The Dansk Retursystem Pantstation integration."""

from __future__ import annotations

from collections.abc import Iterable

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
import voluptuous as vol

from .const import CONF_URL, DOMAIN, PLATFORMS, SERVICE_REFRESH

SERVICE_REFRESH_SCHEMA = vol.Schema({vol.Optional(CONF_URL): str})


def _iter_all_coordinators(hass: HomeAssistant) -> Iterable:
    """Yield all station coordinators across active config entries."""
    domain_data = hass.data.get(DOMAIN, {})
    for entry_id, entry_data in domain_data.items():
        if entry_id == "service_registered":
            continue
        for coordinator in entry_data.get("coordinators", []):
            yield coordinator


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up services for Dansk Retursystem Pantstation."""
    hass.data.setdefault(DOMAIN, {})

    async def async_handle_refresh(call) -> None:
        station_url = call.data.get(CONF_URL)
        for coordinator in _iter_all_coordinators(hass):
            if station_url and coordinator.station_url != station_url:
                continue
            await coordinator.async_request_refresh()

    if not hass.services.has_service(DOMAIN, SERVICE_REFRESH):
        hass.services.async_register(
            DOMAIN,
            SERVICE_REFRESH,
            async_handle_refresh,
            schema=SERVICE_REFRESH_SCHEMA,
        )
        hass.data[DOMAIN]["service_registered"] = True

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Dansk Retursystem Pantstation from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        domain_data = hass.data.get(DOMAIN, {})
        domain_data.pop(entry.entry_id, None)

        active_entries = [key for key in domain_data if key != "service_registered"]
        if not active_entries and hass.services.has_service(DOMAIN, SERVICE_REFRESH):
            hass.services.async_remove(DOMAIN, SERVICE_REFRESH)
            domain_data.pop("service_registered", None)
    return unload_ok
