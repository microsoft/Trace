from opto.trace import node
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
