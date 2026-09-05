from opto.trace import node, bundle
from opto.trace.broadcast import apply_op
from opto.trace.containers import NodeContainer
import opto.trace.operators as ops


class SubContainer(NodeContainer):
    def __init__(self, y):
        self.y = node(y)


class Container(NodeContainer):
    def __init__(self, x, v):
        self.x = node(x)
        self.list_x = [node(x + "1"), node(x + "2")]
        self.dict_x = dict(v=v, x=[node(x + "1"), node(x + "2")])
        self.sub_x = SubContainer(x)


foo = Container("foo", 1)
bar = Container("bar", 2)

# foobar = copy.deepcopy(foo)
foobar = Container("not_foobar", 3)
foobar2 = apply_op(ops.add, foobar, foo, bar)

assert foobar == foobar2  # no copy is created in the process
assert foobar.x.data == "foobar"
assert foo.x in foobar.x.parents and bar.x in foobar.x.parents
assert foobar.list_x[0].data == "foo1bar1"
assert foobar.list_x[1].data == "foo2bar2"
assert foobar.dict_x["v"] == 3
assert foobar.dict_x["x"][0].data == "foo1bar1"
assert foobar.dict_x["x"][1].data == "foo2bar2"
assert foobar.sub_x.y.data == "foobar"


# Test list and dict
foobar = apply_op(lambda *args: list(args), foobar, foo, bar)
assert foobar.x[0].data == "foo"
assert foobar.x[1].data == "bar"
assert foobar.dict_x["v"] == 3
assert foobar.dict_x["x"][0][0].data == "foo1"
assert foobar.dict_x["x"][0][1].data == "bar1"
assert foobar.dict_x["x"][1][0].data == "foo2"
assert foobar.dict_x["x"][1][1].data == "bar2"

foobar = apply_op(dict, foobar, foo=foo, bar=bar)
assert foobar.x["foo"].data == "foo"
assert foobar.x["bar"].data == "bar"
assert foobar.dict_x["v"] == 3
assert foobar.dict_x["x"][0]["foo"].data == "foo1"
assert foobar.dict_x["x"][0]["bar"].data == "bar1"
assert foobar.dict_x["x"][1]["foo"].data == "foo2"
assert foobar.dict_x["x"][1]["bar"].data == "bar2"


# Test tuple containers
class TupleContainer(NodeContainer):
    def __init__(self, x):
        self.tuple_x = (node(x + "1"), node(x + "2"))


foo_tuple = (node("foo1"), node("foo2"))
bar_tuple = (node("bar1"), node("bar2"))
out_tuple = apply_op(ops.add, (node("seed1"), node("seed2")), foo_tuple, bar_tuple)
assert isinstance(out_tuple, tuple)
assert out_tuple[0].data == "foo1bar1"
assert out_tuple[1].data == "foo2bar2"
assert foo_tuple[0] in out_tuple[0].parents and bar_tuple[0] in out_tuple[0].parents

# A tuple nested inside a NodeContainer is replaced by the new tuple
foo_tc, bar_tc = TupleContainer("foo"), TupleContainer("bar")
out_tc = apply_op(ops.add, TupleContainer("seed"), foo_tc, bar_tc)
assert isinstance(out_tc.tuple_x, tuple)
assert out_tc.tuple_x[0].data == "foo1bar1"
assert out_tc.tuple_x[1].data == "foo2bar2"

# A tuple nested in a list or a dict is likewise replaced by the new tuple
out_nested = apply_op(
    ops.add,
    [(node("seed1"), node("seed2"))],
    [(node("foo1"), node("foo2"))],
    [(node("bar1"), node("bar2"))],
)
assert isinstance(out_nested[0], tuple)
assert out_nested[0][0].data == "foo1bar1"
assert out_nested[0][1].data == "foo2bar2"

out_nested = apply_op(
    ops.add,
    {"k": (node("seed1"), node("seed2"))},
    {"k": (node("foo1"), node("foo2"))},
    {"k": (node("bar1"), node("bar2"))},
)
assert isinstance(out_nested["k"], tuple)
assert out_nested["k"][0].data == "foo1bar1"
assert out_nested["k"][1].data == "foo2bar2"

# A bare Node is broadcast against every element of a tuple
z = node("Z")
out_tuple = apply_op(ops.add, (node("seed1"), node("seed2")), foo_tuple, z)
assert isinstance(out_tuple, tuple)
assert out_tuple[0].data == "foo1Z"
assert out_tuple[1].data == "foo2Z"

# A list container is still updated in place
foo_list = [node("foo1"), node("foo2")]
bar_list = [node("bar1"), node("bar2")]
seed_list = [node("seed1"), node("seed2")]
out_list = apply_op(ops.add, seed_list, foo_list, bar_list)
assert out_list is seed_list
assert out_list[0].data == "foo1bar1"
assert out_list[1].data == "foo2bar2"


# Test keyword inputs against a Node-valued attribute
@bundle()
def concat(foo, bar):
    return foo + bar


foo_sub, bar_sub = SubContainer("foo"), SubContainer("bar")
out_sub = apply_op(concat, SubContainer("seed"), foo=foo_sub, bar=bar_sub)
assert out_sub.y.data == "foobar"
assert foo_sub.y in out_sub.y.parents and bar_sub.y in out_sub.y.parents

# Keyword inputs may mix bare Nodes with containers
bare = node("Z")
out_sub = apply_op(concat, SubContainer("seed"), foo=SubContainer("foo"), bar=bare)
assert out_sub.y.data == "fooZ"
assert bare in out_sub.y.parents
