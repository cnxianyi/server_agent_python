# 继承ConversationStore 基类
from copy import deepcopy

from openai.types.chat import ChatCompletionMessageParam

from server_agent_python.conversation.store import ConversationStore


class MemoryConversationStore(ConversationStore):
    """基于内存的会话存储。"""

    def __init__(self) -> None:
        self._conversations: dict[
            str,
            list[ChatCompletionMessageParam],
        ] = {}

    async def get(
        self,
        conversation_id: str,
    ) -> list[ChatCompletionMessageParam] | None:
        messages = self._conversations.get(conversation_id)

        if messages is None:
            return None

        return deepcopy(messages)

    async def save(
        self,
        conversation_id: str,
        messages: list[ChatCompletionMessageParam],
    ) -> None:
        self._conversations[conversation_id] = deepcopy(messages)

    async def delete(
        self,
        conversation_id: str,
    ) -> None:
        self._conversations.pop(
            conversation_id,
            None,
        )
