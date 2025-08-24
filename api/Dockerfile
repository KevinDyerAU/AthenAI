# Python base image
FROM python:3.11-slim

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
 && rm -rf /var/lib/apt/lists/*

# Workdir
WORKDIR /app

# Copy requirements first for caching
COPY requirements.txt /app/requirements.txt

# Install dependencies (include gunicorn and gevent stack for websockets)
RUN pip install --no-cache-dir -r /app/requirements.txt \
    && pip install --no-cache-dir gunicorn gevent gevent-websocket greenlet

# Copy app into a package directory so imports are under the 'api' package
COPY . /app/api

# Env
ENV PYTHONUNBUFFERED=1 \
    HOST=0.0.0.0 \
    PORT=5000

# Expose ports (HTTP and optional WS secondary if used)
EXPOSE 5000 5001

# Healthcheck path is /health via compose healthcheck

# Start with Gunicorn using gevent websocket worker
# Import WSGI app from the api package so relative imports work
CMD ["gunicorn", "-k", "geventwebsocket.gunicorn.workers.GeventWebSocketWorker", "-w", "1", "-b", "0.0.0.0:5000", "api.wsgi:app"]
