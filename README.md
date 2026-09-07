# server-agent-python

一个基于 `uv` 的 FastAPI 服务模板，包含：

- FastAPI + Uvicorn
- Loguru 日志
- SQLAlchemy 2.x 异步引擎与 `AsyncSession`（`asyncpg` 驱动）
- `redis-py` 异步客户端
- Pydantic Settings 配置

## 启动

```bash
uv sync
cp .env.example .env
docker compose up -d
uv run uvicorn server_agent_python.main:app --reload
```

访问：

- `http://127.0.0.1:9090/`
- `http://127.0.0.1:9090/api/v1/health`
- `http://127.0.0.1:9090/docs`

也可以直接运行项目脚本：

```bash
uv run server-agent-python
```

## 配置

配置见 `.env.example`，环境变量统一使用 `APP_` 前缀。数据库入口位于 `src/server_agent_python/db.py`，业务接口可以通过 `Depends(get_session)` 获取 SQLAlchemy `AsyncSession`。

## 开发检查

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
```
