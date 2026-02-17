# Technical Architecture

The stack is split between Pi orchestration and ESP runtime.

## Pi (Authoring + Orchestration)

- Flask web modules
- Bridge daemon
- Persistent user configuration

## ESP (Runtime + Safety)

- Real-time switch/coils/LED processing
- Safety enforcement
- Fault handling

## Data Flow

- User edits rules/config in UI.
- Pi persists and compiles state.
- Pi deploys framed JSON commands to ESP bridge.
