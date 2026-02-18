# Hardware

Hardware is the feature for physical I/O mapping and controller integration setup.

It manages pin-level mapping, safety defaults, friendly names, and function assignment.

<img src="./media/screenshot-feature-hardware.png" data-source='{"url":"/login","next_url":"/hardware","dark_mode":true,"settle_ms":320,"click":[{"action":"type","selector":"input[name=\"username\"]","value":"admin"},{"action":"type","selector":"input[name=\"password\"]","value":"password"},{"action":"click","selector":"button[type=\"submit\"]","wait_for":"[data-menu-toggle]"}]}' alt="Hardware feature overview" style="width: 100%; max-width: 800px; height: auto;">

## What This Feature Does

Hardware defines machine I/O in a structured form used by:

- Rules trigger/action targeting
- Lighting cast and fixture context
- ESP deployment and runtime mapping

## Top Controls

- `Reload Pins`
- `Sync to ESP`
- `Save Mapping`

Behaviour:

- unsaved changes show an `Unsaved changes` badge
- save/sync flows include validation and progress states
- sync may request save first when local edits are pending

## Mapping Table Columns

- UID
- Board
- Type
- Notes
- Channel
- PIN State
- PIN Safe
- Friendly Name
- Function

`Table Key` modal explains each column in plain language.

## Editing Fields

### Friendly Name

Editable for mappable pins. Used across UI labels and selectors.

### Function

Select logical function used by runtime and authoring features.

### PIN Safe

For eligible general GPIO pins, choose safe state:

- default
- HIGH
- LOW

Applied for safe inactive/fault conditions.

## Show All Pins Toggle

`Show all Pins` displays normally-hidden reserved/limited pins.

Default view filters to safer, mappable pin rows.

## Save Mapping

`Save Mapping` writes local mapping configuration.

On success:

- dirty state clears
- success toast/message is shown

## Sync to ESP

The Sync button indicates whether the configuration is in sync with the ESP.

- If mapping is not synced, the sync action shows a warning state (`Sync <name>` warning).
- If mapping is synced, the sync action shows the blue disabled OK state.


## Reload Pins

`Reload Pins` refreshes discovered pin set from ESP source.

Use when:

- firmware pin definitions changed
- hardware board changed
- UID/channel set needs refresh

## Practical Setup Examples

### Initial machine mapping

1. Reload Pins.
2. Name each relevant pin.
3. Assign function roles.
4. Save Mapping.
5. Sync to ESP.

### Safety-first output setup

For output-capable pins:

- set clear Friendly Name
- assign correct output function
- define PIN Safe state for boot/fault behaviour

## Related Features

- [ESPLink](11-esplink.md)
- [Rules](7-rules.md)
- [Lighting](8-lighting.md)
