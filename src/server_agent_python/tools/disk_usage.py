import shutil

from openai.types.chat import (
    ChatCompletionToolParam,
)


def get_disk_usage(path: str = "/") -> dict:
    usage = shutil.disk_usage(path)

    # {'path': '/', 'total_bytes': 501914898432, 'used_bytes': 21147795456, 'free_bytes': 475639472128, 'usage_percent': 4.21}
    return {
        "path": path,
        "total_bytes": usage.total,
        "used_bytes": usage.used,
        "free_bytes": usage.free,
        "usage_percent": round(
            usage.used / usage.total * 100,
            2,
        ),
    }


DISK_USAGE_TOOL: ChatCompletionToolParam = {
    "type": "function",
    "function": {
        "name": "get_disk_usage",
        "description": "获取服务器指定路径所在文件系统的磁盘使用情况",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "description": "需要查询的路径，例如 / 或 /srv/ssd",
                }
            },
            "required": [],
        },
    },
}
