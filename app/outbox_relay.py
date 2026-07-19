"""
Minimal outbox relay (dispatcher).

"""
import asyncio
import logging
from datetime import datetime, timezone

from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models import OutboxEvent

logger = logging.getLogger("outbox_relay")

POLL_INTERVAL_SECONDS = 5
BATCH_SIZE = 100


async def _dispatch(event: OutboxEvent) -> None:
    logger.info(
        "Would publish to Kafka (stub): aggregate=%s/%s event_type=%s payload=%s",
        event.aggregate_type,
        event.aggregate_id,
        event.event_type,
        event.payload,
    )


async def process_batch() -> int:
    async with AsyncSessionLocal() as db:
        stmt = (
            select(OutboxEvent)
            .where(OutboxEvent.processed_at.is_(None))
            .order_by(OutboxEvent.id)
            .limit(BATCH_SIZE)
        )
        events = (await db.execute(stmt)).scalars().all()

        for event in events:
            await _dispatch(event)
            event.processed_at = datetime.now(timezone.utc)

        await db.commit()
        return len(events)


async def run_forever() -> None:
    logging.basicConfig(level=logging.INFO)
    logger.info("Outbox relay started (stub — not connected to Kafka yet).")
    while True:
        processed = await process_batch()
        if processed:
            logger.info("Processed %d outbox event(s).", processed)
        await asyncio.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    asyncio.run(run_forever())
