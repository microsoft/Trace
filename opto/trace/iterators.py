from opto.trace.nodes import node, Node
from typing import Any
from opto.trace.bundle import bundle
import opto.trace.operators as ops



# List[Nodes], Node[List]
def iterate(x: Any):
    """ Return an iterator object for node of list, tuple, set, or dict. """
    if not isinstance(x, Node):
        x = node(x)
    if issubclass(x.type, list) or issubclass(x.type, tuple):
        return SeqIterable(x)
    elif issubclass(x.type, set):
        converted_list = ops.to_list(x)
        return SeqIterable(converted_list)
    elif issubclass(x.type, dict):
        return SeqIterable(x.keys())
    else:
        raise Exception("Cannot iterate on an object of type {}".format(type(x._data)))


# List, Tuple, Set share an Iterable
class SeqIterable:
    def __init__(self, wrapped_list):
        assert isinstance(wrapped_list, Node)
        self._index = 0
        self.wrapped_list = wrapped_list

    def __iter__(self):
        self._index = 0
        return self

    def __next__(self):
        if self._index < len(self.wrapped_list._data):
            result = self.wrapped_list[self._index]
            self._index += 1
            assert isinstance(result, Node)
            assert self.wrapped_list in result.parents
            return result
        else:
            raise StopIteration


class DictIterable:
    def __init__(self, wrapped_dict):
        assert isinstance(wrapped_dict, Node)
        self._index = 0
        self.wrapped_dict = wrapped_dict
        self.keys = ops.keys(wrapped_dict)

    def __iter__(self):
        self._index = 0
        return self

    def __next__(self):
        if self._index < len(self.keys):

            key = self.keys[self._index]
            result = (key, self.wrapped_dict[key])
            self._index += 1

            assert self.wrapped_dict in result[1].parents

            return result
        else:
            raise StopIteration

class DictIterable:
    def __init__(self, wrapped_dict):
        assert isinstance(wrapped_dict, Node)
        self._index = 0
        self.wrapped_dict = wrapped_dict
        self.keys = ops.keys(wrapped_dict)

    def __iter__(self):
        self._index = 0
        return self

    def __next__(self):
        if self._index < len(self.keys):

            key = self.keys[self._index]
            result = (key, self.wrapped_dict[key])
            self._index += 1

            assert self.wrapped_dict in result[1].parents

            return result
        else:
            raise StopIteration