# Event Manager Entry Points (Requirement + Implementation)

This page captures the requirement for the event manager/handler layer and the current concrete hook points in the codebase.

For the current registered handler inventory and runtime status, see:

- [Pi Event Manager: Handlers and Current State](event-manager-handlers-and-current-state.md)

## Requirement

The event manager must run against deployed rules (`rules.pd`) and use a clear event boundary on both sides:

- Pi side:
  - orchestration, scoring/state, UI and non-real-time logic
  - publishes commands/events to ESP only through the bridge
- ESP side:
  - real-time runtime and safety enforcement
  - executes immediate hardware logic locally
  - publishes telemetry/events upstream to Pi

Transport requirement:

- Frames-only JSON protocol
- No line-based command path
- `reqId` correlation for response-required RPC
- fire-and-forget path for high-volume events

## Implementation: Single Hook Points

## 1) Pi -> ESP command/event ingress (Bridge TX)

Bridge receives RPC/socket commands and funnels them through a single framed send path:

- Command intake and dispatch loop:
  - `src/pinballctl/bridge/daemon.py:1201`
  - `src/pinballctl/bridge/daemon.py:1231`
- Single serial send function:
  - `src/pinballctl/bridge/daemon.py:224`

This is the Pi-side hook for outbound event manager integration.

## 2) ESP inbound framed command ingress

All framed inbound serial data is parsed in `System::loop()` and forwarded to protocol handler:

- Framed RX parse + dispatch:
  - `src/firmware/src/System.cpp:107`
  - `src/firmware/src/System.cpp:174`

Then protocol-level event commands are handled centrally:

- `EVENT`, `EVENT_FIRE`, `EVENT_STATS`, `EVT_STREAM_*`:
  - `src/firmware/src/protocol/ProtocolHandler.cpp:420`

This is the ESP-side hook for rules/event handler evaluation.

## 3) ESP -> Pi event ingress (Bridge RX + bus publish)

All decoded ESP JSON messages are routed through one handler:

- Message router:
  - `src/pinballctl/bridge/daemon.py:1324`

Event publishing to Pi bus is centralized there:

- Bus emit for `EVT`/`EVENT`:
  - `src/pinballctl/bridge/daemon.py:1379`

This is the Pi-side inbound hook for event handler registration/execution.

## Practical Integration Plan

1. Keep transport layer unchanged (already validated by soak tests).
2. Add rule-evaluation calls only at these hook points.
3. Keep response-required RPC and fire-and-forget event paths distinct.
4. Keep ESP local-first for real-time actions; only publish required upstream events.
5. Preserve `reqId`/sequence correlation and metrics for observability.

This keeps implementation centralized and avoids protocol/handler scattering across modules.
