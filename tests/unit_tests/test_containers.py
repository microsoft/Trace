from opto.trace.containers import Map, Seq
from opto.trace.nodes import node
from opto.trace.bundle import bundle
import os
import pickle

# test if List/Dict/Tuple type ParameterContainer can be pickled and loaded
a = Map({"a": 1, "b": 2})  # this is different form node of dict
pickle.dump(a, open("test.pkl", "wb"))
b = pickle.load(open("test.pkl", "rb"))
os.remove("test.pkl")
assert a == b
assert a["a"] == 1
assert a["b"] == 2
assert type(a["a"])==int

a = Seq([1, 2, 3])  # this is different form node of list
pickle.dump(a, open("test.pkl", "wb"))
b = pickle.load(open("test.pkl", "rb"))
os.remove("test.pkl")
assert a == b
assert a[0] == 1
assert a[1] == 2
assert a[2] == 3

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

# Seq, Map should have a pass-through behavior

# this should link 3 to returned value of 4
# this is work in progress..
a = node(3, trainable=True)
b = Seq([1, 2, 3, 4])
try:
    c = b[a]
except:
    pass