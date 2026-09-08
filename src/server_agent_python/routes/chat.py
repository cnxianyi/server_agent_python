"""聊天路由。 / Chat routes."""

from fastapi import APIRouter, Request

from server_agent_python.agent import run_agent
from server_agent_python.tools.disk_usage import DISK_USAGE_TOOL

from ..config import Settings
from ..llm import LLMClient

from openai.types.chat import (
    ChatCompletionMessageParam,
    ChatCompletionToolParam,
)

router = APIRouter()


@router.get("/chat")
async def chat(
    request: Request,
    content: str,
) -> dict[str, str]:

    settings: Settings = request.app.state.settings
    llm = LLMClient(settings)

    result = await run_agent(
        llm,
        content,
    )

    return {
        "message": result,
    }
