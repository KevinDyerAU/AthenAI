from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..utils.neo4j_client import get_client
from ..utils.rabbitmq import publish_task

ns = Namespace("conversations", description="Conversation management with persistent memory in Neo4j")

conversation_model = ns.model("Conversation", {
    "id": fields.String,
    "title": fields.String,
    "created_at": fields.Integer,
})

message_model = ns.model("Message", {
    "id": fields.String,
    "conversation_id": fields.String,
    "role": fields.String(enum=["user", "assistant", "system", "agent"]),
    "content": fields.String,
    "created_at": fields.Integer,
    "agent": fields.String,
})

create_conv_model = ns.model("CreateConversation", {
    "title": fields.String,
    "context": fields.Raw,
})

post_message_model = ns.model("PostMessage", {
    "role": fields.String(required=True, enum=["user", "assistant", "system", "agent"]),
    "content": fields.String(required=True),
    "agent": fields.String,
})

delegate_model = ns.model("Delegate", {
    "agent": fields.String(required=True),
    "task": fields.String(required=True),
    "metadata": fields.Raw,
})


@ns.route("")
class ConversationCollection(Resource):
    @jwt_required()
    def get(self):
        user = get_jwt_identity()
        uid = user["id"] if isinstance(user, dict) else user
        cypher = (
            "MATCH (u:User {id: $uid})-[:OWNS]->(c:Conversation) "
            "RETURN c ORDER BY c.created_at DESC LIMIT 100"
        )
        rows = get_client().run_query(cypher, {"uid": str(uid)})
        items = [r["c"] for r in rows]
        return {"items": [dict(id=i.get("id"), title=i.get("title"), created_at=i.get("created_at")) for i in items]}

    @jwt_required()
    @ns.expect(create_conv_model, validate=True)
    def post(self):
        payload = request.get_json() or {}
        user = get_jwt_identity()
        uid = user["id"] if isinstance(user, dict) else user
        cypher = (
            "MERGE (u:User {id: $uid}) "
            "WITH u, randomUUID() AS cid, timestamp() AS now "
            "CREATE (c:Conversation {id: cid, title: coalesce($title, 'Conversation'), created_at: now}) "
            "MERGE (u)-[:OWNS]->(c) "
            "WITH c "
            "FOREACH (ctx IN CASE WHEN $context IS NULL THEN [] ELSE [$context] END | SET c.context = ctx) "
            "RETURN c"
        )
        row = get_client().run_query(cypher, {"uid": str(uid), "title": payload.get("title"), "context": payload.get("context")})
        c = row[0]["c"] if row else {}
        return dict(id=c.get("id"), title=c.get("title"), created_at=c.get("created_at")), 201


@ns.route("/<string:cid>")
class ConversationItem(Resource):
    @jwt_required()
    def get(self, cid: str):
        user = get_jwt_identity()
        uid = user["id"] if isinstance(user, dict) else user
        cypher = (
            "MATCH (u:User {id: $uid})-[:OWNS]->(c:Conversation {id: $cid}) "
            "OPTIONAL MATCH (c)-[:HAS_MESSAGE]->(m:Message) "
            "RETURN c, collect(m) AS messages"
        )
        rows = get_client().run_query(cypher, {"uid": str(uid), "cid": cid})
        if not rows:
            ns.abort(404, "Conversation not found")
        c = rows[0][0]
        messages = rows[0][1] or []
        return {
            "conversation": dict(id=c.get("id"), title=c.get("title"), created_at=c.get("created_at")),
            "messages": [dict(id=m.get("id"), role=m.get("role"), content=m.get("content"), created_at=m.get("created_at"), agent=m.get("agent")) for m in messages]
        }


@ns.route("/<string:cid>/messages")
class ConversationMessages(Resource):
    @jwt_required()
    @ns.expect(post_message_model, validate=True)
    def post(self, cid: str):
        payload = request.get_json() or {}
        user = get_jwt_identity()
        uid = user["id"] if isinstance(user, dict) else user
        cypher = (
            "MATCH (u:User {id: $uid})-[:OWNS]->(c:Conversation {id: $cid}) "
            "WITH c, randomUUID() AS mid, timestamp() AS now "
            "CREATE (m:Message {id: mid, role: $role, content: $content, created_at: now, agent: $agent}) "
            "MERGE (c)-[:HAS_MESSAGE]->(m) "
            "RETURN m"
        )
        row = get_client().run_query(cypher, {"uid": str(uid), "cid": cid, "role": payload.get("role"), "content": payload.get("content"), "agent": payload.get("agent")})
        m = row[0]["m"] if row else {}
        return dict(id=m.get("id"), role=m.get("role"), content=m.get("content"), created_at=m.get("created_at"), agent=m.get("agent")), 201


@ns.route("/<string:cid>/delegate")
class ConversationDelegate(Resource):
    @jwt_required()
    @ns.expect(delegate_model, validate=True)
    def post(self, cid: str):
        payload = request.get_json() or {}
        user = get_jwt_identity()
        uid = user["id"] if isinstance(user, dict) else user
        # Publish to RabbitMQ for async agent delegation
        task = {
            "type": "agent.delegation",
            "conversation_id": cid,
            "user_id": str(uid),
            "agent": payload.get("agent"),
            "task": payload.get("task"),
            "metadata": payload.get("metadata") or {},
        }
        publish_task(task)
        return {"status": "queued", "task": task}, 202
