"""会话存储。 / Conversation store."""

from abc import ABC, abstractmethod
from copy import deepcopy

from openai.types.chat import ChatCompletionMessageParam


# 使用 abstractmethod 定义抽象基类
class ConversationStore(ABC):
    """会话存储抽象接口。"""

    @abstractmethod  # 子类必须实现该接口
    async def get(
        self,
        conversation_id: str,
    ) -> list[ChatCompletionMessageParam] | None:
        """获取会话。"""

    @abstractmethod
    async def save(
        self,
        conversation_id: str,
        messages: list[ChatCompletionMessageParam],
    ) -> None:
        """保存会话。"""

    @abstractmethod
    async def delete(
        self,
        conversation_id: str,
    ) -> None:
        """删除会话。"""


# 继承ConversationStore 基类
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
