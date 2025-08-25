import json
import os
from typing import Any, Dict, Callable, Optional

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


def start_consumer(queue: str, on_message: Callable[[dict], None], prefetch: int = 10) -> Optional[Callable[[], None]]:
    """Start a simple blocking consumer in the calling thread.
    Returns a stop function when started successfully, else None.
    The caller should run this in a background thread/greenlet.
    """
    if pika is None:
        return None
    params = _get_connection_params()
    if params is None:
        return None

    connection = None
    channel = None
    try:
        connection = pika.BlockingConnection(params)
        channel = connection.channel()
        channel.queue_declare(queue=queue, durable=True)
        channel.basic_qos(prefetch_count=prefetch)

        def _callback(ch, method, properties, body):  # type: ignore
            try:
                payload = json.loads(body.decode("utf-8")) if body else {}
                on_message(payload)
                ch.basic_ack(delivery_tag=method.delivery_tag)
            except Exception:
                # Nack and requeue for later processing
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

        channel.basic_consume(queue=queue, on_message_callback=_callback, auto_ack=False)

        def _stop():
            try:
                if channel and channel.is_open:
                    channel.stop_consuming()
            finally:
                try:
                    if connection and connection.is_open:
                        connection.close()
                except Exception:
                    pass

        # Start consuming in this thread/greenlet; the caller should run it in background
        channel.start_consuming()
        return _stop
    except Exception:
        # Ensure clean close on failure
        try:
            if connection and connection.is_open:
                connection.close()
        except Exception:
            pass
        return None
