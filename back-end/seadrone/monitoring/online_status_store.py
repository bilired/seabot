from __future__ import annotations

import logging
import os
import time
from typing import Any


logger = logging.getLogger(__name__)


def _normalize_ship_model(ship_model: str | None) -> str:
    return (ship_model or '').strip().upper()


def _get_redis_client() -> Any | None:
    redis_url = os.getenv('REDIS_URL', '').strip()
    if not redis_url:
        return None

    try:
        import redis  # type: ignore
    except Exception as exc:
        logger.warning('redis package unavailable, online heartbeat disabled: %s', exc)
        return None

    try:
        return redis.from_url(redis_url, decode_responses=True)
    except Exception as exc:
        logger.warning('redis connection init failed, online heartbeat disabled: %s', exc)
        return None


def _heartbeat_key() -> str:
    prefix = os.getenv('ONLINE_STATUS_KEY_PREFIX', 'seabot')
    return f'{prefix}:device:heartbeat'


def mark_device_online(ship_model: str | None) -> None:
    model = _normalize_ship_model(ship_model)
    if not model:
        return

    client = _get_redis_client()
    if client is None:
        return

    now = time.time()
    try:
        client.zadd(_heartbeat_key(), {model: now})
    except Exception as exc:
        logger.warning('redis heartbeat write failed for %s: %s', model, exc)


def get_online_ship_models(window_seconds: int) -> set[str]:
    seconds = max(int(window_seconds), 1)
    client = _get_redis_client()
    if client is None:
        return set()

    now = time.time()
    cutoff = now - seconds
    key = _heartbeat_key()

    try:
        client.zremrangebyscore(key, '-inf', cutoff)
        raw_members = client.zrangebyscore(key, cutoff, '+inf')
    except Exception as exc:
        logger.warning('redis heartbeat read failed: %s', exc)
        return set()

    return {
        _normalize_ship_model(member)
        for member in raw_members
        if _normalize_ship_model(member)
    }
