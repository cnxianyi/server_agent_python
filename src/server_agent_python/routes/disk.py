"""聊天路由。 / Disk routes."""

from fastapi import APIRouter, Request

from server_agent_python.agent import run_agent

from ..config import Settings
from ..llm import LLMClient

router = APIRouter()


@router.get("/disk")
async def disk(
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
