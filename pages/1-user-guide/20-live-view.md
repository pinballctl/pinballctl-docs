# Live View

Live View is the runtime emulator page for watching table events in real time.

It is read-only for configuration and is intended for live validation of event flow, rule outputs, playfield animations, and media displays.

<img src="./media/screenshot-feature-live-view.webp" data-source='{"url":"/login","next_url":"/liveview","dark_mode":true,"settle_ms":3000,"click":[{"action":"type","selector":"input[name=\"username\"]"},{"action":"type","selector":"input[name=\"password\"]"},{"action":"click","selector":"button[type=\"submit\"]","wait_for":"[data-menu-toggle]"}]}' alt="Live View feature overview" style="width: 100%;height: auto;">

## Purpose

Use Live View to:

- monitor incoming hardware events
- validate rule-triggered output behavior visually
- test keyboard shortcuts and trigger mappings
- preview active media runtime displays in the right column

Live View does not edit playfield, hardware, rules, lighting, audio, or media configs.

## Page Structure

Live View has a single tab:

1. `Live View`

Main areas:

- left: playfield runtime stage (scaled table)
- right: display runtime cards (one card per enabled media display)

Each display card:

- uses the configured display title in the card header
- keeps a `100%` width preview area
- preserves configured display width/height ratio
- renders the live media runtime output for that display

## Runtime Interaction

Keyboard input:

- shortcuts mapped in Playfield keymap trigger the matching hardware gestures/events

Mouse input:

- right-click a component on the table to open available trigger actions
- context menu actions are sourced from configured hardware rule triggers for that source
- selecting a menu action fires the corresponding event path immediately
- for button components with both `PRESSED` and `RELEASED` bindings, a combined `PRESSED + RELEASED` option is available

## Event + Visual Behavior

Live View listens to the event stream and applies visual feedback:

- button press pulse/highlight
- plunger pulse animation
- flipper kick/hold visuals
- output state visuals (for supported types)

Rule action mapping is used so table visuals follow configured trigger/action relationships.

## Media Integration

Live View display cards are connected to media runtime display endpoints.

As media scenes change via rules/events, display cards update automatically without opening separate kiosk windows.

## Typical Workflow

1. Open `Live View`.
2. Trigger real hardware input or keyboard shortcuts.
3. Verify table animations on the stage.
4. Verify media overlays/displays in the right column.
5. Use component right-click actions to test specific trigger paths.

## Related Features

- [Playfield](9-layout.md)
- [Rules](7.1-rules.md)
- [Media](18-media.md)
- [Scoring](10-scoring.md)
- [Logs](14-logs.md)
