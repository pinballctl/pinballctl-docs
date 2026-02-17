# Pinball Event-to-Action Engine

This document describes an event/action engine that connects hardware
events (like button presses) to actions (like firing coils or flashing
lights) in the Pinball project.

------------------------------------------------------------------------

## Overview

The engine: - Loads hardware mapping from `mapping.json` - Defines rules
connecting input events to sequences of actions - Supports
press/hold/release semantics for coils and buttons - Handles coil safety
and timeouts - Sends commands to ESP bridge (HTTP or serial) - Can be
embedded in `pinballctl` or run standalone

------------------------------------------------------------------------

## Example `mapping.json`

``` json
{
  "hardware": {
    "L_FLIP_COIL": { "type": "coil", "key": "coil_01", "max_on_ms": 150 },
    "L_FLIP_HOLD_COIL": { "type": "coil", "key": "coil_01", "max_on_ms": 150 },
    "L_FLIP_LED": { "type": "led", "key": "led_05" },
    "BUTTON_LEFT": { "type": "button", "key": "btn_02" }
  },
  "rules": [
    {
      "name": "Left Flipper (tap or hold)",
      "trigger": { "event": "BUTTON_LEFT_PRESSED", "source": "BUTTON_LEFT" },
      "on_press": [
        {
          "action": "coil_pulse_or_hold",
          "params": {
            "coil": "L_FLIP_COIL",
            "pulse_ms": 40,
            "hold_enabled": true,
            "hold_coil": "L_FLIP_HOLD_COIL",
            "max_hold_ms": 150
          }
        },
        {
          "action": "led_flash",
          "params": { "led": "L_FLIP_LED", "duration_ms": 100 }
        }
      ],
      "on_release": [
        {
          "action": "release_hold_coil",
          "params": { "coil": "L_FLIP_HOLD_COIL" }
        }
      ]
    }
  ]
}
```

------------------------------------------------------------------------

## `bridge_client.py`

``` python
# File: bridge_client.py
import requests
from typing import Dict, Any

class BridgeClient:
    def __init__(self, base_url: str = "http://localhost:5001/bridge"):
        self.base_url = base_url.rstrip("/")

    def send_command(self, device_key: str, command: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/command"
        payload = {"device_key": device_key, "command": command, "params": params or {}}
        try:
            r = requests.post(url, json=payload, timeout=1.5)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            print(f"[BridgeClient] send_command error: {e} payload={payload}")
            return {"ok": False, "error": str(e)}
```

------------------------------------------------------------------------

## `actions.py`

``` python
# File: actions.py
import threading
import time
from typing import Dict, Any, Optional
from bridge_client import BridgeClient

class CoilState:
    def __init__(self):
        self.state = {}
        self.lock = threading.Lock()

    def ensure(self, coil_key):
        with self.lock:
            if coil_key not in self.state:
                self.state[coil_key] = {"last_on": 0.0, "last_off": 0.0, "is_on": False, "lock": threading.Lock()}

    def set_on(self, coil_key):
        self.ensure(coil_key)
        with self.state[coil_key]["lock"]:
            self.state[coil_key]["is_on"] = True
            self.state[coil_key]["last_on"] = time.time()

    def set_off(self, coil_key):
        self.ensure(coil_key)
        with self.state[coil_key]["lock"]:
            self.state[coil_key]["is_on"] = False
            self.state[coil_key]["last_off"] = time.time()

coil_state = CoilState()

class Actions:
    def __init__(self, mapping: Dict[str, Dict], bridge: BridgeClient):
        self.mapping = mapping
        self.bridge = bridge

    def resolve_key(self, logical_name: str) -> Optional[str]:
        entry = self.mapping.get(logical_name)
        if not entry:
            print(f"[Actions] unknown hardware name: {logical_name}")
            return None
        return entry.get("key")

    def coil_on(self, logical_coil: str) -> None:
        coil_key = self.resolve_key(logical_coil)
        if not coil_key:
            return
        coil_state.set_on(coil_key)
        self.bridge.send_command(coil_key, "coil_on", {})

    def coil_off(self, logical_coil: str) -> None:
        coil_key = self.resolve_key(logical_coil)
        if not coil_key:
            return
        self.bridge.send_command(coil_key, "coil_off", {})
        coil_state.set_off(coil_key)

    def led_flash(self, logical_led: str, duration_ms: int = 100) -> None:
        led_key = self.resolve_key(logical_led)
        if not led_key:
            return
        self.bridge.send_command(led_key, "led_on", {})
        t = threading.Timer(duration_ms / 1000.0, lambda: self.bridge.send_command(led_key, "led_off", {}))
        t.start()

    def safe_coil_pulse(self, logical_coil: str, pulse_ms: int, max_on_ms: int = 200):
        duration = min(pulse_ms, max_on_ms)
        self.coil_on(logical_coil)
        t = threading.Timer(duration / 1000.0, lambda: self.coil_off(logical_coil))
        t.start()

    def coil_pulse_or_hold(self, ctx: Dict[str, Any], params: Dict[str, Any]):
        coil = params["coil"]
        pulse_ms = params.get("pulse_ms", 40)
        hold_enabled = params.get("hold_enabled", False)
        hold_coil = params.get("hold_coil", coil)
        max_hold_ms = params.get("max_hold_ms", 150)
        self.safe_coil_pulse(coil, pulse_ms, max_on_ms=max_hold_ms)
        if hold_enabled:
            def start_hold_after_pulse():
                if ctx.get("released", False):
                    return
                self.coil_on(hold_coil)
                t_off = threading.Timer(max_hold_ms / 1000.0, lambda: self.coil_off(hold_coil))
                t_off.start()
                ctx["hold_off_timer"] = t_off
            t_switch = threading.Timer(pulse_ms / 1000.0, start_hold_after_pulse)
            t_switch.start()
            ctx["hold_coil"] = hold_coil

    def release_hold_coil(self, ctx: Dict[str, Any], params: Dict[str, Any]):
        coil = params["coil"]
        t = ctx.get("hold_off_timer")
        if t and isinstance(t, threading.Timer):
            t.cancel()
        self.coil_off(coil)
```

