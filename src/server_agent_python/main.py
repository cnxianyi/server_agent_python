"""FastAPI 应用入口。 / FastAPI application entrypoint."""

from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from loguru import logger

from .config import get_settings
from .db import create_engine, create_session_factory
from .log import configure_logging
from .redis_client import create_client
from .routes.chat import router as chat_router
from .routes.system import router as system_router


# contextlib 异步上下文管理器装饰器 / contextlib async context manager decorator
@asynccontextmanager
async def lifespan(application: FastAPI):
    """随应用生命周期创建和关闭共享数据库客户端。
    / Create and close shared database clients with the application.
    """
    settings = get_settings()
    configure_logging(settings)

    # 初始化 SQLAlchemy / Initialize SQLAlchemy
    engine = create_engine(settings)
    session_factory = create_session_factory(engine)

    # 初始化 Redis / Initialize Redis
    redis_client = create_client(settings)
    application.state.settings = settings
    application.state.engine = engine
    application.state.session_factory = session_factory
    application.state.redis = redis_client

    logger.info("Application started: {} ({})", settings.name, settings.env)

    try:
        yield
    finally:
        # yield 之后：应用关闭阶段 / After yield: application shutdown phase
        await redis_client.aclose()
        await engine.dispose()
        logger.info("Application stopped")


app = FastAPI(
    title="Server Agent Python",
    version="0.1.0",
    description="FastAPI service with native PostgreSQL and Redis clients.",
    lifespan=lifespan,
)

app.include_router(system_router)
app.include_router(chat_router)


def run() -> None:
    """通过项目脚本运行开发服务器。 / Run the development server through the project script."""

    settings = get_settings()

    logger.info(settings.llm_api_key)

    uvicorn.run(
        "server_agent_python.main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=False,
    )
