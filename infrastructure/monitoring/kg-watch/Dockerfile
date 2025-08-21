# Lightweight cron-based watcher container
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends cron ca-certificates && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy project (adjust context to repo root when building)
COPY . /app

# Install Python deps for the watcher
RUN pip install --no-cache-dir -r api/requirements.txt

# Add crontab
COPY infrastructure/monitoring/kg-watch/crontab /etc/cron.d/kg-watch
RUN chmod 0644 /etc/cron.d/kg-watch && crontab /etc/cron.d/kg-watch

# Entrypoint to start cron and tail logs
COPY infrastructure/monitoring/kg-watch/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Logs
RUN touch /var/log/cron.log

ENTRYPOINT ["/entrypoint.sh"]
