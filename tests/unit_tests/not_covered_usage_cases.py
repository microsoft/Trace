from opto.trace import node, bundle
from opto.trace.modules import apply_op
from opto.trace.modules import NodeContainer
import opto.trace.operators as ops

# ========== Case 1 ==========

"""
Not able to tracing through func_a (updating func_a's parameter)
"""


@bundle(description="[func_a] Returns a+1", trainable=True)
def func_a(a):
    return a + 1


@bundle(description="[func_b] Returns b+1", trainable=True, traceable_code=True)
def func_b(b):
    return func_a(b) + 1


def test_nested_function_visibility():
    x = node(3)
    y = func_b(x)
    fig = y.backward(visualize=True)
    fig.render()


test_nested_function_visibility()

# ========== Case 2 ==========

"""
Updating external variables
"""


@bundle(description="[func_c] Update dictionary")
def func_c(dic):
    dic["a"] = 1


def test_func_c_fail():
    dic = {}
    func_c(dic)
    assert "a" in dic, "Failed to update dictionary"


def test_func_c_succeed():
    dic = {}
    dic = node(dic)
    func_c(dic)
    assert "a" in dic, "Failed to update dictionary"


class Env(dict):
    def __init__(self, init_k, init_v):
        self[init_k] = init_v


def test_func_c_with_class_failed():
    dic = Env("c", 0)
    func_c(dic)
    assert "a" in dic, "Failed to update dictionary"


def test_func_c_with_class_success():
    dic = node(Env("c", 0))
    func_c(dic)
    assert "a" in dic, "Failed to update dictionary"
    print(dic)


# test_func_c_fail()
# test_func_c_succeed()
# test_func_c_with_class_failed()
# test_func_c_with_class_success()

# ========== Case 3 ===========
