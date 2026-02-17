# Media

Media is the scene authoring feature for videos and on-screen overlays.

It lets you build stage scenes, preview them in-browser, and launch kiosk windows on configured displays.

## Page Structure

Media is split into four tabs:

1. `Stage`
2. `Library`
3. `Displays`
4. `Runtime`

## Stage Tab

<img src="/api/manual/assets/screenshots/feature-media-stage.png" alt="Media stage tab" style="width: 100%; max-width: 800px; height: auto;">

Stage is the authoring tab for scene composition and playback preview.

Left panel:

- visual preview stage
- playback controls (`Play / Pause`, `Stop`, scrub bar, time readout)
- launch buttons (`Open Fullscreen`, `Open Small Window`)

Right panel cards:

- `Scenes`: scene dropdown + `+ Add Scene`
- `Options`: scene name, target display, base asset, loop, audio include toggle
- `Overlays`: overlay list + editor + `+ Add Overlay`

Overlay editing includes:

- reorder (up/down)
- collapse/expand per overlay
- position, size, rotation, opacity
- text options (alignment, effects, no-wrap rendering)
- image/frame/variable overlay configuration

## Library Tab

<img src="/api/manual/assets/screenshots/feature-media-library.png" alt="Media library tab" style="width: 100%; max-width: 800px; height: auto;">

Library manages media assets.

Cards:

- `Asset Upload`
  - drag/drop upload
  - file picker upload
  - progress/status feedback
- `Asset Library`
  - asset list with name, type, added date, and actions
  - in-app preview for selected assets

## Displays Tab

<img src="/api/manual/assets/screenshots/feature-media-displays.png" alt="Media displays tab" style="width: 100%; max-width: 800px; height: auto;">

Displays is for output-target configuration and host readiness.

Cards:

- `Detected Displays`
  - display name, role, size, screen mapping, enabled state
  - `Detect` action refresh
- `Runtime Checks`
  - kiosk/runtime dependency checks
  - Chromium/runtime capability status

## Runtime Tab

<img src="/api/manual/assets/screenshots/feature-media-runtime.png" alt="Media runtime tab" style="width: 100%; max-width: 800px; height: auto;">

Runtime shows active scene sessions and runtime controls.

Cards:

- `Runtime`
  - active scene list by display/session
  - per-scene stop actions
- `Controls`
  - global runtime actions such as `Stop All`

## Typical Workflow

1. Build a scene in `Stage`.
2. Choose target display and base asset.
3. Add and tune overlays in preview.
4. Save changes.
5. Launch fullscreen or small window for live validation.
6. Verify/monitor sessions in `Runtime`.

## Related Features

- [Rules](7-rules.md)
- [Lighting](8-lighting.md)
- [Settings](16-settings.md)
