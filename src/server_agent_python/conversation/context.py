"""上下文管理。 / Context management."""

from openai.types.chat import ChatCompletionMessageParam


def trim_messages(
    messages: list[ChatCompletionMessageParam],
    max_turns: int = 100,
) -> list[ChatCompletionMessageParam]:
    """只保留最近 max_turns 个完整 user turn。"""

    if max_turns <= 0:
        raise ValueError("max_turns must be greater than 0")

    user_indexes: list[int] = []

    for index, message in enumerate(messages):
        if message["role"] == "user":
            user_indexes.append(index)

    # 未超过最大轮数，不裁剪
    if len(user_indexes) <= max_turns:
        return messages

    # 最近第 max_turns 个 user 的位置
    start_index = user_indexes[-max_turns]

    # developer 永远保留
    developer_message = messages[0]

    return [
        developer_message,
        *messages[start_index:],
    ]
