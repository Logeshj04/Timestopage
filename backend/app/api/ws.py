import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user_ws
from app.db.session import SessionLocal
from app.websocket.manager import manager

router = APIRouter(tags=["Realtime"])
logger = logging.getLogger(__name__)


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    async with SessionLocal() as db:
        user = await get_current_user_ws(websocket, db)
    if user is None:
        await websocket.close(code=4401)
        return
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:
        logger.exception("WebSocket error")
        manager.disconnect(websocket)
