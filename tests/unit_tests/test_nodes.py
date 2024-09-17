import copy
from opto.trace import node
from opto.trace import operators as ops
from opto.trace.utils import contain


# Sum of str
x = node("NodeX")
y = node("NodeY")
z = ops.add(x=x, y=y)
print("Sum of Node[str]")
print(f" x:{x.data}\n y:{y.data}\n z:{z.data}")

assert z.data == x.data + y.data
assert x in z.parents and y in z.parents
assert z in x.children and z in y.children
for k, v in z._inputs.items():
    assert locals()[k] == v

# Join of str
x = node("NodeX")
y = node("NodeY")
z = node('+').join([x, y])
print("Join of Node[str]")
print(f" x:{x.data}\n y:{y.data}\n z:{z.data}")
assert z.data == x.data + '+' + y.data

# Sum of integers
x = node(1)
y = node(2)
z = ops.add(x, y)
print("Sum of Node[int]")
print(f" x:{x.data}\n y:{y.data}\n z:{z.data}")
assert z.data == x.data + y.data
assert x in z.parents and y in z.parents
assert z in x.children and z in y.children
for k, v in z._inputs.items():
    assert locals()[k] == v

# Condition
condition = node(True)
z = ops.cond(condition, x, y)
assert z.data == x.data if condition.data else y.data
assert x in z.parents and y in z.parents and condition in z.parents
assert z in x.children and z in y.children and z in condition.children
for k, v in z._inputs.items():
    assert locals()[k] == v

# Getitem of list of Nodes
index = node(0)
x = node([node(1), node(2), node(3)])
z = ops.getitem(x, index)
assert z == x[index]  # Test __getitem__ magic function
assert z is not x[index]  # different calls creates different nodes
assert z is not x[index]  # different calls creates different nodes
assert z.data == x.data[index.data].data
assert x in z.parents and index in z.parents
assert z in x.children and z in index.children
for k, v in z._inputs.items():
    assert locals()[k] == v

# Getitem of list
index = node(0)
x = node([1, 2, 3])
z = ops.getitem(x, index)
assert z == x[index]  # Test __getitem__ magic function
assert z.data == x.data[index.data]
assert x in z.parents and index in z.parents
assert z in x.children and z in index.children
for k, v in z._inputs.items():
    assert locals()[k] == v

# Test iterables
x = node([1, 2, 3])
for k, v in enumerate(x):
    assert v.data == x.data[k]

x = node(dict(a=1, b=2, c=3))
for k, v in x.items():
    assert v.data == x.data[k.data]

# Test copy
z_new = ops.identity(z)
z_clone = z.clone()
z_copy = copy.deepcopy(z)
assert z_new.data == z.data
assert z_clone.data == z.data
assert z_copy.data == z.data
assert contain(z_new.parents, z) and len(z_new.parents) == 1 and contain(z.children, z_new)
assert contain(z_clone.parents, z) and len(z_clone.parents) == 1 and contain(z.children, z_clone)
assert not contain(z_copy.parents, z) and len(z_copy.parents) == 0 and not contain(z.children, z_copy)


# Test magic function
x = node("NodeX")
y = node("NodeY")
z = x + y
print("Sum of Node[str]")
print(f" x:{x.data}\n y:{y.data}\n z:{z.data}")

assert z.data == x.data + y.data
assert x in z.parents and y in z.parents
assert z in x.children and z in y.children
for k, v in z._inputs.items():
    assert locals()[k] == v

# Test boolean operators
x = node(1)
y = node(2)
z = x < y
assert z.data == x.data < y.data

if z:
    print(f"z {z} is True")

# Test hash
x = node(1)
y = node(1)
assert y in [x]
assert y not in {x}
assert hash(x) != hash(y)


# Test callable node
def fun(x):
    return x + 1


fun_node = node(fun)
output = fun_node(node(2))
assert output == 3
assert len(output.parents) == 2

# Test trainable of trainable
a = []
x = node(a, trainable=True)
y = node(x, trainable=True)  # This would create a separate node, whose data is a reference to the previous one
assert x.data is y.data
x = node(a, trainable=False)
y = node(x, trainable=True)  # This would create a separate node, whose data is a reference to the previous one
assert x.data is y.data

# Test description
x = node(1, description="x")
assert x.description == "[Node] x"

y = node(1)
assert y.description == '[Node] This is a node in a computational graph.'

x = node(1, description="x", trainable=True)
assert x.description == "[ParameterNode] x"

x = node(1, trainable=True)
assert x.description == "[ParameterNode] This is a ParameterNode in a computational graph."