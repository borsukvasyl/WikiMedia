import time
from json import loads

from kafka import KafkaConsumer


consumer = KafkaConsumer(
    bootstrap_servers=["localhost:9092"],
    auto_offset_reset="latest",  # "'earliest',
    enable_auto_commit=True,
    value_deserializer=lambda x: loads(x.decode("utf-8"))
)

consumer.subscribe(['counter'])
for event in consumer:
    event_data = event.value
    # Do whatever you want
    print(event_data)
    time.sleep(1)
