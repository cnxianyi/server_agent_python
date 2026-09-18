"""工具层异常。 / Tool-layer exceptions."""


class ToolExecutionError(RuntimeError):
    """工具执行失败，但可以安全反馈给模型。"""
