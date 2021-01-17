import json
import os
from typing import Optional

import uvicorn
from fastapi import FastAPI, APIRouter, Request
from kafka import KafkaConsumer
from sse_starlette.sse import EventSourceResponse

from wiki_media.common import constants
from wiki_media.common.database import Database
from wiki_media.common.logger import create_logger

logger = create_logger(__name__)
router = APIRouter()
kafka_url = os.environ.get("KAFKA_URL", constants.KAFKA_URL)

status_stream_retry_timeout = 30000  # milisecond


async def kafka_stream(request: Request, user_id: Optional[str] = None):
    filter_fn = None if user_id is None else lambda k: k == user_id
    consumer = KafkaConsumer(
        bootstrap_servers=[kafka_url],
        auto_offset_reset="latest",
        enable_auto_commit=True,
        key_deserializer=lambda x: str(x.decode("utf-8")),
        value_deserializer=lambda x: json.loads(x.decode("utf-8"))
    )
    consumer.subscribe([constants.USER_CHANNEL])

    for event in consumer:
        if await request.is_disconnected():
            logger.info("Request disconnected, closing KafkaConsumer")
            consumer.close()
            break

        event_key = event.key
        event_data = event.value
        if filter_fn is None or filter_fn(event_key):
            logger.info(f"Sending {event_key} to {request.client}")
            yield {
                "event": "message",
                "retry": status_stream_retry_timeout,
                "data": event_data
            }


@router.get("/stream")
async def get(request: Request, user_id: Optional[str] = None):
    event_generator = kafka_stream(request, user_id)
    return EventSourceResponse(event_generator)


@router.get("/get/user")
async def get(user_id: str, page: int = 0):
    users = await database.get(user_id, page=page)
    return [dict(user) for user in users]


@router.get("/get/user-topics")
async def get(user_id: str, n: int = 1):
    topics = await database.get_user_topics(user_id, n)
    return topics


@router.get("/get/user-contribution")
async def get(user_id: str):
    contribution = await database.get_user_contribution(user_id)
    return contribution


@router.get("/get/top-user")
async def get(time: str):
    user = await database.get_top_user(time)
    return user


@router.get("/get/top-topic")
async def get():
    topics = await database.get_top_topics()
    return topics


app = FastAPI()
app.include_router(router)
database = Database.init()


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0")
