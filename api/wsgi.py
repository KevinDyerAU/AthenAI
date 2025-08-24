# WSGI entrypoint for the API service
# Exposes `app` for Gunicorn to serve with gevent-websocket workers.

from .app import create_app  # type: ignore

app = create_app()

# Gunicorn will import `app` from this module.
# Socket.IO is initialized within create_app via `extensions.socketio`.
