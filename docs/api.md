# API overview

Interactive docs: `/api/docs`

## Auth

- `POST /api/auth/login`
- `GET /api/auth/me`
- `GET|POST /api/users`
- `PATCH /api/users/{id}`

## Master data

- `/api/supervisors`
- `/api/machines`
- `/api/shifts`
- `/api/stoppage-reasons`

GET is authenticated. POST/PATCH are admin-only.

## Stoppages

- `GET /api/stoppages` pagination + filters: date_from, date_to, shift_id, supervisor_id, machine_id, reason_id, search, page, page_size, sort_by, sort_order
- `POST /api/stoppages`
- `GET|PATCH|DELETE /api/stoppages/{id}`

List responses:

```
{ "data": [], "pagination": { "page": 1, "page_size": 50, "total": 250 } }
```

Errors:

```
{ "error": { "code": "VALIDATION_ERROR", "message": "..." } }
```

## Dashboard and reports

- `GET /api/dashboard/summary`
- `GET /api/reports/excel?report_type=raw|summary|complete`
- `GET /api/reports/pdf`

## Realtime

- `WS /api/ws?token=...`

Events: `stoppage.created`, `stoppage.updated`, `stoppage.deleted`
