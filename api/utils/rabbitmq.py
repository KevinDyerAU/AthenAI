import json
import os
from typing import Any, Dict

try:
    import pika  # type: ignore
except Exception:  # pragma: no cover
    pika = None


def _get_connection_params():
    url = os.getenv("RABBITMQ_URL")
    if not url:
        host = os.getenv("RABBITMQ_HOST", "localhost")
        port = int(os.getenv("RABBITMQ_PORT", "5672"))
        user = os.getenv("RABBITMQ_USER", "guest")
        password = os.getenv("RABBITMQ_PASSWORD", "guest")
        credentials = pika.PlainCredentials(user, password) if pika else None
        return pika.ConnectionParameters(host=host, port=port, credentials=credentials) if pika else None
    return pika.URLParameters(url) if pika else None


def publish_task(task: Dict[str, Any], routing_key: str = "tasks") -> bool:
    """Publish a task message to RabbitMQ. Returns True if published, False if not configured.
    If pika is not installed or RabbitMQ is unavailable, it fails gracefully.
    """
    if pika is None:
        return False
    params = _get_connection_params()
    if params is None:
        return False
    try:
        connection = pika.BlockingConnection(params)
        channel = connection.channel()
        channel.queue_declare(queue=routing_key, durable=True)
        body = json.dumps(task).encode("utf-8")
        channel.basic_publish(
            exchange="",
            routing_key=routing_key,
            body=body,
            properties=pika.BasicProperties(content_type="application/json", delivery_mode=2),
        )
        connection.close()
        return True
    except Exception:
        return False
