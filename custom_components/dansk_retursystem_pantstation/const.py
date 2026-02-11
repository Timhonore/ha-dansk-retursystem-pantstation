"""Constants for Dansk Retursystem Pantstation."""

from datetime import timedelta

DOMAIN = "dansk_retursystem_pantstation"
CONF_STATIONS = "stations"
CONF_NAME = "name"
CONF_URL = "url"

DEFAULT_SCAN_INTERVAL = timedelta(minutes=5)
PLATFORMS = ["sensor"]
