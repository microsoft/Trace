from opto import trace
from copy import deepcopy

@trace.model
class Model:

    @trace.bundle(trainable=True)
    def forward(self, x):
        return x + 1


def test_case_two_models():
    m1 = Model()
    m2 = Model()

    # Make sure the parameters are different
    try:
        assert m1.__TRACE_RESERVED_self_node is not m2.__TRACE_RESERVED_self_node
    except AttributeError:
        # These secrets attributes are not defined yet. They will only be defined after the bundled method is accessed.
        pass

    # The hidden nodes are defined now
    assert len(m1.parameters()) == 1
    assert len(m2.parameters()) == 1

    # Make sure the parameters are different
    assert m1.__TRACE_RESERVED_self_node is not m2.__TRACE_RESERVED_self_node  # they are defined now
    assert m1.parameters()[0] is not m2.parameters()[0]

    # check that the reserved node is the returned parameter
    assert getattr(m1, '__TRACE_RESERVED_bundle_Model.forward').parameter is m1.parameters()[0]
    assert getattr(m2, '__TRACE_RESERVED_bundle_Model.forward').parameter is m2.parameters()[0]

    # each instance has a version different from the class' version
    assert m1.forward != m2.forward
    assert m1.forward != Model.forward
    assert m2.forward.parameter == Model.forward.parameter == m1.forward.parameter

    y1 = m1.forward(1)
    y2 = m1.forward(2)

    from opto.trace.utils import contain
    # self is not duplicated
    assert contain(y1.parents, m1.__TRACE_RESERVED_self_node)
    assert contain(y2.parents, m1.__TRACE_RESERVED_self_node)
    # assert m1.__TRACE_RESERVED_self_node in y1.parents
    # assert m1.__TRACE_RESERVED_self_node in y2.parents
    assert contain(y1.parents, m1.forward.parameter)
    assert contain(y2.parents, m1.forward.parameter)
    # assert m1.forward.parameter in y1.parents
    # assert m1.forward.parameter in y2.parents
    assert len(y1.parents) == 3  # since it's trainable
    assert len(y2.parents) == 3

def test_case_model_copy():
    m1 = Model()
    m2 = deepcopy(m1)

    # Make sure the parameters are different
    try:
        assert m1.__TRACE_RESERVED_self_node is not m2.__TRACE_RESERVED_self_node
    except AttributeError:
        # These secrets attributes are not defined yet. They will only be defined after the bundled method is accessed.
        pass

    # The hidden nodes are defined now
    assert len(m1.parameters()) == 1
    assert len(m2.parameters()) == 1

    # Make sure the parameters are different
    assert m1.__TRACE_RESERVED_self_node is not m2.__TRACE_RESERVED_self_node  # they are defined now
    assert m1.parameters()[0] is not m2.parameters()[0]

    # check that the reserved node is the returned parameter
    assert getattr(m1, '__TRACE_RESERVED_bundle_Model.forward').parameter is m1.parameters()[0]
    assert getattr(m2, '__TRACE_RESERVED_bundle_Model.forward').parameter is m2.parameters()[0]

    # each instance has a version different from the class' version
    assert m1.forward is not m2.forward
    assert m1.forward is not Model.forward
    assert m2.forward.parameter == Model.forward.parameter == m1.forward.parameter

    y1 = m1.forward(1)
    y2 = m2.forward(2)

    from opto.trace.utils import contain
    # self is not duplicated
    assert contain(y1.parents, m1.__TRACE_RESERVED_self_node)
    assert contain(y2.parents, m2.__TRACE_RESERVED_self_node)
    # assert m1.__TRACE_RESERVED_self_node in y1.parents
    # assert m1.__TRACE_RESERVED_self_node in y2.parents
    assert contain(y1.parents, m1.forward.parameter)
    assert contain(y2.parents, m2.forward.parameter)

    # assert m1.forward.parameter in y1.parents
    # assert m1.forward.parameter in y2.parents
    assert len(y1.parents) == 3  # since it's trainable
    assert len(y2.parents) == 3

def printout_deecopy_modules():
    pass

test_case_two_models()
test_case_model_copy()