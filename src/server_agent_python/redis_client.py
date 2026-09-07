"""Redis 客户端配置。 / Redis client setup."""

from redis.asyncio import Redis

from .config import Settings


def create_client(settings: Settings) -> Redis:
    """创建延迟连接的异步 redis-py 客户端。 / Create a lazy async redis-py client."""

    return Redis.from_url(
        settings.redis_url,
        decode_responses=True,
        socket_connect_timeout=settings.redis_connect_timeout,
        socket_timeout=settings.redis_socket_timeout,
        health_check_interval=30,
    )


async def ping(client: Redis) -> None:
    """验证 Redis 连接。 / Verify Redis connectivity."""

    await client.ping()
