import opto.trace as trace
from opto.trace.bundle import TraceMissingInputsError
from opto.trace.nodes import Node, node
from opto.trace.utils import for_all_methods, contain


global_var = node('This is a global variable')


def run(trainable=False):
    # Test the basic usage of bundle
    from opto.trace import bundle
    from functools import partial
    bundle = partial(bundle, trainable=trainable)


    nonlocal_var = node('This is a nonlocal variable')
    @bundle()
    def print_test():
        # Check accessibility
        print('locals\n', locals())
        print(global_var._data)
        print(nonlocal_var._data)#

    print_test()

    x = Node(1, name="node_x")
    y = Node(2, name="node_y")
    condition = Node(True)


    # Test node_dict==None
    @bundle("[auto_cond] This selects x if condition is True, otherwise y.", node_dict=None)
    def auto_cond(condition: Node, x: Node, y: Node):
        """
        A function that selects x if condition is True, otherwise y.
        """
        # You can type comments in the function body
        x, y, condition = x, y, condition  # This makes sure all data are read
        return x if condition else y


    output = auto_cond(condition, x, y)
    if not trainable:
        assert output.name.split(":")[0] == "auto_cond", output.name.split(":")[0]
    assert output._inputs[x.name] is x and output._inputs[y.name] is y and output._inputs[condition.name] is condition


    # Test node_dict=='auto'
    # here we use the signature to get the keys of message_node._inputs
    @bundle("[cond] This selects x if condition is True, otherwise y.", node_dict="auto")
    def cond(condition: Node, x: Node, y: Node):
        x, y, condition = x, y, condition  # This makes sure all data are read
        return x if condition else y


    output = cond(condition, x, y)
    if not trainable:
        assert output.name.split(":")[0] == "cond",  output.name.split(":")[0]
    assert output._inputs["x"] is x and output._inputs["y"] is y and output._inputs["condition"] is condition


    # Test dot is okay for operator name
    @bundle("[fancy.cond] This selects x if condition is True, otherwise y.", node_dict="auto")
    def fancy_cond(condition: Node, x: Node, y: Node):
        x, y, condition = x, y, condition  # This makes sure all data are read
        return x if condition else y


    output = fancy_cond(condition, x, y)
    if not trainable:
        assert output.name.split(":")[0] == "fancy.cond", output.name.split(":")[0]
    assert output._inputs["x"] is x and output._inputs["y"] is y and output._inputs["condition"] is condition


    # Test wrapping a function that returns a node
    @bundle("[add_1] Add input x and input y")
    def foo(x, y):
        z = x + y
        return z


    z = foo(x, y)
    assert z.data == 3
    if not trainable:
        assert set(z.parents) == {x, y}
    else:
        assert len(z.parents)==3


    # Test tracing class method
    class Foo:
        @bundle("[Foo.add] Add input x and input y")
        def add(self, x, y):
            z = x + y
            return z


    foo = Foo()
    z = foo.add(x, y)


    # Test composition of bundle with for all_all_methods
    @for_all_methods
    def test_cls_decorator(fun):
        def wrapper(*args, **kwargs):
            return fun(*args, **kwargs)

        return wrapper


    @test_cls_decorator
    class Foo:
        # Test automatic description generation
        @bundle()
        def add(self, x, y):
            z = x + y
            return z


    foo = Foo()
    z = foo.add(x, y)


    # Test functions with *args and *kwargs and node_dict=None
    @bundle(node_dict=None, unpack_input=False)
    def fun(a, args, kwargs, *_args, **_kwargs):
        print(a.data)
        print(args.data)
        print(kwargs.data)
        return a

    x = fun(
        node(1), node("args"), node("kwargs"), node("_args_1"), node("_args_2"), b=node("_kwargs_b"), c=node("_kwargs_c")
    )
    print(x, x.inputs)
    if not trainable:
        assert len(x.inputs) == 3
    else:
        assert len(x.inputs) == 4


    # Test functions with *args and *kwargs and node_dict='auto'
    @bundle(node_dict="auto")  # This is the default behavior
    def fun(a, args, kwargs, *_args, **_kwargs):
        print(a)
        print(args)
        print(kwargs)
        for v in _args:
            print(v)
        for k, v in _kwargs.items():
            print(v)
        return a


    x = fun(
        node(1), node("args"), node("kwargs"), node("_args_1"), node("_args_2"), b=node("_kwargs_b"), c=node("_kwargs_c")
    )
    print(x, x.inputs)


    # Test stop_tracing
    x = node(1)
    y = node(2)
    with trace.stop_tracing():
        z = x + y
    assert z.inputs == {}
    assert z == 3

    @bundle()  # Test bundle with inline comment
    def fun(a, b):  # Test bundle with inline comment
        return a + b
    assert fun(node(1), node(2)) == 3

    # Test bundle as an inline decorator
    def fun(a, b):
        return a + b

    tfun = bundle()(fun)
    assert tfun(node(1), node(2)) == 3

    tfun = bundle()(fun)  # Test inline bundle with comments
    assert tfun(node(1), node(2)) == 3


    # Test multi-output function
    @bundle(n_outputs=2)
    def fun(a, b):
        return a + b, a - b


    x, y = fun(node(1), node(2))


    @bundle()  # single output
    def fun(a, b):
        return a + b, a - b


    x_y = fun(node(1), node(2))
    assert isinstance(x_y, Node) and len(x_y) == 2
    assert isinstance(x, Node)
    assert isinstance(y, Node)

    assert x == x_y[0] and y == x_y[1]


    # Test trace codes using nodes


    @bundle(traceable_code=True)  # set unpack_input=False to run node-based codes
    def test(a: Node, b: Node):
        """Complex function."""
        return a + b + 10


    x = node(1)
    y = node(2)
    z = test(x, y)
    assert z == (x + y + 10)
    assert contain(z.parents, x) and contain(z.parents, y)
    if not trainable:
        assert "test" in z.name

    z0 = z.info["output"]  # This is the original output
    assert z == z0
    assert not contain(z0.parents, x) and not contain(z0.parents, y)
    assert "add" in z0.name


    # Test external dependencies

    external_var = node(0)


    @bundle()  # set unpack_input=False to run node-based codes
    def test(a: Node, b: Node):
        """Complex function."""
        return a + b + 10 + external_var.data


    x = node(1)
    y = node(2)
    try:
        z = test(x, y)
    except TraceMissingInputsError:
        print("This usage throws an error because external_var is not provided as part of the inputs")


    @bundle(node_dict={"x": external_var})
    def test(a: Node, b: Node):
        """Complex function."""
        return a + b + 10 + external_var.data


    z = test(x, y)
    assert z == (x + y + 10 + external_var.data)
    assert contain(z.parents, x) and contain(z.parents, y) and contain(z.parents, external_var)
    assert "a" in z.inputs and "b" in z.inputs and "x" in z.inputs


    @bundle(allow_external_dependencies=True)
    def test(a: Node, b: Node):
        """Complex function."""
        return a + b + 10 + external_var.data


    z = test(x, y)
    assert z == (x + y + 10 + external_var.data)
    assert contain(z.parents, x) and contain(z.parents, y)
    assert contain(z.info["external_dependencies"], external_var)
    assert "a" in z.inputs and "b" in z.inputs

    # Test get attribute and call


    class Foo:
        def __init__(self):
            self.node = node(1)
            self.non_node = 2

        def trace_fun(self, x: Node):
            print(x.data)
            return self.node * 2

        def non_trace_fun(self):
            return self.non_node * 2


    foo = node(Foo())
    x = node("x")
    try:
        foo.node
        foo.trace_fun()
    except AttributeError:
        print("The attribute of the wrapped object cannot be directly accessed. Instead use getattr() or call()")


    attr = foo.getattr("node")
    print(f"foo_node: {attr}\nparents {[(p.name, p.data) for p in attr.parents]}")


    attr = foo.getattr("non_node")
    print(f"non_node: {attr}\nparents {[(p.name, p.data) for p in attr.parents]}")


    fun = foo.getattr("non_trace_fun")
    y = fun()
    print(f"output: {y}\nparents {[(p.name, p.data) for p in y.parents]}")

    fun = foo.getattr("trace_fun")
    y = fun(x)

    y = foo.call("non_trace_fun")
    print(f"output: {y}\nparents {[(p.name, p.data) for p in y.parents]}")

    y = foo.call("trace_fun", x)
    print(f"output: {y}\nparents {[(p.name, p.data) for p in y.parents]}")


    class Foo:
        def __init__(self):
            self.x = node(1)

        def add(self, y):
            return y + 1 + self.x  # node


    node_F = node(Foo())
    y = node_F.getattr("x")
    assert len(y.parents) == 2
    assert "getattr" in y.name
    assert y == node_F.data.x  # value

    add = node_F.getattr("add")
    z = add(node(2))
    assert len(z.parents) == 2
    assert contain(z.parents, add)
    assert contain(z.parents[0].parents, node_F)

    z2 = node_F.call("add", 2)
    assert z2 == z
    assert contain(z2.parents[0].parents, node_F)

    z2 = node_F.call("add", node(2))
    assert z2 == z
    assert contain(z2.parents[0].parents, node_F)

    # Test recursion
    @bundle()
    def recursion(n):
        if n == 0:
            return 0
        return n + recursion(n - 1)

    output = recursion(10)
    assert output == 55, "Failed to compute recursion"
    if not trainable:
        assert len(output.parents) == 1
    else:
        assert len(output.parents) == 2

    # Test nested function visibility

    @bundle()
    def func_a(a):
        "Returns a+1"
        return a + 1


    @bundle()
    def func_b(b):
        "Returns b+1"
        return func_a(b) + 1

    y = func_b(3)
    if not trainable:
        assert len(y.parents) == 1
    else:
        assert len(y.parents) == 2
    assert y == 5


    def test_retriving_non_local_objects():

        @bundle()
        def non_local_func_a(a):
            "Returns a+1"
            return a + 1
        @bundle()
        def non_func_b(b):
            "Returns b+1"
            return non_local_func_a(b) + 1
        y = non_func_b(3)
        if not trainable:
            assert len(y.parents) == 1
        else:
            assert len(y.parents) == 2
        assert y == 5

    test_retriving_non_local_objects()




print("Running tests with trainable=False")
run(trainable=False)
print("Running tests with trainable=True")
run(trainable=True)