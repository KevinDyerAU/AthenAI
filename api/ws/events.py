from flask_socketio import SocketIO, join_room, leave_room


def register_socketio_events(socketio: SocketIO):
    @socketio.on("connect")
    def on_connect():
        # You can add auth checks here if desired
        socketio.emit("system:notification", {"message": "Connected to WebSocket"})

    @socketio.on("chat:message")
    def on_chat_message(data):
        # Broadcast chat message to all clients
        socketio.emit("chat:message", data, broadcast=True)

    @socketio.on("agent:status")
    def on_agent_status(data):
        # Forward agent status updates
        socketio.emit("agent:status", data, broadcast=True)

    # --- Context-aware events (rooms) ---
    @socketio.on("room:join")
    def on_room_join(data):
        cid = (data or {}).get("conversation_id")
        if not cid:
            return
        join_room(cid)
        socketio.emit("room:joined", {"conversation_id": cid}, room=cid)

    @socketio.on("room:leave")
    def on_room_leave(data):
        cid = (data or {}).get("conversation_id")
        if not cid:
            return
        leave_room(cid)

    @socketio.on("chat:message:room")
    def on_chat_message_room(data):
        cid = (data or {}).get("conversation_id")
        if not cid:
            return
        socketio.emit("chat:message", data, room=cid)

    @socketio.on("agent:status:room")
    def on_agent_status_room(data):
        cid = (data or {}).get("conversation_id")
        if not cid:
            return
        socketio.emit("agent:status", data, room=cid)

    @socketio.on("disconnect")
    def on_disconnect():
        pass
