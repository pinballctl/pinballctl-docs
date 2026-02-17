# Events API Module (Internal)

## Purpose

Internal event bus API used by modules/services to emit and stream events.

## Functionality

- Returns event registry metadata.
- Validates and fires events.
- Streams events over SSE.

## Key Endpoints

- `GET /api/events/registry`
- `POST /api/events/fire`
- `GET /api/events/stream`

## Notes

This module is API-first and hidden from top-level menu navigation.
