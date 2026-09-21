"""Redis 会话存储。 / Redis conversation store."""

import json
from typing import cast

from openai.types.chat import ChatCompletionMessageParam
from redis.asyncio import Redis

from server_agent_python.conversation.store import ConversationStore


class RedisConversationStore(ConversationStore):
    """基于 Redis 的会话存储。"""

    def __init__(
        self,
        redis: Redis,
        ttl_seconds: int = 86400,
    ) -> None:
        self._redis = redis
        self._ttl_seconds = ttl_seconds

    def _key(
        self,
        conversation_id: str,
    ) -> str:
        return f"conversation:{conversation_id}"

    async def get(
        self,
        conversation_id: str,
    ) -> list[ChatCompletionMessageParam] | None:
        key = self._key(conversation_id)

        data = await self._redis.get(key)

        if data is None:
            return None

        if isinstance(data, bytes):
            data = data.decode("utf-8")

        messages = json.loads(data)

        return cast(
            list[ChatCompletionMessageParam],
            messages,
        )

    async def save(
        self,
        conversation_id: str,
        messages: list[ChatCompletionMessageParam],
    ) -> None:
        key = self._key(conversation_id)

        data = json.dumps(
            messages,
            ensure_ascii=False,
        )

        await self._redis.set(
            key,
            data,
            ex=self._ttl_seconds,
        )

    async def delete(
        self,
        conversation_id: str,
    ) -> None:
        key = self._key(conversation_id)

        await self._redis.delete(key)