------------------------------------------------------------------------

## `event_engine.py`

``` python
# File: event_engine.py
import json
import threading
import time
from queue import Queue, Empty
from typing import Dict, Any
from bridge_client import BridgeClient
from actions import Actions

event_queue = Queue()

class EventEngine:
    def __init__(self, mapping_path: str, bridge_base: str = "http://localhost:5001/bridge"):
        self.mapping_path = mapping_path
        self.mapping = {}
        self.rules = []
        self.bridge = BridgeClient(bridge_base)
        self.actions = None
        self.running = False
        self.worker_thread = None
        self.active_contexts = {}
        self._load_mapping()

    def _load_mapping(self):
        with open(self.mapping_path, "r") as fh:
            doc = json.load(fh)
        self.mapping = doc.get("hardware", {})
        self.rules = doc.get("rules", [])
        self.actions = Actions(self.mapping, self.bridge)

    def start(self):
        self.running = True
        self.worker_thread = threading.Thread(target=self._run_loop, daemon=True)
        self.worker_thread.start()

    def stop(self):
        self.running = False
        if self.worker_thread:
            self.worker_thread.join(timeout=1.0)

    def post_event(self, event: Dict[str, Any]):
        event_queue.put(event)

    def _run_loop(self):
        while self.running:
            try:
                ev = event_queue.get(timeout=0.2)
            except Empty:
                continue
            try:
                self._handle_event(ev)
            except Exception as e:
                print("[EventEngine] error:", e)

    def _handle_event(self, ev: Dict[str, Any]):
        name = ev.get("event")
        src = ev.get("source")
        for rule in self.rules:
            trig = rule.get("trigger", {})
            if trig.get("event") != name:
                continue
            if "source" in trig and trig["source"] != src:
                continue
            if name.endswith("_PRESSED"):
                ctx = {"rule": rule.get("name"), "event": ev, "released": False}
                key = f"{rule.get('name')}::{src}"
                self.active_contexts[key] = ctx
                for act in rule.get("on_press", []):
                    self._exec_action(ctx, act)
            elif name.endswith("_RELEASED"):
                key = f"{rule.get('name')}::{src}"
                ctx = self.active_contexts.get(key, {"event": ev})
                ctx["released"] = True
                for act in rule.get("on_release", []):
                    self._exec_action(ctx, act)
                if key in self.active_contexts:
                    del self.active_contexts[key]

    def _exec_action(self, ctx: Dict[str, Any], act: Dict[str, Any]):
        name = act.get("action")
        params = act.get("params", {})
        if name == "coil_pulse_or_hold":
            self.actions.coil_pulse_or_hold(ctx, params)
        elif name == "release_hold_coil":
            self.actions.release_hold_coil(ctx, params)
        elif name == "led_flash":
            self.actions.led_flash(params.get("led"), params.get("duration_ms", 100))
        else:
            self.actions.run_action(name, ctx, params)
```

------------------------------------------------------------------------

## Integration

-   The ESP bridge should POST events such as:

    ``` json
    { "event": "BUTTON_LEFT_PRESSED", "source": "BUTTON_LEFT", "ts": 169... }
    ```

-   `BridgeClient` sends commands to ESP via `/bridge/command` endpoint
    or serial.

-   Put `mapping.json` under your instance path (same as
    `hardware/api.py`).

------------------------------------------------------------------------

## Safety Recommendations

-   Enforce coil `max_on_ms` in both ESP firmware and the Pi.
-   Implement minimum off-time between pulses.
-   Add watchdog to disable coils on fault.
-   Extend coil state tracking to detect overheat or missed release.

------------------------------------------------------------------------

## Next Steps

-   Add UI for rule editing
-   Add conditional logic and sequences
-   Integrate event logging with your `LogManager`
-   Simulate hardware for testing

------------------------------------------------------------------------
