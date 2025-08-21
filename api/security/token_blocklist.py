from datetime import datetime, timezone
from typing import Set

# Simple in-memory blocklist. Replace with persistent store (e.g., Redis) in production.
BLOCKLIST: Set[str] = set()


def add(jti: str):
    if jti:
        BLOCKLIST.add(jti)


def is_blocked(jti: str) -> bool:
    return jti in BLOCKLIST
