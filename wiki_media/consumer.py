import os
import time
from json import loads

from kafka import KafkaConsumer

from wiki_media.common import constants

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
