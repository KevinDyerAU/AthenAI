import os
import json

try:
    import pika  # type: ignore
except Exception as e:
    raise SystemExit("pika is required: pip install pika")

QUEUE = os.getenv("AGENT_UPDATES_QUEUE", "agent_updates")
RABBIT_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")


def on_message(ch, method, properties, body):
    try:
        payload = json.loads(body.decode("utf-8"))
    except Exception:
        payload = {"raw": body.decode("utf-8", errors="ignore")}
    print("[x] Received:", payload)
    ch.basic_ack(delivery_tag=method.delivery_tag)


def main():
    params = pika.URLParameters(RABBIT_URL)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE, durable=True)
    channel.basic_qos(prefetch_count=10)
    channel.basic_consume(queue=QUEUE, on_message_callback=on_message, auto_ack=False)
    print(f"[*] Waiting for messages on {QUEUE}. Press CTRL+C to exit.")
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()
    finally:
        connection.close()


if __name__ == "__main__":
    main()
