"""上下文管理。 / Context management."""

import json

import tiktoken
from loguru import logger
from openai.types.chat import ChatCompletionMessageParam

# GPT 新模型常用 tokenizer
ENCODING = tiktoken.get_encoding("o200k_base")


def count_message_tokens(
    messages: list[ChatCompletionMessageParam],
) -> int:
    """估算 messages 占用的 Token 数量。"""

    content = json.dumps(
        messages,
        ensure_ascii=False,
        separators=(",", ":"),
    )

    return len(ENCODING.encode(content))


def trim_messages(
    messages: list[ChatCompletionMessageParam],
    max_turns: int = 100,
    max_tokens: int = 500,
) -> list[ChatCompletionMessageParam]:
    """先按 Token 数量裁剪，再按最大会话轮数裁剪。"""

    if max_turns <= 0:
        raise ValueError("max_turns must be greater than 0")

    if max_tokens <= 0:
        raise ValueError("max_tokens must be greater than 0")

    # 创建待裁剪的 messages
    trimmed_messages = list(messages)

    # -------------------------
    # 1. 按 Token 数量裁剪
    # -------------------------
    while count_message_tokens(trimmed_messages) > max_tokens:
        user_indexes: list[int] = []

        for index, message in enumerate(trimmed_messages):
            if message["role"] == "user":
                user_indexes.append(index)

        # 只剩最后一轮 user 时停止
        # developer + 最新 user turn 必须保留
        if len(user_indexes) <= 1:
            break

        logger.info(
            "当前 tokens: {}，开始裁剪",
            count_message_tokens(trimmed_messages),
        )
        # 第二个 user 的位置
        # 从这里开始保留，相当于删除最老的一整轮
        start_index = user_indexes[1]

        developer_message = trimmed_messages[0]

        trimmed_messages = [
            developer_message,
            *trimmed_messages[start_index:],
        ]
        logger.info(
            "当前 tokens: {}，裁剪结束",
            count_message_tokens(trimmed_messages),
        )

    # -------------------------
    # 2. 按最大轮数裁剪
    # -------------------------
    user_indexes = []

    for index, message in enumerate(trimmed_messages):
        if message["role"] == "user":
            user_indexes.append(index)

    if len(user_indexes) > max_turns:
        # 最近第 max_turns 个 user 的位置
        start_index = user_indexes[-max_turns]

        developer_message = trimmed_messages[0]

        trimmed_messages = [
            developer_message,
            *trimmed_messages[start_index:],
        ]

    return trimmed_messages
