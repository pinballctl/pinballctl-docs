# Bridge Protocol

Bridge communication is framed JSON only.

## Frame Format

- 4-byte big-endian payload length
- UTF-8 JSON payload

## Notes

- No line-based parsing.
- Host commands and responses are framed.
- Keep command payloads explicit and version-friendly.
