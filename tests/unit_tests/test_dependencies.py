from opto.trace import node, bundle
from opto.trace.utils import contain, sum_feedback

# x = node(1, name="node_x")
# y = node(2, name="node_y")
# a = x + y
# b = x + 1
# final = a + b

# final.backward(visualize=True)
# fig = final.backward(visualize=True)
# fig.view()

x = node(1., trainable=True)
y = node(2.)
z = x**y + (x*x*x*x) + 0.5

assert len(z.parameter_dependencies) == 1
assert contain(z.parameter_dependencies, x)
assert not contain(z.parameter_dependencies, y)



###

x = node(1., trainable=True)
hidden_param = node(-15., trainable=True)

@bundle()
def inner_function(x):
    return x**2 + hidden_param


@bundle(traceable_code=True)
def outer_function(x):
    return inner_function(x) + 1 + hidden_param



output = outer_function(x)

assert len(output.parameter_dependencies) == 1
assert contain(output.parameter_dependencies, x)
assert not contain(output.parameter_dependencies, hidden_param)
assert len(output.expandable_dependencies) == 1
assert contain(output.expandable_dependencies, output)

print(x)

output.backward('feedback', visualize=True)
g = sum_feedback([x])
sg, fig = g.expand(output, visualize=True)
sg.visualize()