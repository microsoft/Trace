import os
from opto.trace.bundle import bundle, ExecutionError
from opto.trace.nodes import Node, node, ExceptionNode
from opto.trace.utils import for_all_methods
from opto.trace import model
from opto.optimizers.optoprime import OptoPrime

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



## Trainable Code (Execution Error)
## Error in C code
print("\n"+"="*20)
print("Nested Execution error in trainable code:\n\n")


@bundle(trainable=True)
def top_fun(x):
    if False:
        u = [1]
    x = [u[i] for i in range(3)]
    return

try:
    top_fun(1)
except ExecutionError as e:
    print(f"Error message to developer:\n{e}")
    print("\n\n")
    print(f"Error message to optimizer:\n{e.exception_node.data}")
    assert isinstance(e.exception_node, ExceptionNode)
    assert top_fun.parameter in e.exception_node.parents


## Returning None while unpacking with multiple variables
@bundle(catch_execution_error=True)
def fun(x):
    return None

try:
    a, b = fun(1)
except ExecutionError as e:
    print(f"Error message to developer:\n{e}")
    assert isinstance(e.exception_node, ExceptionNode)

# error inside lambda functions

@bundle()
def test(a, b):
    return a(b)

def add_one(y):
    add_one_fn = lambda x: x + y + 1
    return add_one_fn

add_one_fn = add_one(2)
try:
    z = test(add_one_fn, '1')
except ExecutionError as e:
    print(f"Error message to developer:\n{e}")
    print("\n\n")
    print(f"Error message to optimizer:\n{e.exception_node.data}")
    assert isinstance(e.exception_node, ExceptionNode)

## Bundle with error
# not resolved
def test_early_exception():
    @model
    class TestAgent:
        @bundle(trainable=True)
        def func1(self):
            return 1

        @bundle(trainable=True)
        def func2(self):
            return 1

        @bundle(trainable=True)
        def func3(self):
            raise Exception("Error in func1")

        def act(self):
            self.func1()
            self.func2()
            self.func3()

    agent = TestAgent()
    try:
        output = agent.act()
    except ExecutionError as e:
        feedback = e.exception_node.create_feedback()
        output = e.exception_node

    optimizer = OptoPrime(agent.parameters())
    optimizer.zero_feedback()
    optimizer.backward(output, feedback)
    optimizer.summarize()

if os.path.exists("OAI_CONFIG_LIST"):
    test_early_exception()
