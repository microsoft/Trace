from opto.trace.bundle import bundle, ExecutionError
from opto.trace.nodes import Node, node, ExceptionNode
from opto.trace.utils import for_all_methods

x = Node(1, name="node_x")
y = Node(0, name="node_y")


# Invalid input values
def bug_program(x: Node, y: Node):
    z = x / y
    return z


try:
    bug_program(x, y)
except ExecutionError as e:
    print(f"Error message to developer:\n{e}")
    print("\n\n")
    print(f"Error message to optimizer:\n{e.exception_node.data}")
    assert isinstance(e.exception_node, ExceptionNode)
    assert x in e.exception_node.parents
    assert y in e.exception_node.parents


# Decorator usage
print("\n"+"="*20)
@bundle()
def error_fun():
    x = None
    x.append(1)
    return x

try:
    error_fun()
except Exception as e:
    assert type(e) == ExecutionError
    print(f"\nError message to developer:\n{e}")
    print("\n\n")
    print(f"Error message to optimizer:\n{e.exception_node.data}")

##  inline usage
print("\n"+"="*20)
print("Inline usage:\n\n")
def error_fun():
    x = None
    x.append(1)
    return x

error_fun = bundle()(error_fun)
try:
    error_fun()
except Exception as e:
    assert type(e) == ExecutionError
    print(f"Error message to developer:\n{e}")
    print("\n\n")
    print(f"Error message to optimizer:\n{e.exception_node.data}")

# nested error
print("\n"+"="*20)
print("Hidden error:\n\n")
def error_fun():
    x = None
    x.append(1)
    return x
@bundle()
def top_fun(x):
    x += 1
    error_fun()
    return 2

try:
    top_fun(1)
except Exception as e:
    assert type(e) == ExecutionError
    print(f"Error message to developer:\n{e}")
    print("\n\n\n")
    print(f"Error message to optimizer:\n{e.exception_node.data}")


x = Node(1, name="node_x")


# Trainable Code (Syntax Error)
print("\n"+"="*20)
print("Syntax error in trainable code:\n\n")
syntax_error_code = """
def bug_progam(x):
    x = 1
    x *=2
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
    print(f"Error message to developer:\n{e}")
    print("\n\n")
    print(f"Error message to optimizer:\n{e.exception_node.data}")
    assert isinstance(e.exception_node, ExceptionNode)
    assert bug_progam.parameter in e.exception_node.parents
    assert "SyntaxError" in e.exception_node.data

## Trainable Code (Execution Error)
print("\n"+"="*20)
print("Execution error in trainable code:\n\n")

@bundle(trainable=True)
def bug_progam(x):
    x + 10
    x / 0
    return

try:
    bug_progam(1)
except ExecutionError as e:
    print(f"Error message to developer:\n{e}")
    print("\n\n")
    print(f"Error message to optimizer:\n{e.exception_node.data}")
    assert isinstance(e.exception_node, ExceptionNode)
    assert bug_progam.parameter in e.exception_node.parents



## Trainable Code (Execution Error)
print("\n"+"="*20)
print("Nested Execution error in trainable code:\n\n")

def bug_progam(x):
    x + 10
    x / 0
    return

@bundle(trainable=True)
def top_fun(x):
    bug_progam(x)

try:
    top_fun(1)
except ExecutionError as e:
    print(f"Error message to developer:\n{e}")
    print("\n\n")
    print(f"Error message to optimizer:\n{e.exception_node.data}")
    assert isinstance(e.exception_node, ExceptionNode)
    assert top_fun.parameter in e.exception_node.parents