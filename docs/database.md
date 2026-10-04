# Database

PostgreSQL, normalized around `stoppage_records`.

## Tables

- `users` login accounts (`admin` | `supervisor`), optional `supervisor_id` for future individual accounts
- `supervisors` business supervisor names
- `machines` machine codes, `active` flag
- `shifts` A/B/C including `crosses_midnight`
- `stoppage_reasons` including `requires_details`, `measurement_type`
- `stoppage_records` one row per event

## Stoppage record fields

id, production_date, shift_id, supervisor_id, machine_id, stoppage_reason_id, duration_minutes, details, remarks, created_at, updated_at, created_by, updated_by, deleted_at

`duration_minutes` is `Numeric(10,2)` with a check constraint `> 0`.

## Indexes

production_date, shift_id, supervisor_id, machine_id, stoppage_reason_id, created_at, deleted_at, plus composites on (production_date, shift_id) and (production_date, machine_id).

Foreign keys do not cascade-delete historical stoppages. Master data is deactivated instead of removed.
