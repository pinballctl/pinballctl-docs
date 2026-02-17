# Rules Module

## Purpose

Authoring surface for gameplay/event rules that drive machine behavior.

## Functionality

- Loads and edits rulesets.
- Saves rules to persisted JSON.
- Integrates with bridge command flow for ESP updates.
- Exposes sync/status paths for deployment visibility.

## Key Endpoints

- `GET /api/rules/catalog`
- `GET /api/rules/list`
- `POST /api/rules/save`
- `POST /api/rules/sync`
- `GET /api/rules/sync/status`
