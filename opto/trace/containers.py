from opto.trace.nodes import node, Node, MessageNode
from typing import TYPE_CHECKING, Any
from opto.trace.bundle import bundle
import opto.trace.operators as ops


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


# class ExceptionIterator:
#     def __init__(self, exception):
#         self.exception = exception
#
#     def __iter__(self):
#         return self
#
#     def __next__(self):
#         raise StopIteration
