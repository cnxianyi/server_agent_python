"""聊天路由。 / Chat routes."""

from fastapi import APIRouter, Request

from ..config import Settings
from ..llm import LLMClient

router = APIRouter()


@router.get("/chat", tags=["system"])
async def chat(request: Request, content: str) -> dict[str, str]:
    """测试 LLM 调用。 / Test the LLM call."""

    settings: Settings = request.app.state.settings
    llm = LLMClient(settings)

    response = await llm.chat(
        [
            {
                "role": "user",
                "content": content or "回复你的模型详细版本号",
            }
        ]
    )

    return {"message": response}
