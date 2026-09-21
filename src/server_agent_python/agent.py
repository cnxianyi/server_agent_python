"""Agent 核心循环。 / Agent core loop."""

import json

from loguru import logger
from openai.types.chat import ChatCompletionMessageParam

from server_agent_python.conversation.store import ConversationStore

from .llm import LLMClient
from .tools.errors import ToolExecutionError
from .tools.registry import (
    TOOL_DEFINITIONS,
    TOOL_HANDLERS,
)

# 最大循环次数
MAX_LOOP = 10

# 最大会话保存轮数
MAX_CONVERSATION_TURNS = 3


async def run_agent(
    llm: LLMClient,
    store: ConversationStore,
    conversation_id: str,
    user_content: str,
) -> str:
    messages = await store.get(conversation_id)

    # 如果内存会话id不存在.初始化 developer
    if messages is None:
        # 明确类型初始化变量
        initial_messages: list[ChatCompletionMessageParam] = [
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
            }
        ]

        messages = initial_messages

    # 插入 user 会话内容
    messages.append(
        {
            "role": "user",
            "content": user_content,
        }
    )

    user_indexes: list[int] = []
    for index, c in enumerate(messages):
        if c["role"] == "user":
            user_indexes.append(index)

    # 开始裁剪
    if len(user_indexes) > MAX_CONVERSATION_TURNS:
        # 最近的MAX_CONVERSATION_TURNS user位置
        start_index = user_indexes[-MAX_CONVERSATION_TURNS]
        # developer
        developer_message = messages[0]

        messages[:] = [  # [:] 直接替换原引用地址
            developer_message,
            *messages[start_index:],  # * 类似js的 ... 展开
        ]

    await store.save(
        conversation_id,
        messages,
    )

    for step in range(1, MAX_LOOP + 1):
        logger.info("第 {} 轮调用 LLM：{}", step, messages)

        response = await llm.chat(
            messages,
            tools=TOOL_DEFINITIONS,
        )

        logger.info("第 {} 轮调用结果：{}", step, response)

        if response.error is not None:
            return response.error

        if response.message is None:
            return "LLM returned no message"

        # AI 没有选择调用 Tool，直接返回最终文本
        if not response.message.tool_calls:
            content = response.message.content or ""

            # AI助手回复的
            messages.append(
                {
                    "role": "assistant",
                    "content": content,
                }
            )

            await store.save(
                conversation_id,
                messages,
            )

            return content

        # 只处理 function 类型的 tool call
        function_tool_calls = [
            tool_call  # 需要保留的tool_call
            # 临时的tool_call进行判断
            for tool_call in response.message.tool_calls
            if tool_call.type == "function"
        ]

        # print(function_tool_calls[0].function.arguments)

        if not function_tool_calls:
            return "LLM returned unsupported tool call type"

        # 把 LLM 的 Tool Call 放回对话历史
        messages.append(
            {
                "role": "assistant",
                "content": response.message.content,
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

            else:  # try成功后执行
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

        await store.save(conversation_id, messages)

        logger.info(
            "第 {} 轮 Tool 执行完成，准备下一轮：{}",
            step,
            messages,
        )

    raise RuntimeError("Agent exceeded maximum loop count")
