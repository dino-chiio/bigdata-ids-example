from kafka import KafkaProducer
import time
import json

producer = KafkaProducer(
    bootstrap_servers='kafka:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

topic = 'test-topic'

for i in range(10):
    data = {'id': i, 'value': f'sample-{i}'}
    producer.send(topic, value=data)
    print(f"Sent: {data}")
    time.sleep(1)

producer.flush()
producer.close()
