import tempfile
import threading
from confluent_kafka import Producer
import json
from confluent_kafka import Producer
from core import settings
from base64 import b64decode


# Write certs to temp files
def write_temp_file(b64_content):
    tmp = tempfile.NamedTemporaryFile(delete=False)
    tmp.write(b64decode(b64_content))
    tmp.flush()
    return tmp.name


ca_path = write_temp_file(settings.KAFKA_CA_PEM)
cert_path = write_temp_file(settings.KAFKA_SERVICE_CERT)
key_path = write_temp_file(settings.KAFKA_SERVICE_KEY)

producer = Producer(
    {
        "bootstrap.servers": settings.KAFKA_URL,
        "security.protocol": "SSL",
        "ssl.ca.location": ca_path,
        "ssl.certificate.location": cert_path,
        "ssl.key.location": key_path,
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
