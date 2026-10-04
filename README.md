# Production Downtime Management System

Enterprise web application for **manual** machine stoppage / downtime data collection, analysis, Excel/PDF reporting, and live dashboard updates.

This system does **not** monitor machine running status. There is no PLC, IoT, sensor, Oracle, SAP, or ERP integration.

## Technology stack

- Frontend: React, TypeScript, Vite, Tailwind CSS, MUI, TanStack Query, React Hook Form, Zod, Recharts
- Backend: Python, FastAPI, Pydantic, SQLAlchemy 2.x, Alembic
- Database: PostgreSQL
- Realtime: WebSocket
- Reports: openpyxl, ReportLab

## Architecture

```
frontend/   React SPA
backend/    FastAPI layered API (routes → schemas → services → repositories → database)
docs/       Business rules, assumptions, API, deployment
```

## Local setup

1. Copy environment file:

```
copy .env.example .env
```

2. Start PostgreSQL (Docker):
    
```
docker compose up db -d
```

3. Backend:

```
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt    docker compose build backend   docker compose run --rm backend alembic upgrade head
alembic upgrade head
python -m app.db.seed            docker compose run --rm backend python -m app.db.seed
uvicorn app.main:app --reload --port 8000
```

4. Frontend:

```
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

### Development credentials (not for production)

- Admin: `admin` / `ChangeMeAdmin123!`
- Shared supervisor: `supervisor` / `ChangeMeSupervisor123!`

Optional demo stoppages (development only):

```
python -m app.db.seed_demo
```

## Docker

```
docker compose up --build
```

- API: http://localhost:8000/api/docs
- UI: http://localhost:8080

## Testing

```
cd backend
pytest
```

```
cd frontend
npm test
npm run build
```

## Important business rules

- Each stoppage is stored as its own row. Repeated reasons are never merged.
- Shift C starts at 22:00 and ends at 06:00 the next calendar day, but the **production date** remains the date Shift C started.
- Between 00:00 and 05:59, current shift is C and current production date is the previous calendar date.
- Downtime is integer minutes in this version.
- Ownership for supervisor edits currently uses the selected supervisor (or created_by for the shared account). Login identity is separate from the business supervisor field because a shared supervisor login is in use.

See `docs/business-rules.md` and `docs/assumptions.md`.
