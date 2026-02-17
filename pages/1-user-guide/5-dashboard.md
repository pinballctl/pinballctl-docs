# Dashboard

The Dashboard is your live status overview for Pinball CTL.

<img src="/api/manual/assets/screenshots/dashboard.png" alt="Dashboard feature overview" style="width: 100%; max-width: 800px; height: auto;">

The Dashboard is designed as a fast health check page before you edit rules, lighting, hardware, or firmware.

## What This Feature Does

It continuously polls runtime APIs and presents a single at-a-glance state for:

- connectivity
- bridge/runtime processes
- ESP state
- sync status
- dependency/tooling readiness

## Live Refresh Behaviour

Dashboard refreshes automatically in the background.

Key behaviour:

- Regular polling (about every 10 seconds).
- Polling pauses when the page is hidden, then resumes when visible.
- If bridge is running but ESP is not yet connected, quick retry mode is used.
- Currency symbol values are loaded from Settings and applied to revenue cards.

## Card-by-Card Reference

### Wi-Fi

Shows:

- interface
- connected status (badge)
- SSID
- IP address
- signal

Use this to confirm remote browser access health.

### Bridge

Shows:

- running/stopped status (badge)
- detection source
- PID

Use this to verify bridge lifecycle state.

### Uptime

Shows:

- since timestamp
- human duration
- raw seconds

Useful for checking unexpected restarts.

### ESP32

Shows:

- firmware
- chip
- ESP time
- connected status
- time sync status

When ESP is connected, additional sync rows are shown:

- Rules Sync (state + last sync time)
- Hardware Sync (state + last sync time)
- Lighting Sync (state + last sync time)

Sync badges:

- `In Sync`
- `Out of Sync`
- `—` when unavailable

### Dependencies

Shows build/flash tooling and whether each dependency is available.

Each row includes:

- tool name
- version (shortened in UI if long)
- `OK`/`Missing` badge

### Gameplay / Revenue Snapshot / Player Flow / Machine

These cards currently display demo/trend style values and machine summary context.

Use them as operational context alongside technical health cards.

## Typical Workflow

1. Open Dashboard first.
2. Confirm Wi-Fi, Bridge, and ESP are healthy.
3. Check sync status rows when ESP is connected.
4. If not healthy, move to the relevant feature:
   - Logs for runtime output
   - Hardware for mapping/sync
   - ESPLink for bridge/device controls

## Example Checks

### Pre-deployment check

Before syncing rules or lighting:

- Bridge = Running
- ESP Connected = Yes
- Time Sync = OK
- Dependencies = all `OK`

### Post-maintenance check

After service work:

- Wi-Fi badge = Yes
- Bridge PID populated
- Uptime progressing normally
- no unexpected sync regressions

## Related Features

- [Hardware](10-hardware.md)
- [ESPLink](11-esplink.md)
- [Logs](14-logs.md)
