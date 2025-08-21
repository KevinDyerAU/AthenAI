from flask_socketio import SocketIO


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

    @socketio.on("disconnect")
    def on_disconnect():
        pass
