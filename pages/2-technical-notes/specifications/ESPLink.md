# ESPLink — Module Specification

## Overview
**ESPLink** is responsible for managing communication between the Raspberry Pi controller and one or more connected ESP32-S3 devices.
It provides a web interface to view device information, monitor serial output, manage firmware updates, and perform diagnostic actions.

---

## Goals
- Display status and metadata for connected ESP devices.
- Manage multiple ESP connections.
- List and apply available firmware versions.
- Provide an inline upload console with real-time feedback.
- Stream and control serial output from each ESP.
- Offer common maintenance tools (reboot, sync time, backup config, etc).

---

## User Interface

### Top Bar (Sticky Header)
- **Device Selector:** Dropdown list of connected devices (`ESP_A1B2C3`, etc).
- **Connection Status:** “Connected / Disconnected” pill with last seen time.
- **Firmware Version:** `vX.Y.Z+build` reported by device.
- **Chip Info:** e.g. `ESP32-S3 | MAC: xx:xx:xx:xx:xx:xx`.
- **Quick Actions:** `Refresh`, `Reboot`, `Sync Time`, `Open Serial`.

### Tabs / Sections
1. **Overview**
   - Live metrics: uptime, heap usage, temperature, Wi-Fi RSSI, IP, last fault.
   - Capabilities list (DMP, LEDs, I2C expanders, etc.).
   - Summary of loaded configuration (controller ID, features).

2. **Firmware**
   - Source selector: `Local dist/` | `Remote`.
   - List of available versions (from `versions.json`).
   - “Apply” button per version to start OTA update.
   - Inline **Upload Console**: step-by-step log output (autoscroll, downloadable).

3. **Serial**
   - Live serial stream viewer.
   - Controls: **Start / Stop**, **Pause / Resume**, **Clear**, **Download**, **Follow tail**.
   - Filters: include/exclude text, timestamps, baud (read-only if fixed).

4. **Tools**
   - Quick actions:
     `Reboot`, `Factory Reset`, `Backup Config`, `Restore Config`,
     `Ping`, `LED Test`, `I/O Monitor`, `Wi-Fi Scan`.

---

## Firmware Management

### `versions.json` Schema
```json
{
  "latest": "1.2.3+45",
  "base_url": "/static/dist/",
  "versions": [
    {
      "version": "1.2.3+45",
      "date": "2025-11-07T12:34:56Z",
      "notes": "Bugfixes and faster serial framing",
      "filename": "firmware-1.2.3+45.bin",
      "sha256": "…",
      "size": 1048576,
      "download_url": "https://example.com/dist/firmware-1.2.3+45.bin"
    }
  ]
}
```

**Rules**
- Prefer `download_url` if present, otherwise use `base_url + filename`.
- The `latest` field marks the recommended build.

### Local Paths
- Development builds stored in:
  `pinballctl/web/static/dist/`
- Cached downloads:
  `~/.local/state/pinballctl/firmware-cache/`

---

## API Endpoints (prefix `/esplink`)

### Devices
| Method | Path | Description |
|:--|:--|:--|
| GET | `/devices` | List connected devices with basic info |
| GET | `/devices/<id>/status` | Detailed device metrics |
| POST | `/devices/<id>/reboot` | Soft-reboot device |
| POST | `/devices/<id>/sync-time` | Sync RTC time with host |

### Firmware
| Method | Path | Description |
|:--|:--|:--|
| GET | `/versions?source=local\|remote` | Return merged version list |
| POST | `/devices/<id>/upload` | Begin OTA upload (SSE/WebSocket progress) |

**Upload events:**
```
STEP: download | verify | enter-ota | transfer 0–100 | commit | reboot | done
LOG: arbitrary text line
ERROR: message
```

