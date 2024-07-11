import inspect

from opto.trace.nodes import node, Node, MessageNode
from typing import TYPE_CHECKING, Any
from opto.trace.bundle import bundle, FunModule
from collections import UserDict, UserList
from opto.trace.modules import ParameterNode, ParameterContainer


# List and Tuple share an Iterable
class SeqIterable:
    def __init__(self, wrapped_list):
        self._index = 0
        self.wrapped_list = wrapped_list

    def __iter__(self):
        self._index = 0
        return self

    def __next__(self):
        if self._index < len(self.wrapped_list.data):
            result = self.wrapped_list[self._index]
            self._index += 1
            result_node = node(result)
            # I'm not sure why this is necessary
            if self.wrapped_list not in result_node.parents:
                result_node._add_parent(self.wrapped_list)
            return result_node
        else:
            raise StopIteration


@bundle("[to_list] This converts x to a list.", node_dict="auto")
def to_list_implicit(x: Any):
    return list(x)


# List[Nodes], Node[List]
def iterate(x: Any):
    if issubclass(type(x), Node):
        if type(x.data) == list or type(x.data) == tuple:
            return SeqIterable(x)
        elif type(x.data) == set:
            converted_list = to_list_implicit(x)
            return SeqIterable(converted_list)
        elif type(x.data) == dict:
            return DictIterable(x)
        else:
            raise Exception("Cannot iterate on an object of type {}".format(type(x.data)))
    elif type(x) == list or type(x) == tuple:
        return SeqIterable(node(x))
    elif type(x) == set:
        converted_list = to_list_implicit(x)
        return SeqIterable(converted_list)
    elif type(x) == dict:
        return DictIterable(node(x))
    else:
        raise Exception("Cannot iterate on an object of type {}".format(type(x)))


class DictIterable:
    def __init__(self, wrapped_dict):
        self._index = 0
        self.wrapped_dict = wrapped_dict
        self.keys = list(wrapped_dict.data.keys())

    def __iter__(self):
        self._index = 0
        return self

    def __next__(self):
        if self._index < len(self.keys):
            key = self.keys[self._index]
            result = (node(key), self.wrapped_dict[key])
            self._index += 1

            result[0]._add_parent(self.wrapped_dict)
            result[1]._add_parent(self.wrapped_dict)

            return result
        else:
            raise StopIteration


def items(x: Any):
    if type(x.data) != dict:
        return AttributeError("Cannot get items from an object of type {}".format(type(x.data)))
    return DictIterable(x)


class Seq(UserList, ParameterContainer):
    """
    Seq is defined as having a length and an index.
    Python's list/tuple will be converted to Seq
    """

    def __init__(self, *args):
        if len(args) == 1 and hasattr(args[0], "__len__") and hasattr(args[0], "__getitem__"):
            seq = args[0]
        else:
            seq = args
        super().__init__(initlist=seq)

    def parameters_dict(self):
        """ Return a dictionary of all the parameters in the model, including
        both trainable and non-trainable parameters. The dict contains
        ParameterNodes or ParameterContainers.
        """
        parameters = {}
        for attr in self.data:
            if isinstance(attr, ParameterNode):
                parameters[attr.name] = attr
            elif isinstance(attr, ParameterContainer):
                parameters[str(attr)] = attr  # TODO: what is the name of the container?

        assert all(isinstance(v, (ParameterNode, ParameterContainer)) for v in parameters.values())
        return parameters


class Map(UserDict, ParameterContainer):
    """
    Map is defined as key and value
    Python's dict will be converted to Map
    """

    def __init__(self, mapping):
        super().__init__(mapping)

    def parameters_dict(self):
        """ Return a dictionary of all the parameters in the model, including
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

        assert all(isinstance(v, (ParameterNode, ParameterContainer)) for v in parameters.values())
        return parameters
