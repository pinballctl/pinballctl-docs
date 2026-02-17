# Firmware Module

## Purpose

Manages firmware artifacts and update package handling.

## Functionality

- Lists local and remote firmware versions.
- Downloads remote firmware assets.
- Deletes single/all local versions.
- Serves firmware download files.

## Key Endpoints

- `GET /api/firmware/versions`
- `GET /api/firmware/versions/remote`
- `POST /api/firmware/delete`
- `POST /api/firmware/delete/all`
- `GET /api/firmware/download/<filename>`
