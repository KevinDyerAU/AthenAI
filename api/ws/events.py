import os
import uuid
from datetime import datetime
from functools import wraps
from typing import Any, Dict, Optional

from flask import request, current_app
from flask_socketio import SocketIO, join_room, leave_room, emit
from flask_jwt_extended import decode_token

from ..utils.neo4j_client import get_client
from ..utils.rabbitmq import start_consumer
from ..metrics import (
    record_websocket_connection,
    record_websocket_message,
)


class WebSocketManager:
    def __init__(self, socketio: SocketIO):
        self.socketio = socketio
        self.active: dict[str, Dict[str, Any]] = {}
        self._consumer_started = False

    # ------------------------- Auth -------------------------
    def _authenticate(self):
        token = request.args.get("token") or (request.headers.get("Authorization") or "").replace("Bearer ", "").strip()
        if not token:
            return None  # anonymous allowed for public rooms/features
        try:
            data = decode_token(token)
            identity = data.get("sub")
            # `sub` may be dict or str depending on how tokens are issued
            if isinstance(identity, dict):
                return str(identity.get("id") or identity.get("user_id") or identity)
            return str(identity)
        except Exception:
            return None

    def _auth_required(self, f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            uid = self._authenticate()
            if uid is None:
                emit("error", {"message": "auth_required"})
                return
            request.ws_user_id = uid  # type: ignore[attr-defined]
            return f(*args, **kwargs)

        return wrapper

    # ------------------------- Persistence -------------------------
    def _verify_conversation_access(self, conversation_id: str, user_id: Optional[str]) -> bool:
        if not user_id:
            return False
        cypher = (
            "MATCH (u:User {id: $uid})-[:OWNS]->(c:Conversation {id: $cid}) RETURN c LIMIT 1"
        )
        rows = get_client().run_query(cypher, {"uid": str(user_id), "cid": conversation_id})
        return bool(rows)

    def _store_message(self, conversation_id: str, user_id: Optional[str], role: str, content: str, agent: Optional[str] = None) -> Dict[str, Any]:
        cypher = (
            "MATCH (c:Conversation {id: $cid}) "
            "WITH c, randomUUID() AS mid, timestamp() AS now "
            "CREATE (m:Message {id: mid, role: $role, content: $content, created_at: now, agent: $agent, user_id: $uid}) "
            "MERGE (c)-[:HAS_MESSAGE]->(m) RETURN m"
        )
        params = {"cid": conversation_id, "role": role, "content": content, "agent": agent, "uid": user_id}
        row = get_client().run_query(cypher, params)
        m = row[0]["m"] if row else {}
        return {
            "id": m.get("id"),
            "conversation_id": conversation_id,
            "role": m.get("role"),
            "content": m.get("content"),
            "created_at": m.get("created_at"),
            "agent": m.get("agent"),
            "user_id": user_id,
        }

    def _fetch_history(self, conversation_id: str, limit: int = 50) -> list[Dict[str, Any]]:
        cypher = (
            "MATCH (c:Conversation {id: $cid})-[:HAS_MESSAGE]->(m:Message) "
            "RETURN m ORDER BY m.created_at DESC LIMIT $lim"
        )
        rows = get_client().run_query(cypher, {"cid": conversation_id, "lim": int(limit)})
        out = []
        for r in rows:
            m = r["m"]
            out.append({
                "id": m.get("id"),
                "conversation_id": conversation_id,
                "role": m.get("role"),
                "content": m.get("content"),
                "created_at": m.get("created_at"),
                "agent": m.get("agent"),
                "user_id": m.get("user_id"),
            })
        return list(reversed(out))

    # ------------------------- RabbitMQ -> WS -------------------------
    def _start_agent_updates_consumer(self):
        if self._consumer_started:
            return

        def _on_msg(payload: Dict[str, Any]):
            # Expected payload includes conversation_id and event type
            cid = payload.get("conversation_id")
            if not cid:
                return
            event = payload.get("event") or "agent:update"
            self.socketio.emit(event, payload, room=cid)

        def _runner():
            # Blocking consume; restart on failure
            queue = os.getenv("AGENT_UPDATES_QUEUE", "agent_updates")
            while True:
                stop = start_consumer(queue, _on_msg)  # returns None if cannot connect
                if stop is None:
                    self.socketio.sleep(5)
                    continue
                # start_consumer blocks until stopped; if it returns, loop to reconnect
                self.socketio.sleep(1)

        self.socketio.start_background_task(_runner)
        self._consumer_started = True

    # ------------------------- Registration -------------------------
    def register(self):
        sio = self.socketio

        @sio.on("connect")
        def on_connect():
            uid = self._authenticate()
            self.active[request.sid] = {
                "connection_id": str(uuid.uuid4()),
                "user_id": uid,
                "connected_at": datetime.utcnow().isoformat(),
                "rooms": set(),
            }
            record_websocket_connection(True)
            emit("connected", {"connection_id": self.active[request.sid]["connection_id"], "user_id": uid})
            # Ensure background consumer is running
            self._start_agent_updates_consumer()

        @sio.on("connect", namespace="/qa")
        def on_connect_qa():
            uid = self._authenticate()
            record_websocket_connection(True)
            emit("connected", {"user_id": uid}, namespace="/qa")

        @sio.on("disconnect", namespace="/qa")
        def on_disconnect_qa():
            record_websocket_connection(False)

        @sio.on("disconnect")
        def on_disconnect():
            self.active.pop(request.sid, None)
            record_websocket_connection(False)

        # ------------ Room management ------------
        @sio.on("room:join")
        @self._auth_required
        def on_room_join(data):
            cid = (data or {}).get("conversation_id")
            if not cid:
                emit("error", {"message": "conversation_id_required"})
                return
            uid = getattr(request, "ws_user_id", None)
            if not self._verify_conversation_access(cid, uid):
                emit("error", {"message": "access_denied"})
                return
            join_room(cid)
            info = self.active.get(request.sid)
            if info:
                info["rooms"].add(cid)
            emit("room:joined", {"conversation_id": cid})
            record_websocket_message("room:join", "in")
            # Send last messages as history
            emit("history", {"conversation_id": cid, "messages": self._fetch_history(cid, limit=50)})

        @sio.on("room:leave")
        def on_room_leave(data):
            cid = (data or {}).get("conversation_id")
            if not cid:
                return
            leave_room(cid)
            info = self.active.get(request.sid)
            if info and cid in info["rooms"]:
                info["rooms"].remove(cid)
            record_websocket_message("room:leave", "in")

        # ------------ Messaging ------------
        @sio.on("message:send")
        @self._auth_required
        def on_send(data):
            cid = (data or {}).get("conversation_id")
            content = (data or {}).get("message")
            role = (data or {}).get("role", "user")
            if not cid or not content:
                emit("error", {"message": "conversation_id_and_message_required"})
                return
            uid = getattr(request, "ws_user_id", None)
            if not self._verify_conversation_access(cid, uid):
                emit("error", {"message": "access_denied"})
                return
            msg = self._store_message(cid, uid, role, content)
            record_websocket_message("message", "in")
            emit("message:new", msg, room=cid)
            record_websocket_message("message", "out")

        @sio.on("history:get")
        @self._auth_required
        def on_history(data):
            cid = (data or {}).get("conversation_id")
            limit = int((data or {}).get("limit", 50))
            uid = getattr(request, "ws_user_id", None)
            if not cid or not self._verify_conversation_access(cid, uid):
                emit("error", {"message": "access_denied"})
                return
            record_websocket_message("history:get", "in")
            emit("history", {"conversation_id": cid, "messages": self._fetch_history(cid, limit=limit)})
            record_websocket_message("history", "out")


def register_socketio_events(socketio: SocketIO):
    WebSocketManager(socketio).register()
