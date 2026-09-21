"""聊天路由。 / Chat routes."""

import uuid

from fastapi import APIRouter, Query, Request

from server_agent_python.agent import run_agent
from server_agent_python.conversation.store import ConversationStore

from ..config import Settings
from ..llm import LLMClient

router = APIRouter()


@router.get("/chat")
async def chat(
    request: Request,
    content: str = Query(..., min_length=1),  # 必填
    cid: str | None = None,
) -> dict[str, str]:

    settings: Settings = request.app.state.settings
    store: ConversationStore = request.app.state.store
    llm = LLMClient(settings)

    if cid is None:
        cid = str(uuid.uuid4())
    conversation_id = cid

    result = await run_agent(
        llm,
        store,
        conversation_id,
        content,
    )

    return {
        "message": result,
    }
