# Hardware Module

## Purpose

Maps discovered hardware/pins to logical functions used by the authoring/runtime stack.

## Functionality

- Views board metadata and pin availability.
- Loads/saves hardware mapping data.
- Supports mapping reload and sync workflows.
- Provides sync status feedback.

## Key Endpoints

- `GET /api/hardware/meta`
- `GET /api/hardware/pins`
- `GET /api/hardware/mapping`
- `POST /api/hardware/save`
- `POST /api/hardware/sync`
- `GET /api/hardware/sync/status`
