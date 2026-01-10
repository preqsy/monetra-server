import tempfile
import threading
import logging
from confluent_kafka import Producer
import json
from confluent_kafka import Producer
from core import settings
from base64 import b64decode


logger = logging.getLogger(__name__)


# Write certs to temp files
def write_temp_file(b64_content):
    tmp = tempfile.NamedTemporaryFile(delete=False)
    tmp.write(b64decode(b64_content))
    tmp.flush()
    return tmp.name


ca_path = write_temp_file(settings.KAFKA_CONFIG.KAFKA_CA_PEM)
cert_path = write_temp_file(settings.KAFKA_CONFIG.KAFKA_SERVICE_CERT)
key_path = write_temp_file(settings.KAFKA_CONFIG.KAFKA_SERVICE_KEY)

kafka_config = {
    "bootstrap.servers": "localhost:9092",
    "acks": "all",
}

if settings.ENVIRONMENT == "prod":
    kafka_config["bootstrap.servers"] = settings.KAFKA_CONFIG.KAFKA_URL
    kafka_config["security.protocol"] = "SSL"
    kafka_config["ssl.ca.location"] = ca_path
    kafka_config["ssl.certificate.location"] = cert_path
    kafka_config["ssl.key.location"] = key_path

producer = Producer(kafka_config)


def publish(topic: str, event: dict):
    print(f"Publishing message...")
    try:
        producer.produce(
            topic=topic,
            key=str(event["user_id"]).encode(),
            value=json.dumps(event).encode(),
        )
        logger.debug(f"Successfully published message: {event}")
    except Exception as e:
        print(f"*****Error: {str(e)}")
        logger.error(f"Failed to publish message: {str(e)}")
        raise


def poll_loop():
    while True:
        producer.poll(0.1)


threading.Thread(target=poll_loop, daemon=True).start()
