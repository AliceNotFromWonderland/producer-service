"""
Minimal outbox relay (dispatcher).

если чо это тут сейчас лишь для галочки, даже не заглушка, просто чтоб обозначить 
что здесь будет вся эта реализация аутбокса когда с брокером разберусь

It polls `outbox_event` for rows with `processed_at IS NULL`, "dispatches"
each one, and marks it processed. Kafka is not wired up at this stage of
the project (per current scope: plain CRUD service, no broker yet) — the
`_dispatch` function below is a stub. When Kafka work actually starts,
replace its body with a real producer call
(aiokafka / confluent-kafka), e.g.:

    await producer.send_and_wait(
        "material-movements", json.dumps(event.payload).encode()
    )


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
    """Stub: log instead of publishing to Kafka. Replace once a broker exists."""
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
