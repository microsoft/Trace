from opto.trace.modules import to_data, Module
from opto.trace.nodes import Node, node
from opto.trace.utils import for_all_methods
from opto.trace.bundle import bundle, trace_class


def simple_test_unnested():
    a = node(1)
    to_data(a)

    a = node({"2": 2})
    to_data(a)

    a = node([1, 2, 3])
    to_data(a)


def simple_test_node_over_container():
    a = node([node(1), node(2), node(3)])
    to_data(a)


def simple_test_container_over_node():
    a = [node(1), node(2), node(3)]
    to_data(a)


def test_container_over_container_over_node():
    # currently fails, and we don't expect this to work
    a = ({node(1): node("1")},)
    to_data(a)


def test_node_over_container_over_container_over_node():
    # currently fails
    a = node(({node(1): node("1")},))
    to_data(a)


# test_container_over_container_over_node()

test_node_over_container_over_container_over_node()
simple_test_unnested()
simple_test_node_over_container()
simple_test_container_over_node()

# Test Module as a class


class TestClass(Module):
    @bundle(trainable=True)
    def method1(self, x):
        return x

    def method2(self, y):
        return y


@trace_class
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
