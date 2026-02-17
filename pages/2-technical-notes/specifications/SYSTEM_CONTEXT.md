# SYSTEM_CONTEXT

## 1. High-level architecture (ESP vs Pi responsibilities)
- ESP32-S3 firmware streams hardware pin data over serial and emits periodic `PING` frames.
- ESP32-S3 firmware responds to commands: `HELLO`, `GET_INFO`, `GET_HW`, and `SYNC_TIME`.
- Raspberry Pi runs a bridge daemon that reads framed serial messages, logs them, and writes hardware snapshots to `src/instance/hardware/discovered.json`.
- Raspberry Pi exposes a Flask-based UI and API; hardware UI reads `/api/hardware/pins` and `/api/hardware/reload`.
- Bridge state (port, firmware, chip, time sync) is persisted in `src/instance/bridge_state.json`.

## 2. Communication model (protocol shape, framing, direction)
- ESP -> Pi uses length-prefixed frames: 4-byte big-endian length header + JSON payload (`writeFramed`).
- Pi -> ESP uses newline-delimited JSON (`to_line` in `bridge/protocol.py`).
- Messages are JSON objects with a `t` field for event type (e.g., `INFO`, `PING`, `HW_BEGIN`, `HW_PIN`, `HW_END`, `TIME`).
- HW discovery is streamed with `HW_STATUS` + `HW_BEGIN` + multiple `HW_PIN` + `HW_END`.
- Firmware emits `HW_PROBE` before probing a GPIO when probing is enabled.
- Bridge processes frames with `_read_frame` and decodes JSON.
- Bridge queues outbound commands via `src/instance/bridge_commands.json` and sends them over serial.

## 3. Hardware interaction model
- ESP firmware maintains a static `PIN_TABLE` describing pins and metadata (`reported`, `notes`, `safe`).
- Pins with `safe=false` are never probed.
- Probing (when enabled) is input-only: `pinMode(INPUT)` + `digitalRead()`.
- GPIO probing is gated by `ALLOW_GPIO_PROBE` in firmware.
- Hardware discovery is non-blocking and paced (`serviceHardwareStream`).
- Pin state is included in `HW_PIN` payload only when probing occurs.

## 4. Known constraints explicitly visible in code
- Hardware stream timeout cap: `HW_STREAM_TIMEOUT_MS = 8000`.
- Serial framing: max frame size limited by `TX_FRAME_MAX` (512 bytes in firmware).
- TX queue depth: `TX_QUEUE_MAX = 4` frames in firmware.
- Bridge read resync: resets input buffer when header/body timeouts occur.
- Bridge logs only raw RX lines at DEBUG level (no parsed JSON).
- Hardware snapshot is stored at `src/instance/hardware/discovered.json`.
- Hardware UI uses `reported` and `notes` fields to display pin notes.

## 5. Areas of uncertainty / risk (UNKNOWN)
- UNKNOWN: Which GPIOs are truly safe to probe for a specific ESP32-S3-DevKitC-1 module beyond the `PIN_TABLE` defaults.
- UNKNOWN: Whether USB-CDC or other serial transport variations affect framing reliability.
- UNKNOWN: Any external expansion board detection mechanisms beyond GPIO probing (not visible in code).

## 6. Modules and UI functionality
- Dashboard UI: Wi‑Fi status (interface/connected/SSID/IP/signal), bridge status (status/via/PID), uptime (since/duration/seconds), ESP32 info (firmware/chip/time/connected/time sync), dependencies list.
- Logs UI: source selection (web combined/error/access/bridge), line count, keyword filter, refresh/clear/purge, tail toggle, log viewport.
- Hardware UI: reload pins, save mapping, table of UID/board/type/notes/channel/state/friendly/function/purpose.
- ESPLink UI: device selection, status/firmware display, refresh/reboot/sync time, bridge start/stop/restart, local firmware list, upload console.
- Firmware UI: list available versions with source selection (default/custom URL), load remote, remove all local versions.
- Settings UI: project name, admin username/password, remote firmware URL, log level, export project bundle, import project bundle.
- Wi‑Fi UI: current status (SSID/IP/status/connected), update settings (SSID/password), save.
- Playfield UI: layout table, size/ratio options, auto layout/clear/save layout, component list (buttons/LEDs/other), component settings (appearance/color/size/key bindings/remove).
- Rules UI: add/save rules, tag filter, rules table (name/tags/triggers/actions), editor panes for triggers/actions.

## 7. Pin mapping goals and UX principles (user-provided)
- Target users may be non-technical; UI should avoid GPIO jargon where possible.
- Mapping should guide users from unknown hardware to identified device via simple choices.
- Mapping must be safe: ESP firmware must never drive/probe unsafe pins; mapping cannot override safe=false.
- UI should distinguish discovered pins, mapped devices, and active configuration.

## 8. Pin mapping data model (proposed minimal shape; user-provided)
- A pin is identified by stable `uid` from firmware (preferred key).
- Mapping is stored on the Pi (not in firmware) and can be applied/config-pushed to ESP later.
- Each mapping record contains:
- `uid`: string (from HW_PIN).
- `gpio`: number|null (optional convenience; do not rely on it for uniqueness).
- `device_type`: enum (e.g., push_button, led_strip, coil, i2c_device, switch_matrix).
- `label`: human-friendly name.
- `config`: object keyed by type.
- `enabled`: bool.
- `created_at`, `updated_at`: timestamps (optional).
- Example mapping JSON: UNKNOWN (not provided).

## 9. Pin mapping invariants (non-negotiable rules; user-provided)
- Mapping must never assign a device to a pin where `safe=false`.
- A `uid` can map to at most one device at a time (no duplicates).
- UI must prevent conflicting assignments (e.g., two devices on the same `uid`).
- Reload pins updates discovery state but must not destroy mappings:
- If a mapped `uid` disappears, mapping is kept but flagged "missing".
- If a discovered `uid` is new, it appears as "unmapped".
- Mapping changes should be atomic (save either succeeds fully or not at all).
- UI should support an Apply/Deploy step separately from Edit mapping.
