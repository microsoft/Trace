from opto.trace.modules import Module, model, Map, Seq
from opto.trace.nodes import node
from opto.trace.bundle import bundle
import os
import pickle

# Test Module as a class


class BaseModule(Module):
    def __init__(self):
        super().__init__()
        self._param = node(1, trainable=True)

    @bundle(trainable=True)
    def method1(self, x):
        return x

    def method2(self, y):
        return y

    def forward(self, i):
        return self.method1(i)


base = BaseModule()
assert len(base.parameters()) == 2
assert len(base.parameters_dict()) == 2


def dummy_method():
    return 1

# test inheritance
class ChildModule(BaseModule):
    def __init__(self):
        super().__init__()
        self._extra_param = node(1, trainable=True)
        self._extra_method = bundle(trainable=True)(dummy_method)
        self._base = BaseModule()  # ParameterContainer

    @bundle(trainable=True)
    def method1(self, x):
        return x

    def method2(self, y):
        return y

child = ChildModule()
print(child.parameters_dict().keys())
assert len(child.parameters()) == 6
assert len(child.parameters_dict()) == 5


# Test using model decorator
@model
class BaseClass:
    def __init__(self):
        super().__init__()
        self._param = node(1, trainable=True)

    @bundle(trainable=True)
    def method1(self, x):
        return x

    def method2(self, y):
        return y

    def forward(self, i):
        return self.method1(i)


base = BaseClass()
assert len(base.parameters()) == 2
assert len(base.parameters_dict()) == 2


def dummy_method():
    return 1

# test inheritance
class ChildClass(BaseClass):
    def __init__(self):
        super().__init__()
        self._extra_param = node(1, trainable=True)
        self._extra_method = bundle(trainable=True)(dummy_method)
        self._base = BaseClass()  # ParameterContainer

    @bundle(trainable=True)
    def method1(self, x):
        return x

    def method2(self, y):
        return y

child = ChildClass()
print(child.parameters_dict().keys())
assert len(child.parameters()) == 6
assert len(child.parameters_dict()) == 5


# test save and load
child._extra_param._data = 2  # simulate data changes
child._extra_method.parameter._data = "fake method" # simulate data changes
child._base._param._data = 3  # simulate data changes
child._new_param = node(1, trainable=True)  # simulate adding new parameter
assert len(child.parameters()) == 7

try:
    child.save("test.pkl")
except AttributeError:
    print("Cannot save attributes of classes created by @model decorator")
    pass

child._base = BaseModule()  # can save Modules
child._base._param._data = 3  # simulate data changes
try:
    child.save("test.pkl")
except AttributeError:
    print("Cannot save classes created by @model decorator")

# child2 = ChildClass()
# child2.load("test.pkl")
# os.remove("test.pkl")

# assert child2._extra_param == 2
# assert child2._extra_method.parameter._data == "fake method"
# assert child2._base._param._data == 3
# assert child2._new_param == 1 # simulate new parameter

# test if List/Dict/Tuple type ParameterContainer can be pickled and loaded
a = Map({"a": 1, "b": 2})
pickle.dump(a, open("test.pkl", "wb"))
b = pickle.load(open("test.pkl", "rb"))
os.remove("test.pkl")
assert a == b

a = Seq([1, 2, 3])
pickle.dump(a, open("test.pkl", "wb"))
b = pickle.load(open("test.pkl", "rb"))
os.remove("test.pkl")
assert a == b

a = Map({"a": 1, "b": node(2)})
pickle.dump(a, open("test.pkl", "wb"))
b = pickle.load(open("test.pkl", "rb"))
os.remove("test.pkl")
assert a == b

a = Seq([1, 2, node(3)])
pickle.dump(a, open("test.pkl", "wb"))
b = pickle.load(open("test.pkl", "rb"))
os.remove("test.pkl")
assert a == b

# test nested parameter retrieval
a = Seq([1, 2, Seq(3,4,5)])
assert a.parameters() == [], "Seq itself is not a parameter node"

a = Seq([1, node(2, trainable=True), Seq(3,node(4, trainable=True),5)])
assert len(a.parameters()) == 2, "Seq contains 2 parameters"

# both key and value could be parameter nodes
a = Map({"a": 1, "b": node(2, trainable=True), node('c', trainable=True): 3})
assert len(a.parameters()) == 2, "Map contains 2 parameters"

# mix and match of Seq and Map
a = Map({"a": 1, "b": node(2, trainable=True), "c": Seq(3,node(4, trainable=True),5)})
assert len(a.parameters()) == 2, "Map contains 2 parameters"