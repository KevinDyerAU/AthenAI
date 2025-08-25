from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..utils.neo4j_client import get_client
from ..utils.rabbitmq import publish_task
from ..extensions import socketio

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
        message = dict(id=m.get("id"), role=m.get("role"), content=m.get("content"), created_at=m.get("created_at"), agent=m.get("agent"))
        # Emit real-time update to WS room named by conversation id
        try:
            socketio.emit("message:new", {"conversation_id": cid, "message": message}, room=cid)
        except Exception:
            pass
        return message, 201


@ns.route("/<string:cid>/messages/search")
class ConversationMessageSearch(Resource):
    @jwt_required()
    def get(self, cid: str):
        """Search messages by substring match in content. Query param: q, limit=50"""
        user = get_jwt_identity()
        uid = user["id"] if isinstance(user, dict) else user
        q = (request.args.get("q") or "").strip()
        limit = int(request.args.get("limit", 50))
        if not q:
            ns.abort(400, "q is required")
        cypher = (
            "MATCH (u:User {id: $uid})-[:OWNS]->(c:Conversation {id: $cid})-[:HAS_MESSAGE]->(m:Message) "
            "WHERE toLower(m.content) CONTAINS toLower($q) "
            "RETURN m ORDER BY m.created_at DESC LIMIT $limit"
        )
        rows = get_client().run_query(cypher, {"uid": str(uid), "cid": cid, "q": q, "limit": limit})
        messages = [r["m"] for r in rows]
        return {"items": [dict(id=m.get("id"), role=m.get("role"), content=m.get("content"), created_at=m.get("created_at"), agent=m.get("agent")) for m in messages], "count": len(messages)}


@ns.route("/<string:cid>/messages")
class ConversationMessagesList(Resource):
    @jwt_required()
    def get(self, cid: str):
        """Paginated messages list: limit, offset, optional role, since, until (timestamps)."""
        user = get_jwt_identity()
        uid = user["id"] if isinstance(user, dict) else user
        limit = int(request.args.get("limit", 50))
        offset = int(request.args.get("offset", 0))
        role = request.args.get("role")
        since = request.args.get("since")  # epoch ms
        until = request.args.get("until")  # epoch ms

        where_parts = []
        if role:
            where_parts.append("m.role = $role")
        if since:
            where_parts.append("m.created_at >= toInteger($since)")
        if until:
            where_parts.append("m.created_at <= toInteger($until)")
        where_clause = ("WHERE " + " AND ".join(where_parts)) if where_parts else ""
        cypher = (
            "MATCH (u:User {id: $uid})-[:OWNS]->(c:Conversation {id: $cid})-[:HAS_MESSAGE]->(m:Message) "
            f"{where_clause} "
            "WITH m ORDER BY m.created_at DESC SKIP $offset LIMIT $limit "
            "RETURN collect(m) AS messages"
        )
        params = {"uid": str(uid), "cid": cid, "limit": limit, "offset": offset, "role": role, "since": since, "until": until}
        rows = get_client().run_query(cypher, params)
        msgs = rows[0][0] if rows else []
        items = [dict(id=m.get("id"), role=m.get("role"), content=m.get("content"), created_at=m.get("created_at"), agent=m.get("agent")) for m in msgs]
        return {"items": items, "count": len(items), "limit": limit, "offset": offset}


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


participant_model = ns.model("Participant", {
    "user_id": fields.String(required=True),
    "role": fields.String(description="participant role", default="member"),
})


@ns.route("/<string:cid>/participants")
class ConversationParticipants(Resource):
    @jwt_required()
    def get(self, cid: str):
        user = get_jwt_identity()
        uid = user["id"] if isinstance(user, dict) else user
        cypher = (
            "MATCH (owner:User {id: $uid})-[:OWNS]->(c:Conversation {id: $cid}) "
            "OPTIONAL MATCH (c)<-[:MEMBER_OF]-(p:User) "
            "RETURN collect(p.id) AS participants"
        )
        rows = get_client().run_query(cypher, {"uid": str(uid), "cid": cid})
        participants = rows[0][0] if rows else []
        return {"participants": [str(x) for x in participants if x is not None]}

    @jwt_required()
    @ns.expect(participant_model, validate=True)
    def post(self, cid: str):
        payload = request.get_json() or {}
        target = str(payload.get("user_id"))
        if not target:
            ns.abort(400, "user_id required")
        user = get_jwt_identity()
        uid = user["id"] if isinstance(user, dict) else user
        role = (payload.get("role") or "member").strip()
        cypher = (
            "MATCH (owner:User {id: $uid})-[:OWNS]->(c:Conversation {id: $cid}) "
            "MERGE (u:User {id: $target}) "
            "MERGE (u)-[r:MEMBER_OF]->(c) "
            "SET r.role = $role "
            "RETURN u.id AS id, r.role AS role"
        )
        rows = get_client().run_query(cypher, {"uid": str(uid), "cid": cid, "target": target, "role": role})
        if not rows:
            ns.abort(404, "Conversation not found")
        added = rows[0]
        try:
            socketio.emit("permission:updated", {"conversation_id": cid, "user_id": target, "role": role}, room=cid)
        except Exception:
            pass
        return {"added": added[0], "role": role}, 201


