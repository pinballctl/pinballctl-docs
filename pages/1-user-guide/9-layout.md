# Playfield

Playfield is the visual editor and runtime simulator for machine layout.

It provides a visual machine model for authoring, key binding, and event-response testing.

## Page Structure

Playfield is split into two tabs:

1. `Stage`
2. `Options`

## Stage Tab

<img src="/api/manual/assets/screenshots/feature-layout-stage.png" alt="Playfield stage tab" style="width: 100%; max-width: 800px; height: auto;">

Stage contains the visual canvas and component editing workflow.

Main areas:

- playfield canvas
- components card
- component inspector (when a component is selected)
- save action in the page header

Component inspector supports:

- appearance and size controls
- bound key capture/removal
- key-down/key-up gesture mapping
- trigger/action test controls
- remove component action

Drag and placement behavior:

- components move by drag on canvas
- selected component is highlighted
- updates persist after `Save Changes`

## Options Tab

<img src="/api/manual/assets/screenshots/feature-layout-options.png" alt="Playfield options tab" style="width: 100%; max-width: 800px; height: auto;">

Options contains layout-level controls.

Primary controls:

- width
- height
- ratio display

Layout actions:

- `Auto Layout`
- `Clear Layout`

Use this tab to quickly regenerate/reset placement without editing each component manually.

## Keyboard Binding System

Binding flow:

1. Select a component in `Stage`.
2. Click `Capture` in inspector.
3. Press a key.
4. Configure key-down and key-up gestures.

This allows interaction testing without physical hardware input.

## Event and Trigger Testing

Playfield can fire bound events and show response state visually.

Common uses:

- validate rule-trigger mappings
- test event-driven reactions
- verify component linkage behavior

## Save Workflow

Recommended flow:

1. Arrange components in `Stage`.
2. Tune layout-level values in `Options`.
3. Test key bindings and events.
4. Click `Save Changes`.

## Related Features

- [Rules](7-rules.md)
- [Lighting](8-lighting.md)
- [Hardware](10-hardware.md)
