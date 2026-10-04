from datetime import datetime, timezone
from uuid import UUID

from app.websocket.manager import manager


async def publish_stoppage_event(event_type: str, stoppage_id: UUID) -> None:
    await manager.broadcast(
        {
            "type": event_type,
            "stoppage_id": str(stoppage_id),
            "at": datetime.now(timezone.utc).isoformat(),
        }
    )
