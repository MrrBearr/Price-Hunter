import json
from typing import Optional, Any
import redis.asyncio as redis
from app.config import get_settings

settings = get_settings()


class RedisService:
    _pool: Optional[redis.Redis] = None

    @classmethod
    async def get_connection(cls) -> redis.Redis:
        if cls._pool is None:
            cls._pool = redis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True,
            )
        return cls._pool

    @classmethod
    async def publish_task(cls, queue: str, data: dict) -> None:
        conn = await cls.get_connection()
        await conn.lpush(queue, json.dumps(data))

    @classmethod
    async def get_task(cls, queue: str, timeout: int = 0) -> Optional[dict]:
        conn = await cls.get_connection()
        result = await conn.brpop(queue, timeout=timeout)
        if result:
            _, data = result
            return json.loads(data)
        return None

    @classmethod
    async def cache_set(cls, key: str, value: Any, expire: int = 3600) -> None:
        conn = await cls.get_connection()
        await conn.set(key, json.dumps(value), ex=expire)

    @classmethod
    async def cache_get(cls, key: str) -> Optional[Any]:
        conn = await cls.get_connection()
        data = await conn.get(key)
        if data:
            return json.loads(data)
        return None

    @classmethod
    async def cache_delete(cls, key: str) -> None:
        conn = await cls.get_connection()
        await conn.delete(key)

    @classmethod
    async def get_queue_length(cls, queue: str) -> int:
        conn = await cls.get_connection()
        return await conn.llen(queue)
