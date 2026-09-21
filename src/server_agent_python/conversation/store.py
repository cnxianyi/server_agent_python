"""会话存储。 / Conversation store."""

from abc import ABC, abstractmethod

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
