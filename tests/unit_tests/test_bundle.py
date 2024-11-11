import opto.trace as trace
from opto.trace.bundle import TraceMissingInputsError
from opto.trace.nodes import Node, node
from opto.trace.utils import for_all_methods, contain


global_var = node('This is a global variable')
global_list = [1,2,3]


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


    # here we use the signature to get the keys of message_node._inputs
    @bundle("[cond] This selects x if condition is True, otherwise y.")
    def cond(condition: Node, x: Node, y: Node):
        x, y, condition = x, y, condition  # This makes sure all data are read
        return x if condition else y


    output = cond(condition, x, y)
    if not trainable:
        assert output.name.split(":")[0] == "cond",  output.name.split(":")[0]
    assert output._inputs["x"] is x and output._inputs["y"] is y and output._inputs["condition"] is condition


    # Test dot is okay for operator name
    @bundle("[fancy.cond] This selects x if condition is True, otherwise y.")
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


    # Test modifying class attribute
    class Foo:
        def __init__(self):
            self.x = 1

        @bundle()
        def modify_x(self):
            self.x = 2

    foo = Foo()
    foo.modify_x()
    assert foo.x == 2


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



    # Test functions with *args and *kwargs
    print("*args, **kwargs test 1")
    @bundle()  # This is the default behavior
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

    print("*args, **kwargs test 2")

    x = fun(
        node(1), 'arg1', 'kwargs', node("var_args_1"), node("var_args_2"), b=node("_kwargs_b"), c=node("_kwargs_c")
    )
    print(x, x.inputs)

    print("*args, **kwargs test 3")

    x = fun(
        node(1), 'arg1', 'kwargs', "var_args_1", node("var_args_2"), b=node("_kwargs_b"), c=node("_kwargs_c")
    )
    print(x, x.inputs)

    print("*args, **kwargs test 3")

    x = fun(
        node(1), 'arg1', 'kwargs', "var_args_1"
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



    @bundle()  # single output
    def fun(a, b):
        return a + b, a - b


    x_y = fun(node(1), node(2))
    assert isinstance(x_y, Node) and len(x_y) == 2
    assert x_y[0] == 3 and x_y[1] == -1

    # Test traceable codes using nodes


    @bundle(traceable_code=True)
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


    @bundle()
    def test(a: Node, b: Node):
        """Complex function."""
        return a + b + 10 + external_var.data


    x = node(1)
    y = node(2)
    try:
        z = test(x, y)
    except TraceMissingInputsError:
        print("This usage throws an error because external_var is not provided as part of the inputs")


    @bundle(allow_external_dependencies=True)
    def test(a: Node, b: Node):
        """Complex function."""
        return a + b + 10 + external_var.data


    z = test(x, y)
    assert z == (x + y + 10 + external_var.data)
    assert contain(z.parents, x) and contain(z.parents, y) and not contain(z.parents, external_var)
    assert "a" in z.inputs and "b" in z.inputs


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
    @bundle(overwrite_python_recursion=True)
    def recursion(n):
        if n == 0:
            return 0
        val = recursion(n - 1)
        assert not isinstance(val, Node)  # overwrite_python_recursion==True would run the original function, instead of the decorated version.
        return n + val

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

    if not trainable:
        # test modifying nonlocal and global variables
        # NOTE this does not work with trainable=True, based on function defined by exec
        nonlocal_x = 5
        @bundle()
        def modify_nonlocal():
            nonlocal nonlocal_x
            print('nonlocal', x)
            nonlocal_x = nonlocal_x + 1
        modify_nonlocal()
        assert nonlocal_x == 6

        print('before', id(global_var))
        @bundle()
        def modify_global():
            global global_var
            print('global', global_var, id(global_var))
            global_var = node(str(trainable)+'none')
        modify_global()
        print(global_var, (str(trainable)+'none'))
        assert (global_var == (str(trainable)+'none')), global_var

    # Test modifying global list
    old_len = len(global_list)
    @bundle()
    def modify_global_list():
        global_list.append(1)
    modify_global_list()
    assert len(global_list) == old_len + 1



print("Running tests with trainable=False")
run(trainable=False)
print("Running tests with trainable=True")
run(trainable=True)