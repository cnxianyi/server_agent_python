"""Agent 核心循环。 / Agent core loop."""

import json

from loguru import logger
from openai.types.chat import ChatCompletionMessageParam

from .llm import LLMClient
from .tools.errors import ToolExecutionError
from .tools.registry import (
    TOOL_DEFINITIONS,
    TOOL_HANDLERS,
)


async def run_agent(
    llm: LLMClient,
    user_content: str,
) -> str:
    messages: list[ChatCompletionMessageParam] = [
        {
            "role": "developer",
            "content": """
你是一个 Linux Server Agent。

你的职责：
- 根据用户请求分析服务器状态
- 必要时主动调用提供的工具获取真实数据
- 不要猜测服务器实时状态
- 如果可以通过工具获得事实，应优先使用工具
- 工具失败时，应根据错误信息解释原因
- 不要声称执行了实际上没有执行的操作
- 最终回答应简洁，并说明关键指标
""".strip(),
        },
        {
            "role": "user",
            "content": user_content,
        },
    ]

    MAX_LOOP = 10

    for step in range(1, MAX_LOOP + 1):
        logger.info("第 {} 轮调用 LLM：{}", step, messages)

        response = await llm.chat(
            messages,
            tools=TOOL_DEFINITIONS,
        )

        logger.info("第 {} 轮调用结果：{}", step, response)

        if response.error is not None:
            return response.error

        message = response.message

        if message is None:
            return "LLM returned no message"

        # AI 没有选择调用 Tool，直接返回最终文本
        if not message.tool_calls:
            return message.content or ""

        # 只处理 function 类型的 tool call
        function_tool_calls = [
            tool_call
            for tool_call in message.tool_calls
            if tool_call.type == "function"
        ]

        if not function_tool_calls:
            return "LLM returned unsupported tool call type"

        # 把 LLM 的 Tool Call 放回对话历史
        messages.append(
            {
                "role": "assistant",
                "content": message.content,
                "tool_calls": [
                    {
                        "id": tool_call.id,
                        "type": "function",
                        "function": {
                            "name": tool_call.function.name,
                            "arguments": tool_call.function.arguments,
                        },
                    }
                    for tool_call in function_tool_calls
                ],
            }
        )

        logger.info("Tool Calls: {}", function_tool_calls)

        # 执行所有 Tool Call
        for tool_call in function_tool_calls:
            name = tool_call.function.name
            arguments: object = None

            try:
                arguments = json.loads(tool_call.function.arguments)
            except json.JSONDecodeError as exc:
                logger.warning(
                    "Tool 参数 JSON 无效: name={} error={}",
                    name,
                    exc.msg,
                )
                result = {"error": "Tool arguments must be valid JSON"}
            else:
                handler = TOOL_HANDLERS.get(name)

                if handler is None:
                    result = {
                        "error": f"Unknown tool: {name}",
                    }
                elif not isinstance(arguments, dict):
                    result = {"error": "Tool arguments must be a JSON object"}
                else:
                    try:
                        result = handler(**arguments)
                    except (ToolExecutionError, TypeError, ValueError) as exc:
                        logger.exception(
                            "Tool 执行失败: name={}",
                            name,
                        )
                        result = {
                            "error": str(exc),
                        }

            logger.info(
                "Tool 执行结果: name={} arguments={} result={}",
                name,
                arguments,
                result,
            )

            # 把 Tool 执行结果作为 Observation 加进 messages
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(
                        result,
                        ensure_ascii=False,
                    ),
                }
            )

        logger.info(
            "第 {} 轮 Tool 执行完成，准备下一轮：{}",
            step,
            messages,
        )

    raise RuntimeError("Agent exceeded maximum loop count")
