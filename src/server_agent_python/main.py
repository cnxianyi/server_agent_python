"""FastAPI application entrypoint."""

from contextlib import asynccontextmanager
from typing import Any

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from loguru import logger
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncEngine

from .config import Settings, get_settings
from .db import create_engine, create_session_factory
from .db import ping as ping_postgres
from .log import configure_logging
from .redis_client import create_client
from .redis_client import ping as ping_redis


@asynccontextmanager
async def lifespan(application: FastAPI):
    """Create and close shared database clients with the application."""

    settings = get_settings()
    configure_logging(settings)

    engine = create_engine(settings)
    session_factory = create_session_factory(engine)
    redis_client = create_client(settings)
    application.state.settings = settings
    application.state.engine = engine
    application.state.session_factory = session_factory
    application.state.redis = redis_client

    logger.info("Application started: {} ({})", settings.name, settings.env)

    try:
        yield
    finally:
        await redis_client.aclose()
        await engine.dispose()
        logger.info("Application stopped")


app = FastAPI(
    title="Server Agent Python",
    version="0.1.0",
    description="FastAPI service with native PostgreSQL and Redis clients.",
    lifespan=lifespan,
)


@app.get("/", tags=["system"])
async def root(request: Request) -> dict[str, str|int ]:
    """Return basic service metadata."""

    settings: Settings = request.app.state.settings
    return {"name": settings.name, "environment": settings.env , "port": settings.port}


async def _check(name: str, check: Any) -> dict[str, str]:
    """Run a dependency check without leaking connection details to clients."""

    try:
        await check()
    except Exception:  # noqa: BLE001 - health must report dependency failures
        logger.exception("Health check failed: {}", name)
        return {"status": "error"}
    return {"status": "ok"}


@app.get("/api/v1/health", tags=["system"])
async def health(request: Request) -> JSONResponse:
    """Report application and dependency health."""

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


def run() -> None:
    """Run the development server through the project script."""

    settings = get_settings()

    uvicorn.run(
        "server_agent_python.main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=False,
    )
