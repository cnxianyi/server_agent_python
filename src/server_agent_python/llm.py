"""LLM 客户端。 / LLM client."""

from dataclasses import dataclass

from loguru import logger
from openai import (
    APIConnectionError,
    APIStatusError,
    AsyncOpenAI,
    InternalServerError,
    RateLimitError,
)
from openai.types.chat import (
    ChatCompletionMessage,
    ChatCompletionMessageParam,
    ChatCompletionToolParam,
)

from .config import Settings


@dataclass
class LLMResult:
    message: ChatCompletionMessage | None
    error: str | None


class LLMClient:
    """封装 LLM API 调用。 / Wrap LLM API calls."""

    def __init__(self, settings: Settings) -> None:
        self._model = settings.llm_model

        self._client = AsyncOpenAI(
            api_key=settings.llm_api_key,
            base_url=settings.llm_base_url,
            timeout=settings.llm_timeout,
        )

    async def chat(
        self,
        messages: list[ChatCompletionMessageParam],
        tools: list[ChatCompletionToolParam] | None = None,
    ) -> LLMResult:
        """发送消息并返回模型消息。"""

        kwargs = {
            "model": self._model,
            "messages": messages,
        }

        err = None

        if tools is not None:
            kwargs["tools"] = tools

        try:
            response = await self._client.chat.completions.create(**kwargs)

        except RateLimitError:
            logger.exception("LLM rate limit exceeded")
            err = "LLM rate limit exceeded"

        except InternalServerError as exc:
            logger.exception(
                "LLM service unavailable: status={}",
                exc.status_code,
            )
            err = f"LLM service unavailable: HTTP {exc.status_code}"

        except APIConnectionError:
            logger.exception("Failed to connect to LLM service")
            err = "Failed to connect to LLM service"

        except APIStatusError as exc:
            logger.exception(
                "LLM API error: status={}",
                exc.status_code,
            )
            err = f"LLM API returned HTTP {exc.status_code}"

        return LLMResult(
            message=response.choices[0].message,
            error=err,
        )
