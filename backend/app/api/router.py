from fastapi import APIRouter

from app.api.auth import router as auth_router
from app.api.dashboard import router as dashboard_router
from app.api.master import router as master_router
from app.api.stoppages import router as stoppage_router
from app.api.users import router as users_router
from app.api.ws import router as ws_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(master_router)
api_router.include_router(stoppage_router)
api_router.include_router(dashboard_router)
api_router.include_router(ws_router)
