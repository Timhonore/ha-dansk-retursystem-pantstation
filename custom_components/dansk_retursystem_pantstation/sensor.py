"""Sensor platform for Dansk Retursystem Pantstation."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_ATTRIBUTION
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import slugify

from .const import CONF_NAME, CONF_STATIONS, CONF_URL, DOMAIN
from .coordinator import PantstationCoordinator


def _get_configured_stations(entry: ConfigEntry) -> list[Mapping[str, str]]:
    """Return configured stations and support legacy single-station data."""
    stations: list[Mapping[str, str]] = entry.data.get(CONF_STATIONS, [])
    if stations:
        return stations

    legacy_name = entry.data.get(CONF_NAME)
    legacy_url = entry.data.get(CONF_URL)
    if isinstance(legacy_name, str) and isinstance(legacy_url, str):
        return [{CONF_NAME: legacy_name, CONF_URL: legacy_url}]

    return []


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up pantstation sensors from config entry."""
    session = async_get_clientsession(hass)
    stations = _get_configured_stations(entry)

    entities: list[SensorEntity] = []
    coordinators: list[PantstationCoordinator] = []

    for station in stations:
        name = station[CONF_NAME]
        url = station[CONF_URL]
        coordinator = PantstationCoordinator(hass, session, name, url)
        await coordinator.async_refresh()
        coordinators.append(coordinator)

        entities.extend(
            [
                PantstationDriftSensor(coordinator, name, url),
                PantstationMessageSensor(coordinator, name, url),
                PantstationAddressSensor(coordinator, name, url),
                PantstationOpeningHoursSensor(coordinator, name, url),
            ]
        )

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {"coordinators": coordinators}

    async_add_entities(entities)


class PantstationBaseSensor(CoordinatorEntity[PantstationCoordinator], SensorEntity):
    """Common base class for pantstation sensors."""

    _attr_has_entity_name = False

    def __init__(self, coordinator: PantstationCoordinator, station_name: str, station_url: str) -> None:
        """Initialize shared station sensor details."""
        super().__init__(coordinator)
        station_slug = slugify(station_url.rstrip("/").rsplit("/", 1)[-1] or station_name)
        self._station_name = station_name
        self._station_url = station_url
        self._station_slug = station_slug

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional station metadata."""
        data = self.coordinator.data
        last_update = data.fetched_at if data else None

        return {
            "url": data.url if data else self._station_url,
            "source": "danskretursystem.dk",
            "last_update": last_update.isoformat() if last_update else None,
            ATTR_ATTRIBUTION: "Data fra danskretursystem.dk",
        }

    @property
    def device_info(self) -> DeviceInfo:
        """Group all station sensors under one Home Assistant device."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._station_slug)},
            name=f"Dansk Retursystem Pantstation {self._station_name}",
            manufacturer="Dansk Retursystem",
            model="Pantstation",
            configuration_url=self._station_url,
        )


class PantstationDriftSensor(PantstationBaseSensor):
    """Main drift status sensor for a pantstation."""

    def __init__(self, coordinator: PantstationCoordinator, station_name: str, station_url: str) -> None:
        super().__init__(coordinator, station_name, station_url)
        self._attr_unique_id = f"dansk_retursystem_pantstation_{self._station_slug}_drift"
        self._attr_name = f"Pantstation {station_name} drift"
        self._attr_icon = "mdi:recycle"

    @property
    def native_value(self) -> str | None:
        """Return the current drift state."""
        return self.coordinator.data.drift_state if self.coordinator.data else None


class PantstationMessageSensor(PantstationBaseSensor):
    """Sensor that exposes station status message."""

    def __init__(self, coordinator: PantstationCoordinator, station_name: str, station_url: str) -> None:
        super().__init__(coordinator, station_name, station_url)
        self._attr_unique_id = f"dansk_retursystem_pantstation_{self._station_slug}_message"
        self._attr_name = f"Pantstation {station_name} besked"
        self._attr_icon = "mdi:message-text"

    @property
    def native_value(self) -> str | None:
        """Return current station message."""
        return self.coordinator.data.message if self.coordinator.data else None


class PantstationAddressSensor(PantstationBaseSensor):
    """Sensor that exposes station address."""

    def __init__(self, coordinator: PantstationCoordinator, station_name: str, station_url: str) -> None:
        super().__init__(coordinator, station_name, station_url)
        self._attr_unique_id = f"dansk_retursystem_pantstation_{self._station_slug}_address"
        self._attr_name = f"Pantstation {station_name} adresse"
        self._attr_icon = "mdi:map-marker"

    @property
    def native_value(self) -> str | None:
        """Return station address."""
        return self.coordinator.data.address if self.coordinator.data else None


class PantstationOpeningHoursSensor(PantstationBaseSensor):
    """Sensor that exposes station opening hours."""

    def __init__(self, coordinator: PantstationCoordinator, station_name: str, station_url: str) -> None:
        super().__init__(coordinator, station_name, station_url)
        self._attr_unique_id = f"dansk_retursystem_pantstation_{self._station_slug}_opening_hours"
        self._attr_name = f"Pantstation {station_name} åbningstider"
        self._attr_icon = "mdi:clock-outline"

    @property
    def native_value(self) -> str | None:
        """Return opening hours as newline-separated text."""
        if not self.coordinator.data or not self.coordinator.data.opening_hours:
            return None
        return "\n".join(self.coordinator.data.opening_hours)
