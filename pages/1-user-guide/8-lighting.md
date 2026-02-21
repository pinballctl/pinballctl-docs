# Lighting

Lighting is the scene authoring workflow for playfield effects and event-driven feedback.

It lets you build scenes, preview compiler output, and sync lighting data to ESP.

## Page Structure

Lighting is split into two tabs:

1. `Stage`
2. `Fixtures`


## Fixtures Tab

<img src="./media/screenshot-feature-lighting-fixtures.png" data-source='{"url":"/login","dark_mode":true,"settle_ms":420,"click":[{"action":"type","selector":"input[name=\"username\"]"},{"action":"type","selector":"input[name=\"password\"]"},{"action":"click","selector":"button[type=\"submit\"]","wait_for":"[data-menu-toggle]"},{"action":"click","selector":"[data-menu-toggle]","wait_for":"body.flood-open"},{"action":"click","selector":"[data-nav-link][data-module-name=\"lighting\"]","wait_for":"#lighting-tab-fixtures"},{"action":"click","selector":"#lighting-tab-fixtures","wait_for":"#lighting-tab-fixtures-pane.show.active"}]}' alt="Lighting fixtures tab" style="width: 100%;height: auto;">

Sourced from the hardware mapping, the fixtures lists all the lighting hardware available and allow you to further refine the information. The colour can be selected for single LED's and for RGB strips, the number of pixels, length and layout can be defined.

Use it to:

- review available fixtures
- inspect fixture layout/type metadata
- control cast targeting and selection scope
- validate which fixtures a scene will affect


## Stage Tab

<img src="./media/screenshot-feature-lighting-stage.png" data-source='{"url":"/login","next_url":"/lighting","dark_mode":true,"settle_ms":320,"click":[{"action":"type","selector":"input[name=\"username\"]"},{"action":"type","selector":"input[name=\"password\"]"},{"action":"click","selector":"button[type=\"submit\"]","wait_for":"[data-menu-toggle]"}]}' alt="Lighting stage tab" style="width: 100%;height: auto;">

Stage is where scene playback and scene-level authoring happen.

A scene is a set of lighting patterns build up either on a custom timeline or by choosing pre-defined patterns. Multiple scenes can be created and via the Rules manager can be triggered to play individually or layered.

Main areas:

- scene preview/stage area
- scene selector and `Add Scene`
- options/editor card for selected scene
- save and sync actions in the header

Scene options include:

- title
- duration (`seconds`, `minutes`, `frames`)
- end behavior (`stop`, `repeat`, `bounce`)
- pattern selection
- priority and blend mode
- cast scope/mask

When pattern is `Custom Timeline`, timeline editing is available:

- frame scrubber and frame stepping
- marker/tag pins
- clear frame action
- per-frame visual editing

Playback behavior:

- `Play` / `Stop` controls
- preview follows compiled output path
- updates reflect scene/pattern changes after compile

## Top Actions

- `Add Scene`: create a new scene
- `Play` / `Stop`: preview selected scene
- `Sync Lighting`: compile and queue lighting sync to ESP
- `Save Changes`: persist local lighting config

If local and ESP revisions differ, an out-of-sync warning is shown.

## Custom Timeline

The custom timeline gives you exact control of which pixels are on/off and the colour at every specific frame. Pixels can be selected individually or multi selected.

## Timeline Tags

Frame tags are managed from the tag modal.

Rules:

- lowercase letters/numbers with `_` or `-`
- max length `64`
- unique per scene

Tags are available in Rules `Apply Lighting Scene` actions (`Start at: Tag`).

## Save and Sync Workflow

1. Build or edit scene in `Stage`.
2. Validate cast/fixture targeting in `Fixtures`.
3. Click `Save Changes`.
4. Click `Sync Lighting`.

## Related Features

- [Rules](7-rules.md)
- [Playfield](9-layout.md)
- [Hardware](10-hardware.md)
