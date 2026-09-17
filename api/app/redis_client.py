import json
import uuid
from typing import Any, Optional

import redis.asyncio as redis

from app.config import (
    REDIS_DB,
    REDIS_HOST,
    REDIS_PASSWORD,
    REDIS_PORT,
    REDIS_SESSION_TTL,
)

KEY_PREFIX = "reborn:session:"

_client: Optional[redis.Redis] = None


def get_redis() -> redis.Redis:
    global _client
    if _client is None:
        _client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            password=REDIS_PASSWORD,
            db=REDIS_DB,
            decode_responses=True,
        )
    return _client


async def close_redis() -> None:
    global _client
    if _client is not None:
        await _client.close()
        _client = None


async def create_session(user_data: dict[str, Any], ttl: int = REDIS_SESSION_TTL) -> str:
    session_id = uuid.uuid4().hex
    key = f"{KEY_PREFIX}{session_id}"
    payload = json.dumps(user_data, default=str, ensure_ascii=False)
    await get_redis().setex(key, ttl, payload)
    return session_id


async def get_session(session_id: str) -> Optional[dict[str, Any]]:
    key = f"{KEY_PREFIX}{session_id}"
    data = await get_redis().get(key)
    if data is None:
        return None
    return json.loads(data)


async def delete_session(session_id: str) -> None:
    key = f"{KEY_PREFIX}{session_id}"
    await get_redis().delete(key)