# AGENTS.md

## Cursor Cloud specific instructions

This is a Home Assistant custom integration (HACS-compatible). There is no build system, no Docker, no database — just a Python package under `custom_components/dansk_retursystem_pantstation/`.

### Running the integration locally

1. Create a HA config directory with a symlink to the custom component:
   ```
   mkdir -p /tmp/ha-config/custom_components
   ln -sf /workspace/custom_components/dansk_retursystem_pantstation /tmp/ha-config/custom_components/dansk_retursystem_pantstation
   ```

2. Start Home Assistant:
   ```
   hass -c /tmp/ha-config
   ```
   HA will be available at http://localhost:8123.

3. On first run, complete onboarding via the API or UI (user: dev / pass: dev12345 if previously configured).

### Important caveats

- **aiodns/pycares compatibility**: HA 2025.1.x ships with `aiodns==3.2.0` which requires `pycares==4.4.0` (not 5.x). If DNS resolution fails inside HA, run:
  ```
  pip3 install --break-system-packages "aiodns==3.2.0" "pycares==4.4.0"
  ```

- **python3-dev required**: HA's `pyspeex-noise` dependency (for frontend/cloud) needs Python C headers. Install with `apt-get install -y python3.12-dev`.

- **Internet access**: The integration fetches live HTML from `https://danskretursystem.dk/pantstation/<city>/`. Without internet connectivity, sensors will show `unavailable`.

### Linting

```
ruff check custom_components/
ruff format --check custom_components/
```

All `ruff check` rules pass. Format check shows some files would be reformatted (the repo doesn't enforce formatting).

### Testing the integration via API

After HA is running and onboarded, configure the integration via REST:
```bash
# Init config flow
curl -X POST http://localhost:8123/api/config/config_entries/flow \
  -H "Authorization: Bearer $HA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"handler": "dansk_retursystem_pantstation"}'

# Select add_station, then pick a station key (randers, odense, etc.), then finish
```

Sensor entities are named `sensor.pantstation_<city>_drift`, `sensor.pantstation_<city>_besked`, etc.

### Refresh service

Call `dansk_retursystem_pantstation.refresh` to trigger immediate data fetch:
```bash
curl -X POST http://localhost:8123/api/services/dansk_retursystem_pantstation/refresh \
  -H "Authorization: Bearer $HA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://danskretursystem.dk/pantstation/randers/"}'
```
