"""Agent 核心循环。 / Agent core loop."""

import json

from loguru import logger
from openai.types.chat import ChatCompletionMessageParam

from .llm import LLMClient
from .tools.disk_usage import (
    DISK_USAGE_TOOL,
    get_disk_usage,
)


async def run_agent(
    llm: LLMClient,
    user_content: str,
) -> str:
    messages: list[ChatCompletionMessageParam] = [
        {
            "role": "user",
            "content": user_content,
        }
    ]

    MAX_LOOP = 10

    for step in range(1, MAX_LOOP):
        # 第一次调用 LLM
        logger.info("第 {} 轮调用 LLM：{}", step, messages)
        response = await llm.chat(
            messages,
            tools=[DISK_USAGE_TOOL],
        )
        logger.info("第 {} 轮调用结果：{}", step, response)

        # AI没有选择调用 Tool，直接返回文本
        if not response.tool_calls:
            return response.content or ""

        # 先把 LLM 的 tool call 放回对话历史
        messages.append(
            {
                "role": "assistant",
                "content": response.content,
                "tool_calls": [
                    {
                        "id": tool_call.id,
                        "type": "function",
                        "function": {
                            "name": tool_call.function.name,
                            "arguments": tool_call.function.arguments,
                        },
                    }
                    for tool_call in response.tool_calls
                ],
            }
        )

        """
           [ChatCompletionMessageFunctionToolCall(
               id='call_poVLdZfxHp2t326OZlTzMut7',
               function=Function(
                   arguments='{"path":"/"}',
                   name='get_disk_usage'),
                   type='function'
               )]
           """
        logger.info(response.tool_calls)

        # 执行所有 Tool Call
        for tool_call in response.tool_calls:
            name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)

            if name == "get_disk_usage":
                result = get_disk_usage(**arguments)
            else:
                result = {"error": f"Unknown tool: {name}"}

            logger.info("执行结果: {}", result)

            # 把 Tool 执行结果作为 Observation 加进 messages
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(  # 将对象转为字符串
                        result,
                        ensure_ascii=False,  # 不将中文转为类似\u78c1编码
                    ),
                }
            )
        logger.info("第 {} 轮 Tool 执行完成，准备下一轮：{}", step, messages)
        """
        [
            {'role': 'user', 'content': '检查我的磁盘'
            },
            {'role': 'assistant', 'content': None, 'tool_calls': [
                    {'id': 'call_5BeyvmMWrhyolEg3kCFViLyO', 'type': 'function', 'function': {'name': 'get_disk_usage', 'arguments': '{}'
                        }
                    }
                ]
            },
            {'role': 'tool', 'tool_call_id': 'call_5BeyvmMWrhyolEg3kCFViLyO', 'content': '{
                    "path": "/",
                    "total_bytes": 501914898432,
                    "used_bytes": 21150646272,
                    "free_bytes": 475636621312,
                    "usage_percent": 4.21
                }'
            }
        ]
        """

    raise RuntimeError("Agent exceeded maximum loop count")
