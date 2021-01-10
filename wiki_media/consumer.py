import asyncio
import os
import time
from json import loads

from aiosseclient import aiosseclient
from fire import Fire
from kafka import KafkaConsumer

from wiki_media.common import constants


def kafka_client():
    kafka_url = os.environ.get("KAFKA_URL", constants.KAFKA_URL)
    consumer = KafkaConsumer(
        bootstrap_servers=[kafka_url],
        auto_offset_reset="latest",  # "'earliest',
        enable_auto_commit=True,
        value_deserializer=lambda x: loads(x.decode("utf-8"))
    )

    consumer.subscribe([constants.USER_CHANNEL])
    for event in consumer:
        event_data = event.value
        print(event_data)
        time.sleep(1)


async def _fastapi_client():
    async for event in aiosseclient("http://localhost:8000/stream/user", timeout=None):
        print(f"Event: {event.event}")
        print(f"Data: {event.data}")


def fastapi_client():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(_fastapi_client())


def main(client: str):
    if client == "kafka":
        kafka_client()
    elif client == "fastapi":
        fastapi_client()
    else:
        raise ValueError("kokoko")


if __name__ == '__main__':
    Fire(main)
