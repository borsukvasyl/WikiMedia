import time
from json import dumps

from kafka import KafkaProducer


producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda x: dumps(x).encode('utf-8')
)

for j in range(10):
    print("Iteration", j)
    data = {'counter': j}
    producer.send('counter', value=data)
    time.sleep(0.5)
