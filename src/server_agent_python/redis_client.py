"""Redis client setup."""

from redis.asyncio import Redis

from .config import Settings


def create_client(settings: Settings) -> Redis:
    """Create a lazy async redis-py client."""

    return Redis.from_url(
        settings.redis_url,
        decode_responses=True,
        socket_connect_timeout=settings.redis_connect_timeout,
        socket_timeout=settings.redis_socket_timeout,
        health_check_interval=30,
    )


async def ping(client: Redis) -> None:
    """Verify Redis connectivity."""

    await client.ping()
