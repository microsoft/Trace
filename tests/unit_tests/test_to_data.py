from opto.trace.bundle import to_data
from opto.trace import node

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