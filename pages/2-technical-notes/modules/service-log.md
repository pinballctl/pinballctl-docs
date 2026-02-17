# Service Log Module

## Purpose

Tracks maintenance/service records, notes, and attachments.

## Functionality

- Creates, updates, and reads service entries.
- Stores associated attachment records/files.
- Supports audit-style maintenance history.

## Key Endpoints

- `GET /api/service/log`
- `POST /api/service/log`
- `POST /api/service/log/<entry_id>`
- `GET /api/service/log/<entry_id>`
- `GET /api/service/attachment/<filename>`
