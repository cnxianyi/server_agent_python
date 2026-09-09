from collections.abc import Callable  # 这个变量/参数应该是一个可以被调用的对象
from typing import Any

from openai.types.chat import ChatCompletionToolParam

from .disk_usage import (
    DISK_USAGE_TOOL,
    get_disk_usage,
)

# 定义
TOOL_DEFINITIONS: list[ChatCompletionToolParam] = [
    DISK_USAGE_TOOL,
]

TOOL_HANDLERS: dict[str, Callable[..., Any]] = {
    "get_disk_usage": get_disk_usage,
}
