import psutil
from openai.types.chat import (
    ChatCompletionToolParam,
)


def get_memory_usage(path: str = "/") -> dict:
    memory = psutil.virtual_memory()
    # svmem(total=16630382592, available=11173531648, percent=32.8, used=5456850944, free=226881536, active=4250357760, inactive=10552606720, buffers=198995968, cached=11215523840, shared=119271424, slab=1225199616)
    swap = psutil.swap_memory()
    # sswap(total=8589926400, used=328204288, free=8261722112, percent=3.8, sin=16400384, sout=331890688)

    return {"memory": memory, "swap": swap}


MEMORY_USAGE_TOOL: ChatCompletionToolParam = {
    "type": "function",
    "function": {
        "name": "get_memory_usage",
        "description": "获取服务器内存占用情况",
    },
}
