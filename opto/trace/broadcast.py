import copy

from opto.trace.containers import NodeContainer
from opto.trace.nodes import Node


def recursive_conversion(true_func, false_func):
    """Recursively apply true_func to the nodes and false_func to the rest of
    the objects in a container of nodes. Container of nodes are tuple, list,
    dict, set, and NodeContainer.

    Args:
        true_func (callable): the function to be applied to the nodes.
        false_func (callable): the function to be applied to the rest of the objects.

    """

    def func(obj):
        if isinstance(obj, Node):  # base case
            return true_func(obj)
        elif isinstance(obj, tuple):
            return tuple(func(x) for x in obj)
        elif isinstance(obj, list):
            return [func(x) for x in obj]
        elif isinstance(obj, dict):
            return {k: func(v) for k, v in obj.items()}
        elif isinstance(obj, set):
            return {func(x) for x in obj}
        elif isinstance(obj, NodeContainer):
            output = copy.copy(obj)
            for k, v in obj.__dict__.items():
                setattr(output, k, func(v))
            return output
        else:
            return false_func(obj)

    return func


# TODO to test it and clean up the code
def apply_op(op, output, *args, **kwargs):
    """A broadcasting operation that applies an op to container of Nodes.

    Args:
        op (callable): the operator to be applied.
        output (Any): the container to be updated.
        *args (Any): the positional inputs of the operator.
        **kwargs (Any): the keyword inputs of the operator.
    """

    inputs = list(args) + list(kwargs.values())
    containers = [x for x in inputs if not isinstance(x, Node)]
    if len(containers) == 0:  # all inputs are Nodes, we just apply op
        return op(*args, **kwargs)

    # # there is at least one container
    # output = copy.deepcopy(containers[0])  # this would be used as the template of the output

    def admissible_type(x, base):
        return type(x) is type(base) or isinstance(x, Node)

    assert all(
        admissible_type(x, output) for x in inputs
    )  # All inputs are either Nodes or the same type as output

    if isinstance(output, list) or isinstance(output, tuple):
        assert all(
            isinstance(x, Node) or len(output) == len(x) for x in inputs
        ), f"output {output} and inputs {inputs} are of different lengths."
        for k in range(len(output)):
            _args = [x if isinstance(x, Node) else x[k] for x in args]
            _kwargs = {
                kk: vv if isinstance(vv, Node) else vv[k] for kk, vv in kwargs.items()
            }
            output[k] = apply_op(op, output[k], *_args, **_kwargs)
        if isinstance(output, tuple):
            output = tuple(output)

    elif isinstance(output, dict):
        for k, v in output.items():
            _args = [x if isinstance(x, Node) else x[k] for x in args]
            _kwargs = {
                kk: vv if isinstance(vv, Node) else vv[k] for kk, vv in kwargs.items()
            }
            output[k] = apply_op(op, output[k], *_args, **_kwargs)

    elif isinstance(output, NodeContainer):  # this is a NodeContainer object instance
        for k, v in output.__dict__.items():
            _args = [x if isinstance(x, Node) else getattr(x, k) for x in args]
            _kwargs = {
                kk: vv if isinstance(v, Node) else getattr(vv, k)
                for kk, vv in kwargs.items()
            }
            new_v = apply_op(op, v, *_args, **_kwargs)
            setattr(output, k, new_v)
    else:
        pass
    return output
