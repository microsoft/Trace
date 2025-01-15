from opto import trace


@trace.model
class Model:

    @trace.bundle(trainable=True)
    def forward(self, x):
        return x + 1


m1 = Model()
m2 = Model()
try:
    assert m1.__TRACE_RESERVED_self_node != m2.__TRACE_RESERVED_self_node
except AttributeError:
    # These secrets attributes are not defined yet. They will only be defined after the bundled method is accessed.
    pass

assert len(m1.parameters()) == 1
assert len(m2.parameters()) == 1

assert m1.__TRACE_RESERVED_self_node != m2.__TRACE_RESERVED_self_node  # they are defined now

# each instance has a version different from the class' version
assert m1.forward != m2.forward
assert m1.forward != Model.forward
assert m2.forward.parameter == Model.forward.parameter == m1.forward.parameter

y1 = m1.forward(1)
y2 = m1.forward(2)

# self is not duplicated
assert m1.__TRACE_RESERVED_self_node in y1.parents
assert m1.__TRACE_RESERVED_self_node in y2.parents
assert m1.forward.parameter in y1.parents
assert m1.forward.parameter in y2.parents
assert len(y1.parents) == 3  # since it's trainable
assert len(y2.parents) == 3
