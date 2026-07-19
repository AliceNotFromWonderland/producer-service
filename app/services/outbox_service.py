from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import OutboxEvent


async def enqueue_event(
    db: AsyncSession,
    aggregate_type: str,
    aggregate_id: int,
    event_type: str,
    payload: dict[str, Any],
) -> OutboxEvent:
    event = OutboxEvent(
        aggregate_type=aggregate_type,
        aggregate_id=aggregate_id,
        event_type=event_type,
        payload=payload,
    )
    db.add(event)
    return event
