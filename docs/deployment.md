# Deployment

1. Set `ENVIRONMENT=production`.
2. Generate strong `SECRET_KEY` and `JWT_SECRET`. Do not use development passwords.
3. Set `CORS_ORIGINS` to the real frontend origin only (never `*` with credentials).
4. Point `DATABASE_URL` at managed PostgreSQL.
5. Run `alembic upgrade head`.
6. Create the first admin user out of band or by temporarily seeding in a controlled way. Default seed users are skipped when `ENVIRONMENT=production`.
7. Build the frontend with production `VITE_API_BASE_URL` and `VITE_WS_URL`.
8. Serve the SPA behind TLS. Keep the API behind TLS as well.
9. Do not run `python -m app.db.seed_demo` in production.

Docker Compose is intended for local/dev. For cloud deployment, run the backend (uvicorn or gunicorn+uvicorn workers), a PostgreSQL instance, and a static host/nginx for the frontend.
