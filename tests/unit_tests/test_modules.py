from opto.trace.modules import Module, model
from opto.trace.nodes import Node, node
from opto.trace.utils import for_all_methods
from opto.trace.bundle import bundle


# Test Module as a class


class TestClass(Module):
    @bundle(trainable=True)
    def method1(self, x):
        return x

    def method2(self, y):
        return y


@model
class TestClass2:
    @bundle(trainable=True)
    def method1(self, x):
        return x

    def method2(self, y):
        return y


def test_parameters():
    t = TestClass()
    assert len(t.parameters()) == 1
    assert len(t.parameters_dict()) == 1


test_parameters()


def test_parameters2():
    t = TestClass2()
    assert len(t.parameters()) == 1
    assert len(t.parameters_dict()) == 1


test_parameters2()
