"""LLM 客户端。 / LLM client."""

from openai import AsyncOpenAI

from .config import Settings
from typing import Any

from openai.types.chat import (
    ChatCompletionMessageParam,
    ChatCompletionToolParam,
)


class LLMClient:
    """封装 LLM API 调用。 / Wrap LLM API calls."""

    def __init__(self, settings: Settings) -> None:
        self._model = settings.llm_model

        self._client = AsyncOpenAI(
            api_key=settings.llm_api_key,
            base_url=settings.llm_base_url,
            timeout=settings.llm_timeout,
        )

    async def chat(self, messages: list[ChatCompletionMessageParam], tools: list[ChatCompletionToolParam] | None = None):
        """发送消息并返回模型文本回复。"""
        
        kwargs = {
            "model": self._model,
            "messages": messages,  # type: ignore[arg-type]
        }
        
        if tools is not None:
            kwargs["tools"] = tools
            
        
        response = await self._client.chat.completions.create(**kwargs)

        result = response.choices[0].message

        return result
