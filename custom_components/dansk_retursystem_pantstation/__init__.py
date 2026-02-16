"""The Dansk Retursystem Pantstation integration."""

from __future__ import annotations

from collections.abc import Iterable
import logging
from pathlib import Path

from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
import voluptuous as vol

from .const import CONF_URL, DOMAIN, PLATFORMS, SERVICE_REFRESH

SERVICE_REFRESH_SCHEMA = vol.Schema({vol.Optional(CONF_URL): str})
_LOGGER = logging.getLogger(__name__)
_RUNTIME_DATA_KEYS = {"service_registered", "static_registered"}


async def _async_register_static_images(hass: HomeAssistant) -> None:
    """Register local images for sensor entity pictures."""
    domain_data = hass.data.setdefault(DOMAIN, {})
    if domain_data.get("static_registered"):
        return

    static_dir = (Path(__file__).parent / "images").resolve()
    if not static_dir.exists():
        _LOGGER.warning("Pantstation static image dir not found: %s", static_dir)
        return

    await hass.http.async_register_static_paths(
        [StaticPathConfig(f"/{DOMAIN}/img", str(static_dir), cache_headers=True)]
    )
    domain_data["static_registered"] = True


def _iter_all_coordinators(hass: HomeAssistant) -> Iterable:
    """Yield all station coordinators across active config entries."""
    domain_data = hass.data.get(DOMAIN, {})
    for entry_id, entry_data in domain_data.items():
        if entry_id in _RUNTIME_DATA_KEYS:
            continue
        for coordinator in entry_data.get("coordinators", []):
            yield coordinator


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up services for Dansk Retursystem Pantstation."""
    hass.data.setdefault(DOMAIN, {})
    await _async_register_static_images(hass)

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
    await _async_register_static_images(hass)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        domain_data = hass.data.get(DOMAIN, {})
        domain_data.pop(entry.entry_id, None)

        active_entries = [key for key in domain_data if key not in _RUNTIME_DATA_KEYS]
        if not active_entries and hass.services.has_service(DOMAIN, SERVICE_REFRESH):
            hass.services.async_remove(DOMAIN, SERVICE_REFRESH)
            domain_data.pop("service_registered", None)
    return unload_ok
