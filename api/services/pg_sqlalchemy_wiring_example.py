"""
Example SQLAlchemy wiring for KnowledgeSyncService.

This is an example module and is NOT imported by the app by default.
Wire your real models or adapt as needed.
"""
from __future__ import annotations

from typing import Any, Dict, Iterable, Optional
from dataclasses import asdict, dataclass
from datetime import datetime, timezone

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, String, Integer, JSON, DateTime
from sqlalchemy.orm import declarative_base

# Example local declarative base for demonstration only.
# In your app, use the shared Base from your model layer if available.
Base = declarative_base()


class KnowledgeItem(Base):
    __tablename__ = "knowledge_items"

    id = Column(String, primary_key=True)
    content = Column(String, nullable=False)
    entity_type = Column(String, nullable=False, default="generic")
    version = Column(Integer, nullable=False, default=1)
    metadata = Column(JSON, nullable=True)
    embedding = Column(JSON, nullable=True)  # store as list[float]
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


# -----------------------------
# Factory functions to wire with KnowledgeSyncService
# -----------------------------

def make_list_pg_entities(db: SQLAlchemy):
    def _list() -> Iterable[Dict[str, Any]]:
        for row in db.session.query(KnowledgeItem).limit(1000).all():
            yield {
                "id": row.id,
                "content": row.content,
                "entity_type": row.entity_type,
                "version": row.version,
                "metadata": row.metadata or {},
                "embedding": row.embedding,
                "created_by": "pg",  # example
                "updated_by": "pg",  # example
            }
    return _list


def make_get_pg_entity(db: SQLAlchemy):
    def _get(entity_id: str) -> Optional[Dict[str, Any]]:
        row = db.session.get(KnowledgeItem, entity_id)
        if not row:
            return None
        return {
            "id": row.id,
            "content": row.content,
            "entity_type": row.entity_type,
            "version": row.version,
            "metadata": row.metadata or {},
            "embedding": row.embedding,
        }
    return _get


def make_upsert_pg_entity(db: SQLAlchemy):
    def _upsert(payload: Dict[str, Any]) -> None:
        entity_id = str(payload.get("id"))
        row = db.session.get(KnowledgeItem, entity_id)
        if not row:
            row = KnowledgeItem(
                id=entity_id,
                content=str(payload.get("content", "")),
                entity_type=str(payload.get("entity_type", "generic")),
                version=int(payload.get("version", 1)),
                metadata=payload.get("metadata") or {},
                embedding=payload.get("embedding"),
            )
            db.session.add(row)
        else:
            row.content = str(payload.get("content", row.content))
            row.entity_type = str(payload.get("entity_type", row.entity_type))
            row.version = int(payload.get("version", row.version))
            row.metadata = payload.get("metadata") or row.metadata
            row.embedding = payload.get("embedding", row.embedding)
        db.session.commit()
    return _upsert


# Example usage (not executed automatically):
# from ..services.knowledge_sync import KnowledgeSyncService
# from ..extensions import db
# ecs = EnhancedConsciousnessSubstrate(uri, user, password)
# svc = KnowledgeSyncService(
#     ecs,
#     list_pg_entities=make_list_pg_entities(db),
#     get_pg_entity=make_get_pg_entity(db),
#     upsert_pg_entity=make_upsert_pg_entity(db),
# )
# svc.sync_pg_to_neo4j(transform_to_updates=lambda row: (row["id"], row))
# svc.sync_neo4j_to_pg(
#     list_neo4j_entities=lambda: [],  # implement query from Neo4j
#     transform_to_pg=lambda node: node,
# )
