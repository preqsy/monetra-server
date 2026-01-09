import threading
from confluent_kafka import Producer
import json

producer = Producer(
    {
        "bootstrap.servers": "localhost:9092",
        "acks": "all",
    }
)


def publish(topic: str, event: dict):
    producer.produce(
        topic=topic,
        key=str(event["user_id"]).encode(),
        value=json.dumps(event).encode(),
    )


def poll_loop():
    while True:
        producer.poll(0.1)


threading.Thread(target=poll_loop, daemon=True).start()
