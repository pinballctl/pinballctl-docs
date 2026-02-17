# Bridge Event Flow And Throughput

This page documents how Pi, Bridge, and ESP communicate in the current framed-JSON architecture, plus measured throughput from soak testing on February 6, 2026.

![Pi-Bridge-ESP event flow](/api/manual/assets/pi-bridge-esp-event-flow.svg)

## High-Level Model

- Pi Web/API is the orchestration layer.
- Bridge daemon is the single transport boundary between Pi and ESP.
- ESP is the real-time runtime/safety authority.

All Pi <-> ESP traffic goes through the bridge using framed JSON:

- 4-byte big-endian length header
- UTF-8 JSON payload
- No newline/line-based command path

## Message Types

## Response-required RPC (request/response)

Used for control/status requests where caller expects a specific response.

Examples:

- `ECHO`
- `GET_INFO`
- `GET_FS_STATUS`
- `FS_LIST`
- `FS_MANIFEST_GET`
- `SET_RULES` (with `RULES_STATUS` response)

These use `reqId` correlation through bridge pending-response handling.

## Fire-and-forget events (high-volume, no per-event response)

Used for fast event publication where acknowledgement is not required.

Examples:

- `EVENT_FIRE` from Pi -> ESP
- `EVT` stream from ESP -> Pi

This path is intended for high-frequency gameplay telemetry/event flow.

## Event stream control/status

Used for load/soak testing and controlled event burst runs.

Examples:

- `EVT_STREAM_START`
- `EVT_STREAM_STATUS`
- `EVT_STREAM_DONE`

## Runtime Notes

- ESP enforces runtime safety and local real-time behavior.
- Bridge handles framing, req/resp correlation, and event publication into Pi handlers.
- UI responsiveness improves when high-rate event traffic is not over-logged.

## Throughput Results (Soak)

Representative run:

Command:

```bash
./utils/event-soak.sh --rpc-count 100 --fire-count 10000 --fire-batch 1000 --stream-count 10000 --stream-rate 800 --stream-timeout 120
```

Results:

- Phase 1 (Pi->ESP RPC `EVENT` w/ `EVENT_ACK`): `22.81 req/s`
- Phase 1 latency: `43.8 ms avg`, `49.9 ms max`
- Phase 1b (Pi->ESP `EVENT_FIRE`): `10000/10000 seen`, `0 lost`
- Phase 1b throughput: `543.60 evt/s` end-to-end (`598.84 evt/s` enqueue rate)
- Phase 2 (ESP->Pi stream at target `800`): `sent=10000`, `dropped=0`, `rx_delta=10000`
- Phase 2 measured rate: `551.29 evt/s`

Higher target run:

Command:

```bash
./utils/event-soak.sh --rpc-count 100 --fire-count 10000 --fire-batch 1000 --stream-count 10000 --stream-rate 1200 --stream-timeout 120
```

Results:

- Phase 2: `sent=10000`, `dropped=0`, `rx_delta=10000`
- Measured stream rate: `542.95 evt/s`

Interpretation:

- Current practical ESP->Pi sustained ceiling is around `~540-550 evt/s` in this environment.
- System saturates cleanly at higher requested rates (no firmware-reported drops in these runs).

## Practical Operating Guidance

- Keep response-required RPC for control/status only.
- Use fire-and-forget event flow for high-frequency gameplay traffic.
- Keep ultra-latency-critical reactions local on ESP.
- Send summarized/batched telemetry upstream to Pi where appropriate.

Conservative planning targets:

- Sustained design target: `<= 350-400 evt/s`
- Burst target: up to `~500 evt/s`

This preserves headroom for background work and future rule complexity.
