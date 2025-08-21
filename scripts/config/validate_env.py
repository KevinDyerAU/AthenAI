#!/usr/bin/env python3
"""
validate_env.py

Usage:
  python scripts/config/validate_env.py --env-file .env.development.example --environment development
  python scripts/config/validate_env.py --env-file .env.production.example --environment production

Exits with code 0 if valid, 1 otherwise.
"""
from __future__ import annotations
import argparse
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# Simple .env file loader (no external deps). Supports KEY=VALUE and ignores comments.
ENV_LINE_RE = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)\s*$")


def load_env_file(path: Path) -> Dict[str, str]:
    env: Dict[str, str] = {}
    if not path.exists():
        raise FileNotFoundError(f"Env file not found: {path}")
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        m = ENV_LINE_RE.match(line)
        if not m:
            # Allow lines like VAR="quoted value" or with inline comments later; keep simple
            if "=" not in line:
                continue
            key, val = line.split("=", 1)
            key = key.strip()
            val = val.strip()
        else:
            key = m.group(1)
            val = m.group(2)
        # Strip surrounding quotes
        if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
            val = val[1:-1]
        env[key] = val
    return env


def is_url(s: str) -> bool:
    return bool(re.match(r"^(http|https)://", s or ""))


def is_amqp_url(s: str) -> bool:
    return bool(re.match(r"^amqp(s)?://", s or ""))


def is_db_url(s: str) -> bool:
    return bool(re.match(r"^postgresql\+psycopg2://", s or ""))


def is_bolt_url(s: str) -> bool:
    return bool(re.match(r"^bolt(\+s)?://", s or ""))


def require(keys: List[str], env: Dict[str, str], errors: List[str], prefix: str = ""):
    for k in keys:
        if not env.get(k):
            errors.append(f"Missing required {prefix}{k}")


def validate_common(env: Dict[str, str], environment: str, errors: List[str], warnings: List[str]):
    require(["APP_ENV", "PORT", "LOG_LEVEL"], env, errors)
    try:
        if int(env.get("PORT", "")) <= 0:
            errors.append("PORT must be a positive integer")
    except ValueError:
        errors.append("PORT must be an integer")
    if environment == "production":
        if env.get("CORS_ORIGINS", "*") in ("*", "*"):
            warnings.append("CORS_ORIGINS should not be '*' in production")


def validate_db(env: Dict[str, str], errors: List[str], warnings: List[str]):
    db_url = env.get("DATABASE_URL")
    if not db_url:
        # derive from components
        require(["DB_HOST", "DB_PORT", "DB_USER", "DB_PASSWORD", "DB_NAME"], env, errors, prefix="DB_")
    else:
        if not is_db_url(db_url):
            errors.append("DATABASE_URL must start with postgresql+psycopg2://")
    # Pooling
    for k in ["DB_POOL_SIZE", "DB_MAX_OVERFLOW", "DB_POOL_TIMEOUT", "DB_POOL_RECYCLE"]:
        if k in env and env[k]:
            try:
                int(env[k])
            except ValueError:
                errors.append(f"{k} must be an integer")


def validate_security(env: Dict[str, str], environment: str, errors: List[str], warnings: List[str]):
    require(["JWT_SECRET"], env, errors)
    if environment == "production":
        if env.get("TLS_ENABLED", "false").lower() == "true":
            require(["TLS_CERT_FILE", "TLS_KEY_FILE"], env, errors)
        if env.get("DATABASE_SSL_MODE", ""):  # recommend require or verify-full
            mode = env["DATABASE_SSL_MODE"].lower()
            if mode not in ("require", "verify-ca", "verify-full"):
                warnings.append("DATABASE_SSL_MODE should be 'require', 'verify-ca', or 'verify-full' in production")


def validate_integrations(env: Dict[str, str], environment: str, errors: List[str], warnings: List[str]):
    # n8n
    require(["N8N_BASE_URL"], env, errors)
    if env.get("N8N_BASE_URL") and not is_url(env["N8N_BASE_URL"]):
        errors.append("N8N_BASE_URL must be http(s) URL")
    # Neo4j
    require(["NEO4J_URI", "NEO4J_USER", "NEO4J_PASSWORD"], env, errors)
    if env.get("NEO4J_URI") and not is_bolt_url(env["NEO4J_URI"]):
        errors.append("NEO4J_URI must start with bolt:// or bolt+s://")
    # RabbitMQ
    if environment == "production":
        require(["RABBITMQ_URL"], env, errors)
    if env.get("RABBITMQ_URL") and not is_amqp_url(env["RABBITMQ_URL"]):
        errors.append("RABBITMQ_URL must start with amqp:// or amqps://")


def validate_ai(env: Dict[str, str], errors: List[str], warnings: List[str]):
    # Only check presence if provider set
    provider = (env.get("AI_DEFAULT_PROVIDER") or "").lower()
    if provider == "openai" and not env.get("OPENAI_API_KEY"):
        warnings.append("OPENAI_API_KEY is empty while provider is openai")
    if provider == "anthropic" and not env.get("ANTHROPIC_API_KEY"):
        warnings.append("ANTHROPIC_API_KEY is empty while provider is anthropic")


def validate_backups(env: Dict[str, str], environment: str, errors: List[str], warnings: List[str]):
    if env.get("BACKUP_ENABLED", "false").lower() == "true":
        require(["BACKUP_S3_BUCKET", "BACKUP_SCHEDULE_CRON", "BACKUP_RETENTION_DAYS"], env, errors)
        try:
            int(env.get("BACKUP_RETENTION_DAYS", ""))
        except ValueError:
            errors.append("BACKUP_RETENTION_DAYS must be an integer")


def validate_env(env: Dict[str, str], environment: str) -> Tuple[List[str], List[str]]:
    errors: List[str] = []
    warnings: List[str] = []
    validate_common(env, environment, errors, warnings)
    validate_db(env, errors, warnings)
    validate_security(env, environment, errors, warnings)
    validate_integrations(env, environment, errors, warnings)
    validate_ai(env, errors, warnings)
    validate_backups(env, environment, errors, warnings)
    return errors, warnings


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--env-file", required=True)
    parser.add_argument("--environment", choices=["development", "staging", "production"], required=True)
    args = parser.parse_args()

    env_file = Path(args.env_file)
    try:
        env = load_env_file(env_file)
    except Exception as e:
        print(f"ERROR: failed to load env file: {e}")
        sys.exit(1)

    errors, warnings = validate_env(env, args.environment)

    print("Validation summary:\n-------------------")
    if warnings:
        print("Warnings:")
        for w in warnings:
            print(f" - {w}")
    if errors:
        print("Errors:")
        for e in errors:
            print(f" - {e}")
        sys.exit(1)

    print("All checks passed.")
    sys.exit(0)


if __name__ == "__main__":
    main()
