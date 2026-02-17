# Lighting Module – Technical Specification (Draft)

## 1. Purpose

The **Lighting Module** provides centralized control over all illuminated elements on the pinball machine.
Rather than toggling individual LEDs, the module defines **lighting groups** and **sequences** that can be triggered by rules, creating coordinated lighting effects and animations.

It forms the foundation for:
- Dynamic light shows (e.g., attract mode, multiball, bonus count)
- Real-time response to gameplay events (targets, bumpers, launches)
- Timeline-based sequencing and layered playback

---

## 2. Core Concepts

### 2.1 Lighting Groups
A **Lighting Group** (working name: *Light Group*, *Channel*, or *Fixture Group*) represents a logical collection of LEDs or strips.

Each group has:
- **Name / ID**
- **Hardware mapping** (one or more LEDs or LED strips)
- **Type**
  - `single` – individual RGB or mono LED
  - `strip` – addressable LED strip (e.g., 30 LEDs)
  - `matrix` (future) – 2D panel or complex zone
- **Default color / state**
- **Capabilities** – e.g. RGB, brightness control, patterns supported

Lighting groups abstract the hardware so sequences can target logical groups instead of raw pins.

---

### 2.2 Patterns

A **Pattern** defines a behavior or animation that can be applied to a group.
Patterns may be static, timed, or continuous.

**Examples:**
- **Static**
  `On Red`, `Off`, `On Blue 500ms`
- **Transition**
  `Fade to color over [n] ms`, `Pulse`
- **Looped / Animated**
  `Chase`, `Rainbow`, `Knight Rider`, `Sparkle`, `Fill-Drain`

Each pattern includes:
- `type` (enum)
- `duration` (optional)
- `color(s)`
- `parameters` (speed, brightness, direction)
- `behavior` (`loop`, `once`, `fade`, etc.)

---

### 2.3 Sequences

A **Sequence** is a timeline of lighting actions applied to one or more groups.
It defines what happens **over time** — like a mini show.

**Structure:**
```json
{
  "name": "Launch Sequence",
  "duration": 5000,
  "tracks": [
    {
      "group": "LeftStrip",
      "events": [
        { "time": 0, "pattern": "On Red" },
        { "time": 1000, "pattern": "FadeOff", "duration": 800 }
      ]
    },
    {
      "group": "PlayfieldGI",
      "events": [
        { "time": 0, "pattern": "Rainbow", "duration": 4000 }
      ]
    }
  ]
}
```

Each track controls one lighting group over a timeline.
Multiple sequences can run simultaneously.

---

### 2.4 Scenes

A **Scene** represents a reusable lighting setup or “mode,” e.g.:
- `Attract`
- `Gameplay`
- `Multiball`
- `Launch`
- `Bonus`

Scenes reference one or more sequences and define how they interact (overlay, interrupt, fade in/out).

---

## 3. Interaction Model

### 3.1 Rule Integration

Rules trigger lighting actions:

```json
{
  "rule": "Launch",
  "trigger": "LaunchButtonPressed",
  "actions": [
    { "type": "fire_coil", "id": "LaunchCoil" },
    { "type": "play_sound", "file": "rocket.wav" },
    { "type": "start_lighting", "sequence": "Launch" }
  ]
}
```

Lighting actions are sent to the lighting engine with parameters:
- `sequence`: name or ID
- `mode`: `overlay | replace | interrupt`
- `layer`: optional numeric priority (for layering)

---

### 3.2 Playback Modes

| Mode | Description |
|------|--------------|
| **Replace** | Stops current lighting and plays new sequence exclusively |
| **Overlay** | Adds on top of existing sequences; both render together |
| **Interrupt** | Pauses background sequence, runs temporary effect, then resumes |
| **Additive (future)** | Blends light values instead of replacing them |

---

## 4. Editor UI (Web)

The web interface (Flask + Alpine.js) will evolve to include:

### 4.1 Sequence Timeline View
- Displays the **Playfield table view** (read-only background)
- Selects LEDs or groups visually
- Shows time axis at bottom
- Add, move, or resize lighting “blocks” representing patterns
- Scrub/play preview over time