### Serial
| Method | Path | Description |
|:--|:--|:--|
| POST | `/devices/<id>/serial/start` | Begin streaming serial output |
| POST | `/devices/<id>/serial/stop` | Stop serial session |
| POST | `/devices/<id>/serial/pause` | Pause reading |
| POST | `/devices/<id>/serial/resume` | Resume reading |
| GET | `/devices/<id>/serial/stream` | Stream serial output via SSE/WS |
| POST | `/devices/<id>/serial/write` | Optional: send command text |

### Config / Tools
| Method | Path | Description |
|:--|:--|:--|
| GET | `/devices/<id>/config` | Download config |
| POST | `/devices/<id>/config` | Apply config |
| POST | `/devices/<id>/factory-reset` | Factory reset (with confirm) |
| GET | `/devices/<id>/wifi/scan` | Return nearby Wi-Fi networks |
| GET | `/ping` | Simple healthcheck |

---

## OTA Upload Flow

1. **Pause Serial** — suspend logging.
2. **Fetch Firmware** — local or remote download.
3. **Verify Hash** — SHA-256 match if available.
4. **Enter OTA Mode** — instruct device via bridge (`OTA_BEGIN size=<n> sha=<…>`).
5. **Transfer** — chunked writes with progress, retry, throughput stats.
6. **Commit & Reboot** — `OTA_COMMIT`, then reboot.
7. **Reconnect & Resume Serial** — confirm new version.

All steps output lines to the **Upload Console** (monospace, autoscroll, downloadable).

---

## Serial Console UX
- Rolling buffer (e.g., 10 000 lines).
- Optional timestamps.
- Search / filter text.
- Auto-follow toggle.
- Pause automatically during OTA.

---

## Multi-Device Handling
- Devices listed from `/devices` (poll or WebSocket updates).
- Each device keeps its own serial session and upload state.
- Actions always include the device ID in path.

---

## Frontend Structure
- Route: `/esplink/`
- Framework: Alpine.js + WebAwesome.
- Components:
  - `esplink-header`
  - `esplink-overview`
  - `esplink-firmware`
  - `esplink-serial`
  - `esplink-tools`
- Console areas are flex cards with `overflow:auto;` and fixed height.

---

## Bridge / Daemon Integration
- Multiplex serial read/write with per-device pause/resume.
- Emit `HELLO` payload: `{ fw, chip, mac, features, controller }`.
- Rate-limit writes during OTA.
- Normalize line endings (`\n`) and timestamp at source.

---

## Extra Tools & Diagnostics
- **Backup / Restore** device configuration (JSON).
- **Safe Mode / Rollback** firmware if dual partitions exist.
- **I/O Monitor** — live switch & coil states.
- **LED Test** — quick visual check patterns.
- **Fault Snapshot** — retrieve last crash dump.
- **Time Sync** & **NTP status** view.
- **Wi-Fi RSSI / Channel graph.**
- **Manifest check** before arming coils.
- **Download serial transcript** and **upload log** as text.

---

## Security & UX Notes
- Confirmation prompts for destructive actions (reset, OTA).
- CSRF protection on POST routes.
- Verify size and SHA before flashing.
- Require explicit user click to apply “latest”.
- Optional **dry-run verify** mode (hash only, no write).

---

_Last updated: November 2025_




## Original Requirements

I think ESPLink may be more suitable. I would like this module to do the following:

- Display at the top information about the ESP. If it is connected, the version of firmware it is running etc. It may be that we have multiple devices connected so we should be able to select which one we are using. Any other information we can get from it should be displayed.

- Firmware versions will be available during development in the dist folder in our project. We will create a versions.json which will have all the available versions and a "latest" which always points to the latest version. These versions will also have a link for download.  Going forward I will publish this dist to github so we should be able to retrive this list form a remote server. These versions should be listed and an option to Apply whic will upload to the ESP.

- The upload status information should be displayed in an inline "console" window so we can see what is happening.

- I would like to be able to view serial output from here. The UI may have a tab or button to open this up. When we upload we will need a way to pause the connection reading the serial.

Can you think of any other tools here which might be useful to add to the UI ?