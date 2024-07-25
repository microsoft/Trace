import copy
from opto.trace import node, bundle
from opto.trace.nodes import GRAPH, Node
from opto.trace.propagators import GraphPropagator
from opto.optimizers.optoprime import node_to_function_feedback


x = node(1, name="x", trainable=True)
y = node(1, name="y", trainable=True)
output = (x * 2 + y * 3) + 1
output.backward("test feedback")  # this uses the SumPropagator
print(x.feedback)

GRAPH.clear()

x = node(1, name="x", trainable=True)
y = node(1, name="y", trainable=True)
output = (x * 2 + y * 3) + 1


output.backward("test feedback", propagator=GraphPropagator())


print("x")
for k, v in x.feedback.items():
    v = v[0]
    print(f"user_feedback: {v.user_feedback}")
    print("graph")
    for kk, vv in v.graph:
        assert isinstance(vv, Node)
        assert vv is not y
        print(f"  {kk}: {vv}")
print()
print("y")
for k, v in y.feedback.items():
    v = v[0]
    print(f"user_feedback: {v.user_feedback}")
    print("graph")
    for kk, vv in v.graph:
        assert isinstance(vv, Node)
        assert vv is not x
        print(f"  {kk}: {vv}")


@bundle(trainable=True)
def my_fun(x):
    """Test function"""
    return x**2 + 1


x = node(-1, trainable=False)
y = my_fun(x)

y.backward("test feedback", propagator=GraphPropagator())

print("Node Feedback (my_fun)")
for k, v in my_fun.parameter.feedback.items():
    v = v[0]
    print(f"user_feedback: {v.user_feedback}")
    print("graph")
    for kk, vv in v.graph:
        assert isinstance(vv, Node)
        print(f"  {kk}: {vv}")

print("Function Feedback (my_fun)")
feedback = my_fun.parameter.feedback
for k, v in feedback.items():
    f_feedback = node_to_function_feedback(v[0])
    print("Graph:")
    for kk, vv in f_feedback.graph:
        print(f"  {kk}: {vv}")
    print("Roots:")
    for kk, vv in f_feedback.roots.items():
        print(f"  {kk}: {vv}")
    print("Others:")
    for kk, vv in f_feedback.others.items():
        print(f"  {kk}: {vv}")
    print("Documentation:")
    for kk, vv in f_feedback.documentation.items():
        print(f"  {kk}: {vv}")
    print("Output:")
    for kk, vv in f_feedback.output.items():
        print(f"  {kk}: {vv}")
    print("User Feedback:")
    print(f"  {f_feedback.user_feedback}")


# def sum_of_integers():
#     y = x.clone()
#     z = ops.add(x, y)
#     y_clone = y.clone()
#     return ops.add(z, y_clone), z


# final, z = sum_of_integers()
# final.backward("feedback")

# for k, v in x._feedback.items():
#     print(f"child {k}: {k.name}: {k.data}: {v}")
# assert " ".join([str(k) for k in x._feedback.values()]) == "['feedback'] ['feedbackfeedback']"
# print("\n")


# try:
#     z.backward("z_feedback")
# except Exception as e:
#     print("This would throw an error because z has been backwarded.")
#     print(type(e), e)
#     print("\n")

# x.zero_feedback()
# final, z = sum_of_integers()
# fig = final.backward("feedback", retain_graph=True, visualize=True, simple_visualization=False)
# fig.view()
# fig = z.backward("__extra__", visualize=True, simple_visualization=False)
# # fig.view()  # This visualizes only the subgraph before z
# for k, v in x._feedback.items():
#     print(f"child {k}: {k.name}: {k.data}: {v}")
