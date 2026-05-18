import json
import logging
from typing import Optional, Any

from app.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

# In-memory cache fallback when Redis is not available
_memory_cache: dict = {}


class RedisService:
    _pool = None
    _available: Optional[bool] = None

    @classmethod
    async def _is_available(cls) -> bool:
        if cls._available is not None:
            return cls._available
        if not settings.redis_url:
            cls._available = False
            return False
        try:
            import redis.asyncio as redis
            conn = redis.from_url(settings.redis_url, encoding="utf-8", decode_responses=True)
            await conn.ping()
            cls._pool = conn
            cls._available = True
            return True
        except Exception:
            logger.warning("Redis not available, using in-memory fallback")
            cls._available = False
            return False

    @classmethod
    async def get_connection(cls):
        if await cls._is_available():
            return cls._pool
        return None

    @classmethod
    async def publish_task(cls, queue: str, data: dict) -> None:
        conn = await cls.get_connection()
        if conn:
            await conn.lpush(queue, json.dumps(data))

    @classmethod
    async def get_task(cls, queue: str, timeout: int = 0) -> Optional[dict]:
        conn = await cls.get_connection()
        if conn:
            result = await conn.brpop(queue, timeout=timeout)
            if result:
                _, data = result
                return json.loads(data)
        return None

    @classmethod
    async def cache_set(cls, key: str, value: Any, expire: int = 3600) -> None:
        conn = await cls.get_connection()
        if conn:
            await conn.set(key, json.dumps(value), ex=expire)
        else:
            _memory_cache[key] = value

    @classmethod
    async def cache_get(cls, key: str) -> Optional[Any]:
        conn = await cls.get_connection()
        if conn:
            data = await conn.get(key)
            if data:
                return json.loads(data)
        else:
            return _memory_cache.get(key)
        return None

    @classmethod
    async def cache_delete(cls, key: str) -> None:
        conn = await cls.get_connection()
        if conn:
            await conn.delete(key)
        else:
            _memory_cache.pop(key, None)

    @classmethod
    async def get_queue_length(cls, queue: str) -> int:
        conn = await cls.get_connection()
        if conn:
            return await conn.llen(queue)
        return 0
