"""Unstructured Worker: Health/Metrics + RabbitMQ consumer + Neo4j writes

Consumes messages from RabbitMQ with payloads:
{
  "doc_id": "<string>",
  "file_path": "<path inside container>",
  "content_type": "pdf|text",
  "metadata": { ... }
}

Creates `KnowledgeEntity` nodes for document and its chunks in Neo4j.
"""

import json
import os
import threading
import time
from typing import List

import psutil
import pika
from flask import Flask, jsonify
from flask_cors import CORS
from neo4j import GraphDatabase
from prometheus_client import (
    CollectorRegistry,
    CONTENT_TYPE_LATEST,
    Counter,
    Histogram,
    Gauge,
    generate_latest,
    multiprocess,
)
from unstructured.partition.auto import partition

APP_PORT = int(os.getenv("HEALTH_CHECK_PORT", os.getenv("PROMETHEUS_PORT", 8080)))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
QUEUE_NAME = os.getenv("UNSTRUCTURED_QUEUE", "documents.process")
RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

app = Flask(__name__)
CORS(app)

registry = CollectorRegistry()
if os.getenv("PROMETHEUS_MULTIPROC_DIR"):
    multiprocess.MultiProcessCollector(registry)

health_gauge = Gauge("unstructured_worker_health", "Health status (1=ok,0=down)", registry=registry)
cpu_gauge = Gauge("unstructured_worker_cpu_percent", "CPU usage percent", registry=registry)
mem_gauge = Gauge("unstructured_worker_mem_percent", "Memory usage percent", registry=registry)
requests_counter = Counter("unstructured_worker_requests_total", "Total HTTP requests", registry=registry)
processed_docs = Counter("unstructured_worker_documents_processed_total", "Documents processed", registry=registry)
processed_chunks = Counter("unstructured_worker_chunks_processed_total", "Chunks processed", registry=registry)
processing_errors = Counter("unstructured_worker_processing_errors_total", "Processing errors", registry=registry)
docs_total = Counter("documents_processed_total", "Total documents processed", ["status", "file_type"], registry=registry)
processing_hist = Histogram("document_processing_seconds", "Time spent processing a document", registry=registry)
queue_size_gauge = Gauge("queue_size", "Current queue size (messages)", registry=registry)
active_workers_gauge = Gauge("active_workers", "Active unstructured workers", registry=registry)


def neo4j_driver():
    return GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))


def upsert_document_and_chunks(doc_id: str, content: str, chunks: List[str], metadata: dict):
    """Create/Update KnowledgeEntity for document and chunk nodes, relate via HAS_PART."""
    query = """
    MERGE (d:KnowledgeEntity {id:$doc_id})
    ON CREATE SET d.entity_type='document', d.created_at=datetime(), d.version=1, d.metadata=$metadata
    ON MATCH SET d.updated_at=datetime(), d.metadata=$metadata
    SET d.content=$content
    WITH d
    UNWIND range(0, size($chunks)-1) AS idx
    MERGE (c:KnowledgeEntity {id: d.id + ':' + toString(idx)})
    ON CREATE SET c.entity_type='chunk', c.created_at=datetime(), c.version=1
    SET c.content = $chunks[idx], c.updated_at=datetime()
    MERGE (d)-[:HAS_PART]->(c)
    RETURN d.id as document_id, size($chunks) as chunk_count
    """
    with neo4j_driver() as driver:
        with driver.session() as session:
            session.run(query, doc_id=doc_id, content=content, chunks=chunks, metadata=metadata or {})


def process_file(doc_id: str, file_path: str, content_type: str | None, metadata: dict | None):
    start = time.perf_counter()
    file_type = (content_type or os.path.splitext(file_path)[1].lstrip(".") or "unknown").lower()
    try:
        elements = partition(filename=file_path)
        texts = [e.text for e in elements if getattr(e, "text", None)]
        full_text = "\n\n".join(texts)
        upsert_document_and_chunks(doc_id, full_text, texts, metadata or {})
        processed_docs.inc()
        processed_chunks.inc(len(texts))
        docs_total.labels(status="success", file_type=file_type).inc()
    except Exception:
        processing_errors.inc()
        docs_total.labels(status="error", file_type=file_type).inc()
        raise
    finally:
        processing_hist.observe(time.perf_counter() - start)


def consumer_loop():
    while True:
        try:
            params = pika.URLParameters(RABBITMQ_URL)
            connection = pika.BlockingConnection(params)
            channel = connection.channel()
            channel.queue_declare(queue=QUEUE_NAME, durable=True)

            def on_message(ch, method, properties, body):
                try:
                    msg = json.loads(body.decode("utf-8"))
                    doc_id = msg.get("doc_id") or msg.get("id")
                    file_path = msg.get("file_path")
                    content_type = msg.get("content_type")
                    metadata = msg.get("metadata", {})
                    if not doc_id or not file_path:
                        raise ValueError("Missing doc_id or file_path in message")
                    process_file(doc_id, file_path, content_type, metadata)
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                except Exception as e:
                    processing_errors.inc()
                    # Nack with requeue=false to avoid poison messages looping
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

            channel.basic_qos(prefetch_count=int(os.getenv("WORKER_CONCURRENCY", 2)))
            channel.basic_consume(queue=QUEUE_NAME, on_message_callback=on_message)
            channel.start_consuming()
        except Exception:
            # Sleep and retry connection to RabbitMQ
            time.sleep(5)
            continue


def queue_metrics_loop():
    """Periodically fetch queue size and set gauges."""
    active_workers_gauge.set(1)
    while True:
        try:
            params = pika.URLParameters(RABBITMQ_URL)
            connection = pika.BlockingConnection(params)
            channel = connection.channel()
            res = channel.queue_declare(queue=QUEUE_NAME, durable=True, passive=True)
            queue_size_gauge.set(getattr(res.method, "message_count", 0))
            connection.close()
        except Exception:
            # set to -1 to indicate error fetching metrics
            queue_size_gauge.set(-1)
        time.sleep(10)


@app.route("/health", methods=["GET"])  # simple health
def health():
    requests_counter.inc()
    try:
        cpu = psutil.cpu_percent(interval=0.0)
        mem = psutil.virtual_memory().percent
        cpu_gauge.set(cpu)
        mem_gauge.set(mem)
        health_gauge.set(1)
        return jsonify({
            "status": "ok",
            "worker_type": os.getenv("WORKER_TYPE", "unstructured"),
            "concurrency": int(os.getenv("WORKER_CONCURRENCY", 1)),
            "cpu_percent": cpu,
            "mem_percent": mem,
            "queue": QUEUE_NAME
        }), 200
    except Exception as e:
        health_gauge.set(0)
        return jsonify({"status": "error", "detail": str(e)}), 500


@app.route("/metrics")
def metrics():
    requests_counter.inc()
    data = generate_latest(registry)
    return app.response_class(data, mimetype=CONTENT_TYPE_LATEST)


if __name__ == "__main__":
    # Start consumer in background thread
    t = threading.Thread(target=consumer_loop, daemon=True)
    t.start()
    # Start queue metrics updater
    tm = threading.Thread(target=queue_metrics_loop, daemon=True)
    tm.start()
    # Run health/metrics server
    app.run(host="0.0.0.0", port=APP_PORT)
