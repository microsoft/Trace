from opto.trace.bundle import bundle, ExecutionError
from opto.trace.nodes import Node, node, ExceptionNode
from opto.trace.utils import for_all_methods

x = Node(1, name="node_x")
y = Node(0, name="node_y")


def bug_program(x: Node, y: Node):
    z = x / y
    return z


try:
    bug_program(x, y)
except ExecutionError as e:
    print(e)
    assert isinstance(e.exception_node, ExceptionNode)
    assert x in e.exception_node.parents
    assert y in e.exception_node.parents


x = Node(1, name="node_x")

syntax_error_code = """
def bug_progam(x):
    x . 10 # syntax error
    return
"""


@bundle(trainable=True)
def bug_progam(x):
    x + 10
    return


bug_progam.parameter._data = syntax_error_code

try:
    bug_progam(1)
except ExecutionError as e:
    print(e)
    assert isinstance(e.exception_node, ExceptionNode)
    assert bug_progam.parameter in e.exception_node.parents
    assert "SyntaxError" in e.exception_node.data
