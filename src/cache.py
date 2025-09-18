import redis.asyncio as redis
import json
from os import getenv
from typing import Any

REDIS_CONFIG = {
    "host": getenv("REDIS_HOST", "localhost"),
    "port": int(getenv("REDIS_PORT", 6379)),
    "db": int(getenv("REDIS_DB", 0)),
    "password": getenv("REDIS_PASSWORD", None),
}

REDIS_AVAILABLE = False
r: redis.Redis | None = None


TTL_DURATION = getenv("TTL_DURATION", 10)

async def init_redis():
    global r, REDIS_AVAILABLE
    try:
        r = redis.Redis(**REDIS_CONFIG)
        await r.ping()
        REDIS_AVAILABLE = True
        print("Redis initialized successfully!")
    except Exception as e:
        print(f"Redis connection failed: {e}")

async def close_redis():
    global r, REDIS_AVAILABLE
    if r:
        await r.close()
        r = None
        REDIS_AVAILABLE = False
        print("Redis connection closed")

async def insert_redis(key: str, data: Any, ttl: int = TTL_DURATION):
    if not REDIS_AVAILABLE or r is None:
        return 0

    json_data = json.dumps(data)
    await r.set(name=key, value=json_data, ex=ttl)

async def get_redis(key: str) -> str | None:
    if not REDIS_AVAILABLE or r is None:
        return None
    return await r.get(key)
