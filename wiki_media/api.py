import asyncio
import os

import uvicorn
from fastapi import FastAPI, APIRouter, Request
from sse_starlette.sse import EventSourceResponse

from wiki_media.common import constants
from wiki_media.common.logger import create_logger

logger = create_logger(__name__)
router = APIRouter()
kafka_url = os.environ.get("KAFKA_URL", constants.KAFKA_URL)

status_stream_delay = 5  # second
status_stream_retry_timeout = 30000  # milisecond


async def status_event_generator(request: Request, user_id: str):
    previous_status = None
    counter = 0
    while True:
        if await request.is_disconnected():
            logger.debug('Request disconnected')
            break

        if previous_status and False:
            logger.debug('Request completed. Disconnecting now')
            yield {
                "event": "end",
                "data": ""
            }
            break

        current_status = f"{user_id}---{counter}"
        if previous_status != current_status:
            yield {
                "event": "update",
                "retry": status_stream_retry_timeout,
                "data": current_status
            }
            previous_status = current_status
            logger.debug('Current status :%s', current_status)
        else:
            logger.debug('No change in status...')

        await asyncio.sleep(status_stream_delay)
        counter += 1


@router.get("/user")
async def get(user_id: str, request: Request):
    event_generator = status_event_generator(request, user_id)
    return EventSourceResponse(event_generator)


if __name__ == "__main__":
    app = FastAPI()
    app.include_router(router)
    uvicorn.run(app, host="0.0.0.0")
