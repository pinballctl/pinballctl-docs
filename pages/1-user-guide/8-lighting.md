# Lighting

Lighting is the scene authoring workflow for playfield effects and event-driven feedback.

It lets you build scenes, preview compiler output, and sync lighting data to ESP.

## Page Structure

Lighting is split into two tabs:

1. `Stage`
2. `Fixtures`

## Stage Tab

<img src="/api/manual/assets/screenshots/feature-lighting-stage.png" alt="Lighting stage tab" style="width: 100%; max-width: 800px; height: auto;">

Stage is where scene playback and scene-level authoring happen.

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

## Fixtures Tab

<img src="/api/manual/assets/screenshots/feature-lighting-fixtures.png" alt="Lighting fixtures tab" style="width: 100%; max-width: 800px; height: auto;">

Fixtures is focused on fixture inventory, targeting, and per-fixture context.

Use it to:

- review available fixtures
- inspect fixture layout/type metadata
- control cast targeting and selection scope
- validate which fixtures a scene will affect

This tab is useful when tuning cast masks or checking fixture coverage before sync.

## Top Actions

- `Add Scene`: create a new scene
- `Play` / `Stop`: preview selected scene
- `Sync Lighting`: compile and queue lighting sync to ESP
- `Save Changes`: persist local lighting config

If local and ESP revisions differ, an out-of-sync warning is shown.

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
