"""Constants for Dansk Retursystem Pantstation."""

from datetime import timedelta

DOMAIN = "dansk_retursystem_pantstation"
SERVICE_REFRESH = "refresh"
CONF_STATIONS = "stations"
CONF_NAME = "name"
CONF_URL = "url"
CONF_STATION = "station"

DEFAULT_SCAN_INTERVAL = timedelta(minutes=5)
PLATFORMS = ["sensor"]

# Predefined station list shown as dropdown in config flow.
STATION_OPTIONS: dict[str, dict[str, str]] = {
    "randers": {
        CONF_NAME: "Randers",
        CONF_URL: "https://danskretursystem.dk/pantstation/randers/",
    },
    "odense": {
        CONF_NAME: "Odense",
        CONF_URL: "https://danskretursystem.dk/pantstation/odense/",
    },
    "aarhus": {
        CONF_NAME: "Aarhus",
        CONF_URL: "https://danskretursystem.dk/pantstation/aarhus/",
    },
    "aalborg": {
        CONF_NAME: "Aalborg",
        CONF_URL: "https://danskretursystem.dk/pantstation/aalborg/",
    },
    "kolding": {
        CONF_NAME: "Kolding",
        CONF_URL: "https://danskretursystem.dk/pantstation/kolding/",
    },
    "naestved": {
        CONF_NAME: "Næstved",
        CONF_URL: "https://danskretursystem.dk/pantstation/naestved/",
    },
    "esbjerg": {
        CONF_NAME: "Esbjerg",
        CONF_URL: "https://danskretursystem.dk/pantstation/esbjerg/",
    },
    "viborg": {
        CONF_NAME: "Viborg",
        CONF_URL: "https://danskretursystem.dk/pantstation/viborg/",
    },
}