### 4.2 Scene Management
- List of available scenes (Attract, Gameplay, Bonus, etc.)
- Buttons: `Create`, `Edit`, `Duplicate`, `Delete`
- For each scene:
  - Assign included sequences
  - Define transition/overlay behavior

### 4.3 Pattern Editor
- Visual configuration for custom patterns
- Preview color, speed, direction

---

## 5. Runtime Behavior (Backend + ESP)

| Component | Responsibility |
|------------|----------------|
| **Pi (Flask / pinballctl)** | Defines, stores, and triggers lighting sequences |
| **ESP32 Firmware** | Receives pattern and group data, executes animations in real time |
| **Bridge** | Translates scene/sequence events from Flask to ESP messages |
| **Rules Engine** | Fires lighting triggers via `start_lighting` actions |

Example bridge command:
```
LIGHTSEQ START name=Launch mode=overlay
```
or direct group command:
```
LIGHTGROUP SET group=LeftStrip pattern=Rainbow duration=4000
```

### 5.1 Runtime Layering Model (Reference)

The runtime model should support **multiple active scene instances** and resolve output per fixture/pixel every tick.

Primary goals:
- Keep a low-priority base scene running (`Attract`, `InGame`).
- Allow temporary overlays (`Bonus`, `Mode`, `Jackpot`) to take control of only their cast.
- Support interrupt behavior: pause underlying scene(s), play insert scene, resume exactly where paused.

#### 5.1.1 Active Scene Instances

Each active scene instance tracks:
- `sceneId`
- `instanceId`
- `priority` (higher wins)
- `state` (`running | paused | stopped | completed`)
- `clockMs` (frozen while paused)
- `startedAtMs`
- `cast` (fixture/pixel scope)
- `onComplete` policy

Notes:
- Multiple instances of different scenes may run concurrently.
- By default, one scene may have at most one active instance unless explicitly allowed.

#### 5.1.2 Ownership and Arbitration

For each fixture/pixel output slot:
1. Collect all active scene instances that currently address that slot.
2. Select the highest-priority active writer.
3. Apply that writer’s value.
4. If no active writer exists, fall through to lower layers, then default/off.

This gives deterministic behavior where `Bonus` can temporarily take control of inserts also used by `InGame`.

#### 5.1.3 Playback Policies

Recommended start modes:
- `replace`: stop all lower/equal-priority scenes and start new scene.
- `overlay`: start scene without stopping others; arbitration handles conflicts.
- `interrupt`: pause selected underlying scenes, run new scene, resume paused scenes on completion.

Recommended completion policies:
- `stop`: scene ends; no follow-up action.
- `resume_under`: resume scenes paused by this instance.
- `restore_snapshot` (future): restore exact output snapshot before interrupt.

#### 5.1.4 Time Semantics

- Scene clocks advance only when `running`.
- `paused` scenes keep their current frame/time and continue from that exact point when resumed.
- `repeat` and `bounce` behavior remains scene-local and should not affect other scene clocks.

#### 5.1.5 Precompiled Data and Metadata

Scenes remain precompiled linear instructions, with runtime metadata attached per scene:
- `priority` (default low for base scenes)
- `cast` mask/scope
- `blendMode` (start with `override` only)
- `onComplete` policy

Initial implementation guidance:
- Start with `override` blending only.
- Add additive/max blend modes only after deterministic override layering is stable.

#### 5.1.6 ESP/Pi Responsibility Split

- **Pi**: authoring, validation, compile, orchestration requests.
- **ESP**: real-time scene-instance scheduler, arbitration, safety-constrained output.

The ESP runtime should be the authority for final per-tick output resolution.

#### 5.1.7 Control Command Shape (Framed JSON)

All runtime control commands must use framed JSON transport.

Suggested control set:
- `SCENE_START` `{sceneId, mode, priority?, onComplete?, instanceId?}`
- `SCENE_STOP` `{sceneId|instanceId|all}`
- `SCENE_PAUSE` `{sceneId|instanceId}`
- `SCENE_RESUME` `{sceneId|instanceId}`
- `SCENE_STATUS` / `GET_SCENE_STATUS` (active instances, states, priorities, clocks)

This supports:
- `Attract -> InGame` transitions,
- overlay feedback scenes (e.g. bonus inserts),
- pause/play inserts that resume the main scene cleanly.

---

## 6. Hardware Integration

