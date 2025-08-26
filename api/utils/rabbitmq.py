import json
import os
from typing import Any, Dict, Callable, Optional
import base64
import hmac
import hashlib

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


def publish_exchange(exchange: str, routing_key: str, message: Dict[str, Any]) -> bool:
    """Publish a JSON message to a specific exchange with routing key.
    Returns True if published, False if not configured/unavailable.
    """
    if pika is None:
        return False
    params = _get_connection_params()
    if params is None:
        return False
    try:
        connection = pika.BlockingConnection(params)
        channel = connection.channel()
        # Ensure topic exchange exists (idempotent)
        channel.exchange_declare(exchange=exchange, exchange_type="topic", durable=True)
        body = json.dumps(message).encode("utf-8")
        channel.basic_publish(
            exchange=exchange,
            routing_key=routing_key,
            body=body,
            properties=pika.BasicProperties(content_type="application/json", delivery_mode=2),
        )
        connection.close()
        return True
    except Exception:
        return False


def publish_exchange_profiled(exchange: str, routing_key: str, message: Dict[str, Any], profile: str = "default") -> bool:
    """Publish with QoS/security profile.
    Profiles configured via env:
      COORD_MSG_SIGN_KEY: HMAC-SHA256 signing key (optional)
      COORD_MSG_PRIORITY_<PROFILE>: integer 0-9
    """
    if pika is None:
        return False
    params = _get_connection_params()
    if params is None:
        return False
    try:
        connection = pika.BlockingConnection(params)
        channel = connection.channel()
        channel.exchange_declare(exchange=exchange, exchange_type="topic", durable=True)
        body = json.dumps(message).encode("utf-8")
        # Optional signing
        headers = {}
        sign_key = os.getenv("COORD_MSG_SIGN_KEY")
        if sign_key:
            sig = hmac.new(sign_key.encode("utf-8"), body, hashlib.sha256).digest()
            headers["sig"] = base64.b64encode(sig).decode("ascii")
            headers["sig_alg"] = "HMAC-SHA256"
        # Optional priority
        try:
            prio = int(os.getenv(f"COORD_MSG_PRIORITY_{profile.upper()}", "0"))
        except Exception:
            prio = 0
        props = pika.BasicProperties(
            content_type="application/json",
            delivery_mode=2,
            headers=headers or None,
            priority=prio if prio else None,
        )
        channel.basic_publish(exchange=exchange, routing_key=routing_key, body=body, properties=props)
        connection.close()
        return True
    except Exception:
        return False


def ensure_coordination_bindings() -> bool:
    """Declare coordination exchange, queues, and bindings with priorities and DLQs.
    Queues:
      coord.events (bindings: agent.register, agent.heartbeat, task.allocated, rebalance.plan, conflict.resolved, consensus.decision, knowledge.shared)
      coord.msg (bindings: msg.#)
    """
    if pika is None:
        return False
    params = _get_connection_params()
    if params is None:
        return False
    try:
        connection = pika.BlockingConnection(params)
        channel = connection.channel()
        # Exchanges
        channel.exchange_declare(exchange="coordination", exchange_type="topic", durable=True)
        channel.exchange_declare(exchange="coordination.dlx", exchange_type="topic", durable=True)
        # Queues with DLQ and priority support
        args_common = {
            "x-dead-letter-exchange": "coordination.dlx",
            "x-max-priority": 10,
        }
        channel.queue_declare(queue="coord.events", durable=True, arguments=args_common)
        channel.queue_declare(queue="coord.msg", durable=True, arguments=args_common)
        # Bindings
        keys = [
            "agent.register", "agent.heartbeat", "task.allocated", "rebalance.plan",
            "conflict.resolved", "consensus.decision", "knowledge.shared",
        ]
        for k in keys:
            channel.queue_bind(queue="coord.events", exchange="coordination", routing_key=k)
        channel.queue_bind(queue="coord.msg", exchange="coordination", routing_key="msg.#")
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
