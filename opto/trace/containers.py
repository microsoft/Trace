import inspect

from opto.trace.nodes import node, Node, MessageNode
from typing import TYPE_CHECKING, Any
from opto.trace.bundle import bundle, FunModule
from collections import UserDict, UserList
from opto.trace.modules import ParameterNode, ParameterContainer




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
#