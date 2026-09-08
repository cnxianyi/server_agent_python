"""LLM 客户端。 / LLM client."""

from openai import AsyncOpenAI

from .config import Settings


class LLMClient:
    """封装 LLM API 调用。 / Wrap LLM API calls."""

    def __init__(self, settings: Settings) -> None:
        self._model = settings.llm_model

        self._client = AsyncOpenAI(
            api_key=settings.llm_api_key,
            base_url=settings.llm_base_url,
            timeout=settings.llm_timeout,
        )

    async def chat(self, messages: list[dict[str, str]]) -> str:
        """发送消息并返回模型文本回复。"""

        response = await self._client.chat.completions.create(
            model=self._model,
            messages=messages,  # type: ignore[arg-type]
        )

        content = response.choices[0].message.content

        if content is None:
            raise RuntimeError("LLM returned no text content")

        return content
