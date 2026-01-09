# Python quick test
from confluent_kafka import Producer, Consumer
import json

# produce
p = Producer({"bootstrap.servers": "localhost:9092"})
p.produce("transaction.created.dev", key="1", value=json.dumps({"amount": 10}))
p.flush()

# consume
c = Consumer(
    {
        "bootstrap.servers": "localhost:9092",
        "group.id": "test",
        "auto.offset.reset": "earliest",
    }
)
c.subscribe(["transaction.created.dev"])
msg = c.poll(5.0)
print(json.loads(msg.value()))  # should print {"amount": 10}