@ns.route("/<string:cid>/participants/<string:user_id>")
class ConversationParticipantItem(Resource):
    @jwt_required()
    def delete(self, cid: str, user_id: str):
        user = get_jwt_identity()
        uid = user["id"] if isinstance(user, dict) else user
        cypher = (
            "MATCH (owner:User {id: $uid})-[:OWNS]->(c:Conversation {id: $cid}) "
            "MATCH (u:User {id: $target})- [r:MEMBER_OF]->(c) "
            "DELETE r RETURN count(r) AS removed"
        )
        rows = get_client().run_query(cypher, {"uid": str(uid), "cid": cid, "target": str(user_id)})
        removed = rows[0][0] if rows else 0
        try:
            socketio.emit("permission:revoked", {"conversation_id": cid, "user_id": user_id}, room=cid)
        except Exception:
            pass
        return {"removed": int(removed)}


perm_set_model = ns.model("PermissionSet", {
    "user_id": fields.String(required=True),
    "role": fields.String(required=True, description="member|admin|viewer|guest"),
})


@ns.route("/<string:cid>/permissions")
class ConversationPermissions(Resource):
    @jwt_required()
    def get(self, cid: str):
        """List participants with roles."""
        user = get_jwt_identity()
        uid = user["id"] if isinstance(user, dict) else user
        cypher = (
            "MATCH (owner:User {id: $uid})-[:OWNS]->(c:Conversation {id: $cid}) "
            "OPTIONAL MATCH (u:User)-[r:MEMBER_OF]->(c) "
            "RETURN collect({user_id: u.id, role: coalesce(r.role,'member')}) AS items"
        )
        rows = get_client().run_query(cypher, {"uid": str(uid), "cid": cid})
        items = rows[0][0] if rows else []
        # normalize to python dicts
        items = [dict(user_id=i.get("user_id"), role=i.get("role")) for i in items if i and i.get("user_id")]
        return {"items": items, "count": len(items)}

    @jwt_required()
    @ns.expect(perm_set_model, validate=True)
    def post(self, cid: str):
        """Set a user's role on the conversation."""
        payload = request.get_json() or {}
        target = str(payload.get("user_id"))
        role = (payload.get("role") or "member").strip()
        user = get_jwt_identity()
        uid = user["id"] if isinstance(user, dict) else user
        cypher = (
            "MATCH (owner:User {id: $uid})-[:OWNS]->(c:Conversation {id: $cid}) "
            "MERGE (u:User {id: $target}) "
            "MERGE (u)-[r:MEMBER_OF]->(c) "
            "SET r.role = $role "
            "RETURN u.id AS user_id, r.role AS role"
        )
        rows = get_client().run_query(cypher, {"uid": str(uid), "cid": cid, "target": target, "role": role})
        if not rows:
            ns.abort(404, "Conversation not found")
        try:
            socketio.emit("permission:updated", {"conversation_id": cid, "user_id": target, "role": role}, room=cid)
        except Exception:
            pass
        return {"user_id": rows[0][0], "role": rows[0][1]}, 200


@ns.route("/<string:cid>/permissions/<string:user_id>")
class ConversationPermissionItem(Resource):
    @jwt_required()
    def delete(self, cid: str, user_id: str):
        """Revoke a user's membership (same as removing participant)."""
        user = get_jwt_identity()
        uid = user["id"] if isinstance(user, dict) else user
        cypher = (
            "MATCH (owner:User {id: $uid})-[:OWNS]->(c:Conversation {id: $cid}) "
            "MATCH (u:User {id: $target})-[r:MEMBER_OF]->(c) DELETE r RETURN count(r) AS removed"
        )
        rows = get_client().run_query(cypher, {"uid": str(uid), "cid": cid, "target": str(user_id)})
        removed = rows[0][0] if rows else 0
        try:
            socketio.emit("permission:revoked", {"conversation_id": cid, "user_id": user_id}, room=cid)
        except Exception:
            pass
        return {"removed": int(removed)}
