##########
# Builder #
##########
FROM python:3.11-slim AS builder

ENV VIRTUAL_ENV=/opt/venv \
    PATH=/opt/venv/bin:$PATH \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Build deps for compiling any wheels
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    libpq-dev \
    libffi-dev \
  && rm -rf /var/lib/apt/lists/*

# Create virtualenv
RUN python -m venv $VIRTUAL_ENV

WORKDIR /app

# Install Python deps first for better caching
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip \
 && pip install --no-cache-dir -r /app/requirements.txt \
 && pip install --no-cache-dir gunicorn

# Copy application source
COPY . /app/api

###########
# Runtime #
###########
FROM python:3.11-slim AS runtime

ENV VIRTUAL_ENV=/opt/venv \
    PATH=/opt/venv/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    HOST=0.0.0.0 \
    PORT=5000

# Runtime OS deps (no compilers)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
  && rm -rf /var/lib/apt/lists/*

# Non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

# Copy venv and app from builder
COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /app/api /app/api

# Create runtime dirs with safe perms
RUN mkdir -p /app/logs /app/data \
 && chown -R appuser:appuser /app

USER appuser

# Expose HTTP and optional WS
EXPOSE 5000 5001

# Default healthcheck is defined in docker-compose.yml hitting /system/health

# Start with Gunicorn using gevent-websocket worker (Socket.IO compatible)
CMD ["gunicorn", "-k", "geventwebsocket.gunicorn.workers.GeventWebSocketWorker", "-w", "1", "-b", "0.0.0.0:5000", "api.wsgi:app"]
