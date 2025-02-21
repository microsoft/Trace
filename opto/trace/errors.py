from opto.trace.nodes import ExceptionNode


class ExecutionError(Exception):
    """Base class for execution error in code tracing."""

    def __init__(self, exception_node: ExceptionNode):
        self.exception_node = exception_node
        super().__init__(self.exception_node.data)

    def __str__(self):
        return "\n\n" + self.exception_node.info["traceback"]  # show full traceback


class TraceMissingInputsError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message  # f"TraceMissingInputsError: {self.message}"
