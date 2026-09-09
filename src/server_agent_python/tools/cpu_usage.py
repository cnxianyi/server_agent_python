import psutil
from openai.types.chat import (
    ChatCompletionToolParam,
)


def get_cpu_usage() -> dict:
    freq = psutil.cpu_freq()

    return {
        "percent": psutil.cpu_percent(interval=1),
        "per_cpu_percent": psutil.cpu_percent(interval=None, percpu=True),
        "physical_cores": psutil.cpu_count(logical=False),
        "logical_cores": psutil.cpu_count(logical=True),
        "frequency_mhz": freq.current if freq else None,
        "load_average": psutil.getloadavg(),
    }


print(get_cpu_usage())


CPU_USAGE_TOOL: ChatCompletionToolParam = {
    "type": "function",
    "function": {
        "name": "get_cpu_usage",
        "description": "获取服务器CPU占用情况",
    },
}
