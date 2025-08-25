import os
import json
import time

try:
    import pika  # type: ignore
except Exception as e:
    raise SystemExit("pika is required: pip install pika")

QUEUE = os.getenv("AGENT_UPDATES_QUEUE", "agent_updates")
RABBIT_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")


def main():
    params = pika.URLParameters(RABBIT_URL)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE, durable=True)

    cid = os.getenv("TEST_CONVERSATION_ID", "demo-conv")
    payload = {
        "conversation_id": cid,
        "event": "agent:update",
        "status": "running",
        "agent_id": "agent-demo",
        "data": {"progress": 0.1, "ts": int(time.time())},
    }

    body = json.dumps(payload).encode("utf-8")
    channel.basic_publish(
        exchange="",
        routing_key=QUEUE,
        body=body,
        properties=pika.BasicProperties(content_type="application/json", delivery_mode=2),
    )
    print(f"Published to {QUEUE}: {payload}")
    connection.close()


if __name__ == "__main__":
    main()
