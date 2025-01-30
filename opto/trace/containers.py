import inspect
from collections import UserDict, UserList
from opto.trace.nodes import ParameterNode
import functools


class NodeContainer:
    """An identifier for a container of nodes."""

    ...


def trainable_method(method):
    from opto.trace.bundle import FunModule

    if isinstance(method, FunModule):
        return method.trainable
    return False


class ParameterContainer(NodeContainer):
    """A container of parameter nodes."""

    def parameters(self):
        """Return a flattned list of all the parameters in the model's
        parameters_dict, useful for optimization."""
        parameters = []
        for k, v in self.parameters_dict().items():
            if isinstance(v, ParameterNode):
                parameters.append(v)
            elif isinstance(v, ParameterContainer):
                parameters.extend(v.parameters())
            else:
                raise ValueError("The model contains an unknown parameter type.")

        return parameters

    def parameters_dict(self):
        """Return a dictionary of all the parameters in the model, including
        both trainable and non-trainable parameters. The dict contains
        ParameterNodes or ParameterContainers.
        """
        parameters = {}
        for name, attr in inspect.getmembers(self):
            if name.startswith('__TRACE_RESERVED_'):
                # These are reserved for internal use.
                continue
            if isinstance(attr, functools.partial):  # this is a class method
                method = attr.func.__self__
                if trainable_method(method):
                    parameters[name] = method.parameter
            if trainable_method(attr):  # method attribute
                parameters[name] = attr.parameter
            elif isinstance(attr, ParameterNode):
                parameters[name] = attr
            elif isinstance(attr, ParameterContainer):
                parameters[name] = attr

        assert all(
            isinstance(v, (ParameterNode, ParameterContainer))
            for v in parameters.values()
        )

        return parameters  # include both trainable and non-trainable parameters


class Seq(UserList, ParameterContainer):
    """
    Seq is defined as having a length and an index.
    Python's list/tuple will be converted to Seq
    """

    def __init__(self, *args):
        if (
            len(args) == 1
            and hasattr(args[0], "__len__")
            and hasattr(args[0], "__getitem__")
        ):
            seq = args[0]
        else:
            seq = args
        super().__init__(initlist=seq)

    def parameters_dict(self):
        """Return a dictionary of all the parameters in the model, including
        both trainable and non-trainable parameters. The dict contains
        ParameterNodes or ParameterContainers.
        """
        parameters = {}
        for attr in self.data:
            if isinstance(attr, ParameterNode):
                parameters[attr.name] = attr
            elif isinstance(attr, ParameterContainer):
                parameters[str(attr)] = attr  # TODO: what is the name of the container?

        assert all(
            isinstance(v, (ParameterNode, ParameterContainer))
            for v in parameters.values()
        )
        return parameters


class Map(UserDict, ParameterContainer):
    """
    Map is defined as key and value
    Python's dict will be converted to Map
    """

    def __init__(self, mapping):
        super().__init__(mapping)

    def parameters_dict(self):
        """Return a dictionary of all the parameters in the model, including
        both trainable and non-trainable parameters. The dict contains
        ParameterNodes or ParameterContainers.
        """
        parameters = {}
        for k, v in self.data.items():
            if isinstance(v, ParameterNode):
                parameters[k] = v
            elif isinstance(v, ParameterContainer):
                parameters[str(v)] = v  # TODO: what is the name of the container?

            if isinstance(k, ParameterNode):
                parameters[str(k)] = k
            elif isinstance(k, ParameterContainer):
                raise Exception("The key of a Map cannot be a container.")

        assert all(
            isinstance(v, (ParameterNode, ParameterContainer))
            for v in parameters.values()
        )
        return parameters


#
