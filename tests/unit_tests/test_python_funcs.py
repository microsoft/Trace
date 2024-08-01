"""
This tests all the functions of Lisp Interpreter
To make sure things work
"""
from opto.trace.nodes import node, Node
from opto.trace import operators as ops
from opto.trace.bundle import bundle
import math


@bundle(
    description="[get_env] Return a new env inside env with params mapped to their corresponding args, and env as the new env's outer env.",
    trainable=True,
)
def get_env(params, args, env=None):
    new_env = {"_outer": env}
    for param, arg in zip(params, args):
        new_env[param] = arg
    return new_env


def test_get_env():
    env = get_env(node(["a", "b"]), node([1, 2]))
    assert isinstance(env, Node)
    assert env.data == {"_outer": None, "a": 1, "b": 2}


# import must be local, otherwise we can't lazy execute
@bundle(
    description="[get_math] Get a dictionary mapping math library function names to their functions.", trainable=True
)
def get_math():
    d = {}
    for name in dir(math):
        if name[:2] != "__":
            d[name] = getattr(math, name)
    return d


def test_empty_inputs():
    result = get_math()
    assert isinstance(result, Node)
    result.backward()

    result = get_ops()
    assert isinstance(result, Node)
    result.backward()


@bundle(
    description="[get_ops] Get a dictionary mapping math library function names to their functions.", trainable=True
)
def get_ops():
    return {
        "+": (lambda x, y: x + y),
        "-": (lambda x, y: x - y),
        "*": (lambda x, y: x * y),
        "/": (lambda x, y: x / y),
        ">": (lambda x, y: x > y),
        "<": (lambda x, y: x < y),
        ">=": (lambda x, y: x >= y),
        "<=": (lambda x, y: x <= y),
        "=": (lambda x, y: x == y),
    }


@bundle(
    description="[apply_fn_dict_key] Return the value of fn_dict_generator()[key](*args_list) in standard_env.",
    _process_inputs=False,
    trainable=True,
    catch_execution_error=False,
)
def apply_fn_dict_key(fn_dict_generator, key, args_list):
    fn_dict = fn_dict_generator()
    return fn_dict[key](*args_list)


def test_apply_fn_dict_key():
    fn_dict_generator = get_ops
    key = "+"
    args_list = node([1, 2])
    result = apply_fn_dict_key(fn_dict_generator, key, args_list)
    assert result.data == 3

    result.backward(visualize=True)


test_get_env()
test_empty_inputs()
test_apply_fn_dict_key()


@bundle(
    description="[get_simple_math] Get a dictionary mapping 'abs', 'min', 'max', 'not', 'round' to their functions.",
    trainable=True,
)
def get_simple_math():
    return {"abs": abs, "min": min, "max": max, "not": lambda x: not x, "round": round}


@bundle(
    description="[standard_env] An environment with some Scheme standard procedures. Start with an environment and update it with standard functions.",
    trainable=True,
    catch_execution_error=False,
)
def standard_env(includes=["math", "ops", "simple_math"]):
    env = {"_outer": None}
    if "math" in includes:
        env.update(get_math())
    if "ops" in includes:
        env.update(get_ops())
    if "simple_math" in includes:
        env.update(get_simple_math())
    return env


def test_standard_env():
    env = standard_env()
    assert isinstance(env, Node)


# this throws an error
test_standard_env()

try:
    # tracing recursive functions
    @bundle(trainable=True, catch_execution_error=False, _process_inputs=False)
    def recurse(dic, var):
        "Simple recursion"
        if var in dic:
            return dic[var]
        else:
            return recurse(dic["_outer"], var)

    def test_recurse():
        dic = {"_outer": {"_outer": {"_outer": None, "a": 1}, "b": 2}, "c": 3}
        result = recurse(node(dic), node("a"))
        assert result.data == 1

    test_recurse()

    @bundle(
        description="[find] Find the value of var in the innermost env where var appears.",
        trainable=True,
        catch_execution_error=False,
        _process_inputs=False,
    )
    def find(env, var):
        if var in env:
            return env[var]
        else:
            return find(env["_outer"], var)

    def test_find():
        env = get_env(node(["a", "b"]), node([1, 2]))
        result = find(env, node("a"))
        assert result.data == 1

        result = find(env, node("b"))
        assert result.data == 2

        result = find(env, node("c"))
        assert result.data == 2

except ValueError as e:
    print("Warning: This test is expected to fail.")
    print(e)
