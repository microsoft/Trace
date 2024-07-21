from opto import trace
from opto.trace import operators as ops
from opto.trace.utils import contain


# Test node of list

x = trace.node([1,2,3])
for i in x:
    assert isinstance(i, trace.Node)
    assert x in i.parents

y = trace.node((4,5,6))

x = ops.list_extend(x, y)
assert len(x) == 6
for i in range(6):
    assert i+1 in x


# Test node of dict

x = trace.node(dict(a=1, b=2, c=3))
for k,v in x.items():
    assert isinstance(k, trace.Node)
    assert isinstance(v, trace.Node)
    assert contain(k.parents[0].parents, x)
    assert contain(v.parents, x)

for i in x.keys():
    assert isinstance(i, trace.Node)
    assert contain(i.parents[0].parents, x)

for i in x.values():
    assert isinstance(i, trace.Node)
    assert contain(i.parents[0].parents, x)


# Test dict of nodes
y = {}
y.update(x)
for k, v in y.items():  # This should have the same effects as calling x.items()
    assert isinstance(k, trace.Node)
    assert isinstance(v, trace.Node)
    assert contain(k.parents[0].parents, x)
    assert contain(v.parents, x)

# Test node of dict
y = trace.node({})
# y.call('update', x)  # This is not allowed, as it will create a node of a dict of nodes which is forbidden
# Instead, we use the dict_update operator
y = ops.dict_update(y, x)  # this updates the internal data of y
for k, v in y.items():
    assert isinstance(k, trace.Node)
    assert isinstance(v, trace.Node)
    assert contain(k.parents[0].parents, y)
    assert contain(v.parents, y)
