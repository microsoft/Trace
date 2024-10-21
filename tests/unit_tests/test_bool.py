from opto import trace
from opto.optimizers import OptoPrime

# NOTE use Node objects in boolean expressions to have consistent behavior.

x = trace.node(True)

# test and
y = True and x  # Node
assert y == True and type(y) == trace.Node
y = x and True  # True
assert y == True and type(y) == bool
y = trace.node(True) and x  # Node
assert y == True and type(y) == trace.Node
y = x and trace.node(True)  # Node
assert y == True and type(y) == trace.Node

y = False and x  # False
assert y == False and type(y) == bool
y = x and False  # False
assert y == False and type(y) == bool
y = trace.node(False) and x  # Node
assert y == False and type(y) == trace.Node
y = x and trace.node(False)  # Node
assert y == False and type(y) == trace.Node

# test or
y = True or x  # True
assert y == True and type(y) == bool
y = x or True  # Node
assert y == True and type(y) == trace.Node
y = trace.node(True) and x  # Node
assert y == True or type(y) == trace.Node
y = x or trace.node(True)  # Node
assert y == True and type(y) == trace.Node


y = False or x  # Node
assert y == True and type(y) == trace.Node
y = x or False  # Node
assert y == True and type(y) == trace.Node
y = trace.node(False) or x  # Node
assert y == True and type(y) == trace.Node
y = x or trace.node(False)  # Node
assert y == True and type(y) == trace.Node


x = trace.node(False)

# test and

y = True and x  # Node
assert y == False and type(y) == trace.Node
y = x and True  # Node
assert y == False and type(y) == trace.Node
y = trace.node(True) and x  # Node
assert y == False and type(y) == trace.Node
y = x and trace.node(True)  # Node
assert y == False and type(y) == trace.Node

# print('\n\n')
y = False and x  # False
assert y == False and type(y) == bool
y = x and False  # Node
assert y == False and type(y) == trace.Node  # interesting
y = trace.node(False) and x  # Node
assert y == False and type(y) == trace.Node
y = x and trace.node(False)  # Node
assert y == False and type(y) == trace.Node


# test or
y = True or x  # True
assert y == True and type(y) == bool
y = x or True  # Node
assert y == True and type(y) == bool # interesting
y = trace.node(True) and x  # Node
assert y == True or type(y) == trace.Node
y = x or trace.node(True)  # Node
assert y == True and type(y) == trace.Node


y = False or x  # Node
assert y == False and type(y) == trace.Node
y = x or False  # Node
assert y == False and type(y) == bool # interesting
y = trace.node(False) or x  # Node
assert y == False and type(y) == trace.Node
y = x or trace.node(False)  # Node
assert y == False and type(y) == trace.Node