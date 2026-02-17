# ESPLink Module

## Purpose

Bridge and ESP device operations panel for connectivity, filesystem, version management, and upload flows.

## Functionality

- Detects devices and bridge status.
- Starts/stops/restarts bridge service actions.
- Queries device info/status and FS status/listings.
- Uploads/syncs assets to device targets.
- Supports reboot/time-sync and version downloads.

## Key Endpoints (subset)

- `GET /api/esplink/devices`
- `GET /api/esplink/bridge/status`
- `POST /api/esplink/bridge/start|stop|restart`
- `POST /api/esplink/devices/<id>/fs-status`
- `POST /api/esplink/devices/<id>/upload`
