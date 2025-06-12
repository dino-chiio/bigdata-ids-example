import json
from nfstream import NFStreamer
from kafka import KafkaProducer

# Configure interface and Kafka topic
INTERFACE = "eth0"  # Change if needed
KAFKA_BROKER = "kafka:9092"
KAFKA_TOPIC = "network-flows"

# Set up Kafka producer
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

# Start NFStreamer
streamer = NFStreamer(source=INTERFACE, decode_tunnels=True, bpf_filter=None)

for flow in streamer:
    # Convert flow to dict and send to Kafka
    producer.send(KAFKA_TOPIC, flow.to_dict())
    producer.flush()
