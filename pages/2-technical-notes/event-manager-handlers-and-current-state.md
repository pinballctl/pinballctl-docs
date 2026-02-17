# Pi Event Manager: Handlers and Current State

This document describes the current Pi-side Event Manager implementation, including all registered handler routes and current behavior.

## Scope

Pi Event Manager is implemented in:

- `src/pinballctl/events/manager.py`

It is currently wired at two ingress points:

- API-origin events:
  - `POST /api/events/fire`
  - implementation: `src/pinballctl/app/modules/events/api.py`
- Bridge-origin events from ESP (`EVT`/`EVENT`):
  - implementation: `src/pinballctl/bridge/daemon.py`

## Handler Model

Event Manager uses route keys and registered handlers:

- `system:<EVENT>`
- `hardware:<deviceClass>:<eventType>`
- `custom`
- `event:<name>` (dynamic route key)
- `all` (global route key)

Current registered default handlers are explicit no-op stubs (`_NoopHandler`) for all rules-defined system and hardware route keys plus `custom`.

This gives a stable, centralized interface now, with business logic to be added incrementally later.

## Current Registered Handlers

The manager currently auto-registers these route keys from rules registry:

### System handlers

- `system:GAME_STARTED`
- `system:GAME_ENDED`
- `system:BALL_STARTED`
- `system:BALL_ENDED`
- `system:PLAYER_ADDED`
- `system:CREDITS_CHANGED`
- `system:HAS_CREDIT_TRUE`
- `system:HAS_CREDIT_FALSE`
- `system:MODE_STARTED`
- `system:MODE_ENDED`
- `system:BOOT_COMPLETED`
- `system:ENABLE_GRANTED`
- `system:ENABLE_REVOKED`
- `system:IDLE_ENTERED`
- `system:IDLE_EXITED`
- `system:BRIDGE_CONNECTED`
- `system:BRIDGE_DISCONNECTED`
- `system:CONFIG_SYNCED`
- `system:FAULT_RAISED`
- `system:FAULT_CLEARED`
- `system:WATCHDOG_TRIGGERED`

### Hardware handlers

- `hardware:button:CLICKED`
- `hardware:button:DOUBLE_CLICKED`
- `hardware:button:HELD`
- `hardware:button:PRESSED`
- `hardware:button:RELEASED`
- `hardware:button:REPEAT_WHILE_HELD`
- `hardware:switch:CLOSED`
- `hardware:switch:OPENED`
- `hardware:switch:CHANGED`
- `hardware:switch:ACTIVE_FOR_MS`
- `hardware:switch:INACTIVE_FOR_MS`
- `hardware:gyro:TILT_NUDGE`
- `hardware:gyro:TILT_WARNING`
- `hardware:gyro:TILT_TRIGGERED`
- `hardware:gyro:LIFTED`
- `hardware:gyro:DROPPED`
- `hardware:nfc:NFC_SCANNED`
- `hardware:nfc:NFC_MATCHED`

### Custom handlers

- `custom`

## Current Behavior

### API path (`/api/events/fire`)

1. Event is validated against rules registry + source mapping.
2. Event is emitted to Pi event bus (`get_bus().emit(...)`).
3. Event Manager dispatch runs for the same event context (`origin=\"api\"`).

### Bridge RX path (`EVT`/`EVENT`)

1. Bridge receives framed message from ESP.
2. Message is emitted to Pi event bus as before.
3. Event Manager dispatch runs for the same event context (`origin=\"bridge\"`).

## Logging Behavior

- Event manager dispatch trace is bridge-verbose only:
  - appears when `LOG_LEVEL=VERBOSE`
  - format: `event-mgr dispatch name=... source=... origin=... routes=... handlers=...`
- Existing event flood visibility rules still apply:
  - `DEBUG`: bridge traffic details, but event flood remains suppressed
  - `VERBOSE`: full event traffic + event manager trace

## Coverage / Verification

Coverage endpoint:

- `GET /api/events/coverage`

Response reports:

- `expected_count`
- `registered_count`
- `missing_count`
- `missing`
- `complete`

Current expected state after this implementation:

- `expected_count = 40`
- `registered_count = 40`
- `missing_count = 0`
- `complete = true`

## What Is Implemented vs Stubbed

Implemented now:

- Single Event Manager abstraction and dispatch interface
- Registry-driven route registration
- Source->deviceClass resolution via `instance/hardware/mapping.json`
- Ingress wiring for both API and Bridge RX paths
- Coverage endpoint for completeness checks

Still stubbed (next phase):

- Real gameplay/scoring/state mutation handlers on Pi
- Rule-action execution logic at handler level
- Per-handler metrics and timing instrumentation

## Compatibility Notes

- No protocol change (frames-only transport unchanged)
- No Playfield contract change (`/api/events/fire` and `/api/events/stream` unchanged)
- No rules save/sync contract change

