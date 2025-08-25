import os
import time
import socketio  # python-socketio client
import pytest

API_HOST = os.getenv("API_HOST", "http://localhost")
API_PORT = int(os.getenv("API_PORT", "5000"))
WS_URL = f"{API_HOST}:{API_PORT}"


def wait_for(event_data, timeout=3):
    start = time.time()
    while time.time() - start < timeout:
        if event_data[0] is not None:
            return event_data[0]
        time.sleep(0.05)
    return None


@pytest.mark.integration
def test_ws_connect_and_auth_enforcement():
    sio = socketio.Client(reconnection=False, transports=["websocket"])  # force ws

    connected_payload = [None]
    error_payload = [None]

    @sio.event
    def connected(data):
        connected_payload[0] = data

    @sio.event
    def error(data):
        error_payload[0] = data

    try:
        sio.connect(WS_URL, wait=True)
    except Exception as e:
        pytest.skip(f"Cannot connect to WebSocket server at {WS_URL}: {e}")

    # Should receive 'connected' with connection_id
    data = wait_for(connected_payload, timeout=3)
    assert data is not None and "connection_id" in data

    # Try to join room without auth token -> expect error auth_required
    sio.emit("room:join", {"conversation_id": "test-conv"})
    err = wait_for(error_payload, timeout=1)
    assert err is not None and err.get("message") == "auth_required"

    sio.disconnect()
