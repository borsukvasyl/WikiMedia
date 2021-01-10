import asyncio
import os
import time
from json import dumps

from aiosseclient import aiosseclient
from kafka import KafkaProducer

from wiki_media.common import constants
from wiki_media.common.logger import create_logger

logger = create_logger(__name__)


class WikiMediaProducer:
    def __init__(self, kafka_url: str):
        self.producer = KafkaProducer(
            bootstrap_servers=[kafka_url],
            value_serializer=lambda x: dumps(x).encode('utf-8')
        )

    def run(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.main())

    async def main(self):
        async for event in aiosseclient(constants.WIKI_URL):
            if event.event == "message":
                logger.info("Posted raw message")
                self.producer.send(constants.RAW_CHANNEL, value=event.data)
            time.sleep(5)


if __name__ == '__main__':
    kafka_url = os.environ.get("KAFKA_URL", constants.KAFKA_URL)
    producer = WikiMediaProducer(kafka_url)
    producer.run()
