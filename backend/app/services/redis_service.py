"""
Redis service with graceful fallback.
If Redis is not available or not installed, uses in-memory cache.
"""
import json
import logging
from typing import Optional, Any

logger = logging.getLogger(__name__)

# In-memory cache fallback
_memory_cache: dict = {}


class RedisService:
    _available: Optional[bool] = None
    _pool = None

    @classmethod
    async def _is_available(cls) -> bool:
        if cls._available is not None:
            return cls._available
        try:
            from app.config import get_settings
            settings = get_settings()
            if not settings.redis_url:
                cls._available = False
                return False

            import redis.asyncio as redis_lib
            conn = redis_lib.from_url(settings.redis_url, encoding="utf-8", decode_responses=True)
            await conn.ping()
            cls._pool = conn
            cls._available = True
            return True
        except ImportError:
            logger.info("Redis library not installed, using memory cache")
            cls._available = False
            return False
        except Exception:
            logger.info("Redis not available, using memory cache")
            cls._available = False
            return False

    @classmethod
    async def publish_task(cls, queue: str, data: dict) -> None:
        if await cls._is_available():
            await cls._pool.lpush(queue, json.dumps(data))

    @classmethod
    async def cache_set(cls, key: str, value: Any, expire: int = 3600) -> None:
        if await cls._is_available():
            await cls._pool.set(key, json.dumps(value), ex=expire)
        else:
            _memory_cache[key] = value

    @classmethod
    async def cache_get(cls, key: str) -> Optional[Any]:
        if await cls._is_available():
            data = await cls._pool.get(key)
            if data:
                return json.loads(data)
            return None
        return _memory_cache.get(key)

    @classmethod
    async def cache_delete(cls, key: str) -> None:
        if await cls._is_available():
            await cls._pool.delete(key)
        else:
            _memory_cache.pop(key, None)
