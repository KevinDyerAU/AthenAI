"""E2E publisher for Unstructured worker

- Copies a fixture PDF into ./data/unstructured/input/
- Publishes a message to RabbitMQ to process the document

Usage:
  python tests/e2e/unstructured_publish.py --rabbitmq amqp://user:pass@localhost:5672/ \
      --doc-id doc-n8n-guide

If --rabbitmq is omitted, uses RABBITMQ_URL env or amqp://guest:guest@localhost:5672/
"""
from __future__ import annotations
import argparse
import os
import shutil
import sys
import uuid
from pathlib import Path
import json

import pika

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = REPO_ROOT / "data" / "unstructured"
INPUT_DIR = DATA_DIR / "input"
SOURCE_PDF = REPO_ROOT / "documentation" / "planning" / "The Ultimate n8n Guide.pdf"

DEFAULT_QUEUE = os.getenv("UNSTRUCTURED_QUEUE", "documents.process")
DEFAULT_RABBIT = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")


def ensure_input_pdf(target_name: str | None = None) -> Path:
    INPUT_DIR.mkdir(parents=True, exist_ok=True)
    if not SOURCE_PDF.exists():
        raise FileNotFoundError(f"Fixture PDF not found: {SOURCE_PDF}")
    dest = INPUT_DIR / (target_name or SOURCE_PDF.name)
    shutil.copy2(SOURCE_PDF, dest)
    return dest


def publish_message(rabbit_url: str, queue: str, doc_id: str, file_path_inside_container: str):
    params = pika.URLParameters(rabbit_url)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    channel.queue_declare(queue=queue, durable=True)
    payload = {
        "doc_id": doc_id,
        "file_path": file_path_inside_container,
        "content_type": "pdf",
        "metadata": {
            "source": "e2e-test",
            "title": "The Ultimate n8n Guide"
        }
    }
    body = json.dumps(payload).encode("utf-8")
    channel.basic_publish(
        exchange="",
        routing_key=queue,
        body=body,
        properties=pika.BasicProperties(content_type="application/json", delivery_mode=2),
    )
    connection.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rabbitmq", default=DEFAULT_RABBIT)
    parser.add_argument("--queue", default=DEFAULT_QUEUE)
    parser.add_argument("--doc-id", default=f"doc-{uuid.uuid4().hex[:8]}")
    parser.add_argument("--target-name", default=None, help="Optional filename for copied PDF")
    args = parser.parse_args()

    copied = ensure_input_pdf(args.target_name)
    # Worker container sees this path via compose volume mapping ./data/unstructured -> /app/data
    file_path_inside_container = f"/app/data/input/{copied.name}"

    print(f"Copied fixture to: {copied}")
    print(f"Publishing to queue '{args.queue}' with doc_id '{args.doc_id}' and file_path '{file_path_inside_container}'")
    publish_message(args.rabbitmq, args.queue, args.doc_id, file_path_inside_container)
    print("Message published. Check worker logs and metrics.")


if __name__ == "__main__":
    sys.exit(main())
