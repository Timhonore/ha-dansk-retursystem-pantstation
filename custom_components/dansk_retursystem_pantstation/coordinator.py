"""Data update coordinator for pantstation drift information."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
import logging
import re

from aiohttp import ClientError, ClientSession
from bs4 import BeautifulSoup

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DEFAULT_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)
_DRIFT_PATTERN = re.compile(r"^(Åben|Lukket|Midlertidigt lukket)\.\s*(.*)$", re.IGNORECASE)


@dataclass(slots=True)
class PantstationData:
    """Parsed pantstation drift data."""

    drift_state: str | None
    message: str | None
    address: str | None
    opening_hours: list[str]
    url: str


class PantstationCoordinator(DataUpdateCoordinator[PantstationData]):
    """Coordinator for a single pantstation page."""

    def __init__(
        self,
        hass: HomeAssistant,
        session: ClientSession,
        station_name: str,
        station_url: str,
    ) -> None:
        """Initialize coordinator."""
        self._session = session
        self.station_name = station_name
        self.station_url = station_url

        super().__init__(
            hass,
            _LOGGER,
            name=f"{station_name} pantstation drift",
            update_interval=DEFAULT_SCAN_INTERVAL,
        )

    async def _async_update_data(self) -> PantstationData:
        """Fetch and parse drift info from the station page."""
        try:
            async with self._session.get(self.station_url, timeout=30) as response:
                response.raise_for_status()
                html = await response.text()
        except (ClientError, TimeoutError) as err:
            _LOGGER.error("Failed fetching station page '%s': %s", self.station_url, err)
            raise UpdateFailed(f"Failed fetching {self.station_url}") from err

        return _parse_station_page(self.station_url, html)


def _parse_station_page(station_url: str, html: str) -> PantstationData:
    """Parse relevant drift information from the station HTML."""
    soup = BeautifulSoup(html, "html.parser")
    lines = _normalized_lines(soup.get_text("\n"))

    drift_state: str | None = None
    message: str | None = None

    for line in lines:
        match = _DRIFT_PATTERN.match(line)
        if not match:
            continue
        drift_state = _normalize_state(match.group(1))
        message = match.group(2).strip() or None
        break

    address = _find_address(lines)
    opening_hours = _find_opening_hours(lines)

    return PantstationData(
        drift_state=drift_state,
        message=message,
        address=address,
        opening_hours=opening_hours,
        url=station_url,
    )


def _normalized_lines(text: str) -> list[str]:
    """Return stripped non-empty lines."""
    return [line.strip() for line in text.splitlines() if line.strip()]


def _normalize_state(state: str) -> str:
    """Normalize known drift states to expected capitalization."""
    lowered = state.casefold()
    if lowered == "åben":
        return "Åben"
    if lowered == "lukket":
        return "Lukket"
    if lowered == "midlertidigt lukket":
        return "Midlertidigt lukket"
    return state


def _find_address(lines: list[str]) -> str | None:
    """Best effort extraction of address from lines after 'Adresse'."""
    index = _find_label_index(lines, "adresse")
    if index is None:
        return None

    candidates = [line for line in lines[index + 1 : index + 3] if line and not _is_heading(line)]
    if not candidates:
        return None

    return ", ".join(candidates)


def _find_opening_hours(lines: list[str]) -> list[str]:
    """Best effort extraction of opening hours after 'Åbningstider'."""
    index = _find_label_index(lines, "åbningstider")
    if index is None:
        return []

    opening_lines: list[str] = []
    for line in _iter_until_heading(lines[index + 1 :]):
        if ":" in line:
            opening_lines.append(line)

    return opening_lines


def _find_label_index(lines: list[str], label: str) -> int | None:
    """Find line index for a case-insensitive label."""
    normalized_label = label.casefold()
    for idx, line in enumerate(lines):
        if line.casefold() == normalized_label:
            return idx
    return None


def _iter_until_heading(lines: Iterable[str]) -> Iterable[str]:
    """Iterate lines until another heading-like line appears."""
    for line in lines:
        if _is_heading(line):
            break
        yield line


def _is_heading(line: str) -> bool:
    """Heuristic heading detection to stop parsing nearby sections."""
    if len(line) > 45:
        return False
    if ":" in line:
        return False
    words = line.split()
    if not words:
        return False
    return all(word[:1].isupper() for word in words)
