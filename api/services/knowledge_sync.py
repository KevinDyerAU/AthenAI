from __future__ import annotations

from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple
from datetime import datetime, timezone
import logging

from ..utils.consciousness_substrate import (
    EnhancedConsciousnessSubstrate,
    ConflictError,
)

logger = logging.getLogger(__name__)


class KnowledgeSyncService:
    """
    Bidirectional synchronization scaffold between Postgres and Neo4j.

    This service is intentionally datastore-agnostic on the Postgres side.
    Inject callables for list/get/upsert operations so we don't depend on
    a specific ORM model structure here.
    """

    def __init__(
        self,
        ecs: EnhancedConsciousnessSubstrate,
        # Postgres callables
        list_pg_entities: Callable[[], Iterable[Dict[str, Any]]],
        get_pg_entity: Callable[[str], Optional[Dict[str, Any]]],
        upsert_pg_entity: Callable[[Dict[str, Any]], None],
    ) -> None:
        self.ecs = ecs
        self.list_pg_entities = list_pg_entities
        self.get_pg_entity = get_pg_entity
        self.upsert_pg_entity = upsert_pg_entity

    # -----------------------------
    # Sync: Postgres -> Neo4j
    # -----------------------------
    def sync_pg_to_neo4j(
        self,
        transform_to_updates: Callable[[Dict[str, Any]], Tuple[str, Dict[str, Any]]],
        conflict_strategy: str = "merge",
        batch_size: int = 100,
    ) -> Dict[str, Any]:
        """
        Push PG entities into Neo4j KnowledgeEntity nodes.
        transform_to_updates maps a PG row -> (entity_id, updates).
        """
        processed, created, updated, conflicts = 0, 0, 0, 0
        buffer: List[Dict[str, Any]] = []
        now = datetime.now(timezone.utc).isoformat()

        def _flush(buf: List[Dict[str, Any]]):
            nonlocal created, updated, conflicts
            for row in buf:
                entity_id, updates = transform_to_updates(row)
                try:
                    # check if node exists by attempting update of non-existing properties
                    # if not present, create minimal entity first
                    try:
                        self.ecs.update_knowledge_entity(
                            entity_id=entity_id,
                            updates=updates,
                            updated_by=str(row.get("updated_by") or "pg-sync"),
                            conflict_resolution=conflict_strategy,
                        )
                        updated += 1
                    except ValueError:
                        # create
                        content = str(updates.get("content", ""))
                        entity_type = str(updates.get("entity_type", "generic"))
                        embedding = updates.get("embedding")
                        metadata = updates.get("metadata", {})
                        self.ecs.create_knowledge_entity(
                            content=content,
                            entity_type=entity_type,
                            created_by=str(row.get("created_by") or "pg-sync"),
                            embedding=embedding,
                            metadata=metadata,
                        )
                        updated += 1
                except ConflictError:
                    conflicts += 1
                except Exception as e:
                    logger.warning("PG->Neo4j sync error: %s", e)

        for row in self.list_pg_entities():
            buffer.append(row)
            processed += 1
            if len(buffer) >= batch_size:
                _flush(buffer)
                buffer.clear()
        if buffer:
            _flush(buffer)

        return {
            "processed": processed,
            "created": created,
            "updated": updated,
            "conflicts": conflicts,
            "timestamp": now,
        }

    # -----------------------------
    # Sync: Neo4j -> Postgres
    # -----------------------------
    def sync_neo4j_to_pg(
        self,
        list_neo4j_entities: Callable[[], Iterable[Dict[str, Any]]],
        transform_to_pg: Callable[[Dict[str, Any]], Dict[str, Any]],
        batch_size: int = 200,
    ) -> Dict[str, Any]:
        """
        Pull KnowledgeEntity nodes (and key props) into PG via upsert.
        list_neo4j_entities should return dictionaries with id/content/entity_type/metadata/etc.
        """
        processed, upserts = 0, 0
        buffer: List[Dict[str, Any]] = []
        now = datetime.now(timezone.utc).isoformat()

        def _flush(buf: List[Dict[str, Any]]):
            nonlocal upserts
            for node in buf:
                try:
                    payload = transform_to_pg(node)
                    self.upsert_pg_entity(payload)
                    upserts += 1
                except Exception as e:
                    logger.warning("Neo4j->PG sync error: %s", e)

        for node in list_neo4j_entities():
            buffer.append(node)
            processed += 1
            if len(buffer) >= batch_size:
                _flush(buffer)
                buffer.clear()
        if buffer:
            _flush(buffer)

        return {"processed": processed, "upserts": upserts, "timestamp": now}

    # -----------------------------
    # Conflict resolution helper (DB-level)
    # -----------------------------
    def resolve_conflict(
        self,
        entity_id: str,
        pg_row: Dict[str, Any],
        neo4j_updates: Dict[str, Any],
        strategy: str = "merge",
    ) -> Dict[str, Any]:
        """Example strategy aggregation combining PG row and Neo4j updates."""
        if strategy == "pg_wins":
            return pg_row
        if strategy == "neo4j_wins":
            return neo4j_updates
        # merge default: prefer neo4j non-null, else pg
        merged: Dict[str, Any] = dict(pg_row)
        for k, v in neo4j_updates.items():
            if v is not None:
                merged[k] = v
        return merged
