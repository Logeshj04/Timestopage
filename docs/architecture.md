# Architecture

The application is a single deployable system (not microservices).

## Layers (backend)

- `app/api` HTTP and WebSocket routes
- `app/schemas` Pydantic request/response models
- `app/services` business rules, authorization, transactions
- `app/repositories` SQLAlchemy queries
- `app/models` database mapping
- `app/reports` Excel and PDF generation
- `app/websocket` connection manager and events
- `app/core` configuration, security, timezone, errors

Stoppage create flow:

validate → insert → commit → broadcast `stoppage.created`

Events are not broadcast before commit.

## Frontend

Feature folders under `src/pages`, `src/features`, `src/services`. Server state uses TanStack Query. WebSocket events invalidate dashboard and history queries rather than patching charts in memory.

## Branding

Company name, application name, and logo/favicon are configuration/branding assets (`frontend/src/config/branding.ts`, `frontend/public/favicon.svg`, environment variables). They can be changed without rewriting screens.
