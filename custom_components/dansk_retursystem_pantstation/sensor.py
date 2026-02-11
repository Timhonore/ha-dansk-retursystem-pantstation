"""Sensor platform for Dansk Retursystem Pantstation."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_ATTRIBUTION
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import slugify

from .const import CONF_NAME, CONF_STATIONS, CONF_URL, DOMAIN
from .coordinator import PantstationCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up pantstation sensors from config entry."""
    session = async_get_clientsession(hass)
    stations: list[Mapping[str, str]] = entry.data.get(CONF_STATIONS, [])

    entities: list[PantstationDriftSensor] = []
    coordinators: list[PantstationCoordinator] = []

    for station in stations:
        name = station[CONF_NAME]
        url = station[CONF_URL]
        coordinator = PantstationCoordinator(hass, session, name, url)
        await coordinator.async_refresh()
        coordinators.append(coordinator)
        entities.append(PantstationDriftSensor(coordinator, name, url))

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {"coordinators": coordinators}

    async_add_entities(entities)


class PantstationDriftSensor(CoordinatorEntity[PantstationCoordinator], SensorEntity):
    """Representation of a pantstation drift sensor."""

    _attr_has_entity_name = False

    def __init__(self, coordinator: PantstationCoordinator, station_name: str, station_url: str) -> None:
        """Initialize sensor."""
        super().__init__(coordinator)
        slug = slugify(station_url.rstrip("/").rsplit("/", 1)[-1] or station_name)
        self._attr_unique_id = f"dansk_retursystem_pantstation_{slug}"
        self._attr_name = f"Pantstation {station_name} drift"

    @property
    def native_value(self) -> str | None:
        """Return the current drift state."""
        return self.coordinator.data.drift_state if self.coordinator.data else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional station metadata."""
        data = self.coordinator.data
        last_update = self.coordinator.last_update_success_time

        return {
            "message": data.message if data else None,
            "address": data.address if data else None,
            "opening_hours": data.opening_hours if data else [],
            "url": data.url if data else self.coordinator.station_url,
            "source": "danskretursystem.dk",
            "last_update": last_update.isoformat() if last_update else None,
            ATTR_ATTRIBUTION: "Data fra danskretursystem.dk",
        }
