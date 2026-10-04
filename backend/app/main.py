from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging

configure_logging()
settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description="Manual machine stoppage collection, analytics, and reporting.",
    version="1.0.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    redoc_url="/api/redoc",
)

origins = settings.cors_origin_list
if settings.is_production and "*" in origins:
    origins = [item for item in origins if item != "*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)
app.include_router(api_router, prefix="/api")
app.logger = __import__("logging").getLogger("pdms")


@app.get("/api/health")
async def health():
    return {"status": "ok", "app": settings.app_name, "environment": settings.environment}
