"""聊天路由。 / Chat routes."""

import uuid

from fastapi import APIRouter, Request

from server_agent_python.agent import run_agent

from ..config import Settings
from ..llm import LLMClient

router = APIRouter()


@router.get("/chat")
async def chat(
    request: Request,
    content: str,
) -> dict[str, str]:

    settings: Settings = request.app.state.settings
    llm = LLMClient(settings)
    conversation_id = str(uuid.uuid4())

    result = await run_agent(
        llm,
        conversation_id,
        content,
    )

    return {
        "message": result,
    }
