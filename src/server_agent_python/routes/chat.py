"""聊天路由。 / Chat routes."""

import uuid
from typing import cast

from fastapi import APIRouter, Query, Request
from redis.asyncio import Redis

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
    # cast 告诉Pylance 该对象类型为 Redis | 类似 as
    redis = cast(Redis, request.app.state.redis)

    llm = LLMClient(settings)

    if cid is None:
        cid = str(uuid.uuid4())
    conversation_id = cid

    lock_key = "conversation_lock:" + conversation_id

    lock = redis.lock(
        lock_key,
        timeout=300,
        blocking_timeout=30,
    )

    """with
        async with 会自动处理进入和退出逻辑
            如同
            await lock.acquire()
            try:
                result = await run_agent(
                    llm,
                    store,
                    conversation_id,
                    content,
                )
            finally:
                await lock.release()
        会自动运行定义好的 
            __aenter__()
            __aexit__()
    """
    async with lock:
        result = await run_agent(
            llm,
            store,
            conversation_id,
            content,
        )

    return {
        "message": result,
        "conversation_id": cid,
    }
