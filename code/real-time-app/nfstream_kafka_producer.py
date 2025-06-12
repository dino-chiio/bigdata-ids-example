import json
import logging
from nfstream import NFStreamer
from kafka import KafkaProducer
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

pcap_path = "../data/network-traffic.pcap"  # Change this to your .pcap file path

# Configure interface and Kafka topic
INTERFACE = "eth0"  # Change if needed
KAFKA_BROKER = "kafka:9092"
KAFKA_TOPIC = "network-flows"

# Set up Kafka producer
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

logging.info(f"Starting NFStreamer on interface: {INTERFACE}")
streamer = NFStreamer(source=pcap_path, decode_tunnels=True, statistical_analysis=True, bpf_filter=None)

logging.info(f"Producing flows to Kafka broker: {KAFKA_BROKER}, topic: {KAFKA_TOPIC}")

fields = [
    "protocol",
    "src2dst_packets",
    "dst2src_packets",
    "src2dst_bytes",
    "dst2src_bytes",
    "bidirectional_duration_ms",
    "bidirectional_min_ps",
    "bidirectional_max_ps",
    "bidirectional_mean_ps",
    "bidirectional_stddev_ps",
    "src2dst_max_ps",
    "src2dst_min_ps",
    "src2dst_mean_ps",
    "src2dst_stddev_ps",
    "dst2src_max_ps",
    "dst2src_min_ps",
    "dst2src_mean_ps",
    "dst2src_stddev_ps",
    "bidirectional_mean_piat_ms",
    "bidirectional_stddev_piat_ms",
    "bidirectional_max_piat_ms",
    "bidirectional_min_piat_ms",
    "src2dst_mean_piat_ms",
    "src2dst_stddev_piat_ms",
    "src2dst_max_piat_ms",
    "src2dst_min_piat_ms",
    "dst2src_mean_piat_ms",
    "dst2src_stddev_piat_ms",
    "dst2src_max_piat_ms",
    "dst2src_min_piat_ms",
    "bidirectional_fin_packets",
    "bidirectional_syn_packets",
    "bidirectional_rst_packets",
    "bidirectional_psh_packets",
    "bidirectional_ack_packets",
    "bidirectional_urg_packets",
    "bidirectional_cwr_packets",
    "bidirectional_ece_packets",
    "src2dst_psh_packets",
    "dst2src_psh_packets",
    "src2dst_urg_packets",
    "dst2src_urg_packets",
]

for flow in streamer:
    flow_dict = {col: getattr(flow, col, None) for col in fields}
    producer.send(KAFKA_TOPIC, flow_dict)
    logging.info(f"Sent filtered flow: {flow_dict}")
    time.sleep(2)  # Adjust sleep time as needed to control flow rate

producer.flush()
producer.close()