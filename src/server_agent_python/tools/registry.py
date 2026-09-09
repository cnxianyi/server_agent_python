from collections.abc import Callable  # 这个变量/参数应该是一个可以被调用的对象
from typing import Any

from openai.types.chat import ChatCompletionToolParam

from server_agent_python.tools.cpu_usage import CPU_USAGE_TOOL, get_cpu_usage
from server_agent_python.tools.memory_usage import MEMORY_USAGE_TOOL, get_memory_usage

from .disk_usage import (
    DISK_USAGE_TOOL,
    get_disk_usage,
)

# 定义
TOOL_DEFINITIONS: list[ChatCompletionToolParam] = [
    DISK_USAGE_TOOL,
    MEMORY_USAGE_TOOL,
    CPU_USAGE_TOOL,
]

TOOL_HANDLERS: dict[str, Callable[..., Any]] = {
    "get_disk_usage": get_disk_usage,
    "get_memory_usage": get_memory_usage,
    "get_cpu_usage": get_cpu_usage,
}
