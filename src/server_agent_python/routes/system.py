"""系统路由。 / System routes."""

from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from loguru import logger
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncEngine

from ..config import Settings
from ..db import ping as ping_postgres
from ..redis_client import ping as ping_redis

router = APIRouter()


@router.get("/", tags=["system"])
async def root(request: Request) -> dict[str, str | int]:
    """返回基础服务元数据。 / Return basic service metadata."""

    settings: Settings = request.app.state.settings
    return {"name": settings.name, "environment": settings.env, "port": settings.port}


async def _check(name: str, check: Any) -> dict[str, str]:
    """执行依赖检查，但不向客户端泄露连接详情。
    / Run a dependency check without leaking connection details to clients.
    """

    try:
        await check()
    except Exception:  # noqa: BLE001 - 健康检查必须报告依赖失败 / health must report dependency failures
        logger.exception("Health check failed: {}", name)
        return {"status": "error"}
    return {"status": "ok"}


@router.get("/api/v1/health", tags=["system"])
async def health(request: Request) -> JSONResponse:
    """报告应用和依赖服务的健康状态。 / Report application and dependency health."""

    engine: AsyncEngine = request.app.state.engine
    redis_client: Redis = request.app.state.redis
    settings: Settings = request.app.state.settings

    postgres = await _check("postgres", lambda: ping_postgres(engine))
    redis = await _check("redis", lambda: ping_redis(redis_client))
    healthy = postgres["status"] == "ok" and redis["status"] == "ok"

    body = {
        "status": "ok" if healthy else "degraded",
        "environment": settings.env,
        "dependencies": {"postgres": postgres, "redis": redis},
    }
    return JSONResponse(status_code=200 if healthy else 503, content=body)