Lighting groups map to hardware via the **Hardware Module**:
- Each hardware entry may declare a lighting capability:
  - `type`: `single | strip`
  - `rgb`: true/false
  - `count`: number of addressable LEDs (if strip)
- This metadata informs the Lighting Module what patterns are valid for that group.

If unspecified, defaults to a single RGB LED.

---

## 7. File & Data Structure

| File | Purpose |
|------|----------|
| `lighting/groups.json` | Defines lighting groups and hardware mappings |
| `lighting/patterns.json` | Stores reusable pattern templates |
| `lighting/sequences.json` | Stores timeline-based sequences |
| `lighting/scenes.json` | Defines scene configurations (collections of sequences) |

All files share the same versioning system used in other modules.

---

## 8. Future Extensions

| Feature | Description |
|----------|--------------|
| **Live Preview** | Play sequences directly in the Playfield table |
| **Beat Sync** | Time lighting to music or sound effects |
| **Conditional Logic** | Sequence branches depending on game state |
| **Parameter Modulation** | Control brightness or hue dynamically via gameplay variables |
| **Hardware Discovery** | Auto-map LED strips and bulbs from ESP report |
| **Palette System** | Define reusable color sets and gradients |

---

## 9. Design Notes

- The **Lighting Module** will **not** control individual bulbs directly; it manages logical groups.
- Sequences will support **nested playback**, allowing a "global" ambient pattern with localized effects layered on top.
- The playback engine must maintain frame consistency — ideally at 30–60Hz — but interpolate smoothly when triggered by low-frequency events.
- Timekeeping and blending are handled on the Pi for preview; ESP runs lightweight interpreted pattern commands for real output.

---

## 10. Naming Ideas for “Lighting Groups”

Candidate terms (choose one standard name):
- **Fixture**
- **Channel**
- **Zone**
- **Light Group**
- **Lighting Node**
- **Cluster**

(Recommended: **Fixture** — it’s standard in lighting design and scales well to multi-LED strips or logical regions.)

---

## 11. Development Phases

| Phase | Scope |
|-------|--------|
| **Phase 1** | Define schema + CRUD for groups, patterns, sequences, and scenes |
| **Phase 2** | Basic UI to create and trigger patterns manually |
| **Phase 3** | Timeline editor + table visualization |
| **Phase 4** | Runtime integration with rule system |
| **Phase 5** | Real-time bridge integration with ESP for live playback |





## Original Requirements
The next module I would like to create is for lighting. I am not quite sure how this one is going to go or how easy it would be. Here are my thoughts.

Rather than controlling and changing individual bulbs and LED strips I would like to setup [find a name to describe lighting groups] that define patterns, this could be a simple "On Red", "Off" and start to get more complex "On and Red for [n] ms, fade off over [n] ms" or apply patterns such as rainbow, chase.

Eventually I would like to create an option where we create a time line and over time we can turn stuff on, off or select a pattern to play over a subset of the time.

It would be great to have the table displayed (From the Playfield) From here individual leds or strips can be selected and the on/off or colour selected for that moment in time. We can then scrub, play the sequence and it will be visually displayed. None light elements would be displayed but faded out.

From this we can then create scenes for "Attract", Bonus, etc

The Rules will then trigger these lighting displays.

Rule: Launch
Triggered by "Launch Button Press"
Actions:
- Fire Launch solanoid
- Play rocket sound
- Trigger "Launch lighting"

Random thoughts:

- Sequence's will need to be configured with a light type, single LED or Strip. If a strip is it RGB and how many LEDs does it have. Will we need to update the harware module so when we map a type we know how many bulbs it has .. or dont we care and just let the lighting module deal with it.

- How do overlaps work. We might have a "In game" sequence playing. But then the launch sequence is started. Does this STOP or Pause the gameplay sequence, play the launch then continue with the gameplay. We could potentially have multiple layers. A target is hit with flashed the "target" leds making them flash, but we still want the game play sequence to stay running.

These leads me to think about if a sequence "overlays" or interrupts, or replaces.

I dont want you to code this yet. I want to create a requirements and specification on this with you padding it out and making it a suitable technical spec covering as much detail as possible. Please keep the formatting simple and in a way I can present it back to you when I am ready for the module to be created.
