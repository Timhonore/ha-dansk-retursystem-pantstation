# Dansk Retursystem Pantstation (Home Assistant custom integration)

Denne integration henter **driftinformation** fra Dansk Retursystems pantstation-sider (fx Randers, Odense) og opretter en sensor pr. station i Home Assistant.

Sensorens state bliver typisk:

- `Åben`
- `Lukket`
- `Midlertidigt lukket`

Derudover sættes attributes:

- `message`
- `address`
- `opening_hours`
- `url`
- `source`
- `last_update`

## Installation (manuel)

1. Kopiér mappen `custom_components/dansk_retursystem_pantstation/` til din Home Assistant installation under `config/custom_components/`.
2. Genstart Home Assistant.
3. Gå til **Indstillinger → Enheder & tjenester → Tilføj integration**.
4. Vælg **Dansk Retursystem – Pantstation driftinfo**.

## Installation via HACS (valgfri)

Hvis du bruger HACS og repoet er tilføjet som custom repository:

1. Installer integrationen via HACS.
2. Genstart Home Assistant.
3. Tilføj integrationen via UI.

## Konfiguration i UI

Flowet er menu-baseret:

1. Vælg **Tilføj pantstation**.
2. Indtast:
   - `name` (frit navn)
   - `url` (skal starte med `https://danskretursystem.dk/pantstation/`)
3. Gentag for flere stationer.
4. Vælg **Færdig** for at oprette integrationen.

## Eksempel-stationer

- Randers: `https://danskretursystem.dk/pantstation/randers/`
- Odense: `https://danskretursystem.dk/pantstation/odense/`

## Tekniske noter

- Polling hvert 5. minut via `DataUpdateCoordinator`.
- Parser HTML med BeautifulSoup4 og tolerant tekstudtræk.
- Hvis driftlinjen ikke kan findes, bliver state `unknown`/`None` og message `None`.
