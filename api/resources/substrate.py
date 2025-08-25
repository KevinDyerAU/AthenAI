from __future__ import annotations

from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required

from ..config import get_config
from ..utils.consciousness_substrate import (
    EnhancedConsciousnessSubstrate,
    ConflictError,
)

ns = Namespace("substrate", description="Enhanced consciousness substrate operations")

# Models
create_entity_model = ns.model(
    "CreateEntity",
    {
        "content": fields.String(required=True),
        "entity_type": fields.String(required=True),
        "created_by": fields.String(required=True),
        "embedding": fields.List(fields.Float, required=False),
        "metadata": fields.Raw(required=False),
    },
)

update_entity_model = ns.model(
    "UpdateEntity",
    {
        "updates": fields.Raw(required=True, description="Properties to set on KnowledgeEntity"),
        "updated_by": fields.String(required=True),
        "strategy": fields.String(default="merge", description="merge|latest_wins|first_wins|strict"),
    },
)

semantic_search_model = ns.model(
    "SemanticSearch",
    {
        "embedding": fields.List(fields.Float, required=True),
        "limit": fields.Integer(default=10),
        "threshold": fields.Float(default=0.7),
    },
)

traverse_model = ns.model(
    "Traverse",
    {
        "start_id": fields.String(required=True),
        "max_depth": fields.Integer(default=2),
        "rel_types": fields.List(fields.String, required=False),
        "limit": fields.Integer(default=50),
    },
)

centrality_model = ns.model(
    "Centrality",
    {
        "top_n": fields.Integer(default=20),
        "relationship": fields.String(default="SIMILAR_TO"),
    },
)

communities_model = ns.model(
    "Communities",
    {
        "write_property": fields.String(default="communityId"),
    },
)


def _ecs() -> EnhancedConsciousnessSubstrate:
    cfg = get_config()
    return EnhancedConsciousnessSubstrate(cfg.NEO4J_URI, cfg.NEO4J_USER, cfg.NEO4J_PASSWORD)


@ns.route("/entity")
class CreateEntity(Resource):
    @jwt_required()
    @ns.expect(create_entity_model, validate=True)
    def post(self):
        payload = request.get_json() or {}
        ecs = _ecs()
        try:
            entity_id = ecs.create_knowledge_entity(
                content=str(payload.get("content", "")),
                entity_type=str(payload.get("entity_type", "generic")),
                created_by=str(payload.get("created_by")),
                embedding=payload.get("embedding"),
                metadata=payload.get("metadata") or {},
            )
            return {"id": entity_id}, 201
        finally:
            ecs.close()


@ns.route("/entity/<string:entity_id>")
class UpdateEntity(Resource):
    @jwt_required()
    @ns.expect(update_entity_model, validate=True)
    def patch(self, entity_id: str):
        payload = request.get_json() or {}
        ecs = _ecs()
        try:
            try:
                new_version = ecs.update_knowledge_entity(
                    entity_id=entity_id,
                    updates=payload.get("updates") or {},
                    updated_by=str(payload.get("updated_by")),
                    conflict_resolution=str(payload.get("strategy", "merge")),
                )
                return {"version": new_version}
            except ConflictError as ce:
                return {"error": "conflict", "details": str(ce)}, 409
        finally:
            ecs.close()


@ns.route("/search/semantic")
class SemanticSearch(Resource):
    @jwt_required()
    @ns.expect(semantic_search_model, validate=True)
    def post(self):
        payload = request.get_json() or {}
        ecs = _ecs()
        try:
            res = ecs.semantic_search(
                query_embedding=payload.get("embedding") or [],
                limit=int(payload.get("limit", 10)),
                threshold=float(payload.get("threshold", 0.7)),
            )
            return {"results": res, "count": len(res)}
        finally:
            ecs.close()


@ns.route("/provenance/<string:entity_id>")
class Provenance(Resource):
    @jwt_required()
    def get(self, entity_id: str):
        ecs = _ecs()
        try:
            res = ecs.get_knowledge_provenance(entity_id)
            return {"history": res, "count": len(res)}
        finally:
            ecs.close()


@ns.route("/traverse")
class Traverse(Resource):
    @jwt_required()
    @ns.expect(traverse_model, validate=True)
    def post(self):
        payload = request.get_json() or {}
        ecs = _ecs()
        try:
            res = ecs.traverse_related(
                start_id=str(payload.get("start_id")),
                max_depth=int(payload.get("max_depth", 2)),
                rel_types=payload.get("rel_types"),
                limit=int(payload.get("limit", 50)),
            )
            return {"nodes": res, "count": len(res)}
        finally:
            ecs.close()


@ns.route("/graph/centrality")
class Centrality(Resource):
    @jwt_required()
    @ns.expect(centrality_model, validate=True)
    def post(self):
        payload = request.get_json() or {}
        ecs = _ecs()
        try:
            res = ecs.centrality_pagerank(
                top_n=int(payload.get("top_n", 20)),
                relationship=str(payload.get("relationship", "SIMILAR_TO")),
            )
            return {"scores": res, "count": len(res)}
        finally:
            ecs.close()


@ns.route("/graph/communities")
class Communities(Resource):
    @jwt_required()
    @ns.expect(communities_model, validate=True)
    def post(self):
        payload = request.get_json() or {}
        ecs = _ecs()
        try:
            res = ecs.community_detection_louvain(
                write_property=str(payload.get("write_property", "communityId"))
            )
            return {"result": res}
        finally:
            ecs.close()


@ns.route("/temporal/<string:entity_id>")
class Temporal(Resource):
    @jwt_required()
    def get(self, entity_id: str):
        since = request.args.get("since")
        until = request.args.get("until")
        ecs = _ecs()
        try:
            res = ecs.temporal_evolution(entity_id, since_iso=since, until_iso=until)
            return {"timeline": res}
        finally:
            ecs.close()
