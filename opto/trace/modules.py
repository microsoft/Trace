from typing import List, Union, Dict, Any
from opto.trace import node
from opto.trace.nodes import Node, ParameterNode
import inspect
import functools
import pickle
import os


class NodeContainer:
    """ An identifier for a container of nodes."""
    ...


def trainable_method(method):
    return callable(method) and hasattr(method, "parameter")


class ParameterContainer(NodeContainer):
    """ A container of parameter nodes. """

    def parameters(self):
        """ Return a flattned list of all the parameters in the model's
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
        """ Return a dictionary of all the parameters in the model, including
        both trainable and non-trainable parameters. The dict contains
        ParameterNodes or ParameterContainers.
        """
        parameters = {}
        for name, attr in inspect.getmembers(self):
            if isinstance(attr, functools.partial):  # this is a class method
                method = attr.func.__self__
                if trainable_method(method):
                    parameters[name] = method.parameter
            elif trainable_method(attr):  # method attribute
                parameters[name] = attr.parameter
            elif isinstance(attr, ParameterNode):
                parameters[name] = attr
            elif isinstance(attr, ParameterContainer):
                parameters[name] = attr

        assert all(isinstance(v, (ParameterNode, ParameterContainer)) for v in parameters.values())

        return parameters  # include both trainable and non-trainable parameters


def model(cls):
    """
    Wrap a class with this decorator. This helps collect parameters for the optimizer.
    """

    class ModelWrapper(ParameterContainer, cls):
        ...

    return ModelWrapper


class Module(ParameterContainer):
    """ Module is a ParameterContainer which has a forward method. """

    def forward(self, *args, **kwargs):
        ...

    def __call__(self, *args, **kwargs):
        return self.forward(*args, **kwargs)

    def save(self, file_name):
        """ Save the parameters of the model to a file."""
        # detect if the directory exists
        directory = os.path.dirname(file_name)
        if directory != "":
            os.makedirs(directory, exist_ok=True)
        with open(file_name, "wb") as f:
            pickle.dump(self.parameters_dict(), f)

    def load(self, file_name):
        """ Load the parameters of the model from a file."""
        with open(file_name, "rb") as f:
            loaded_data = pickle.load(f)
        self._set(loaded_data)

    def _set(self, new_parameters):
        """ Set the parameters of the model from a dictionary.
        new_parameters is a ParamterContainer or a parameter dict.
        """
        assert isinstance(new_parameters, (dict, ParameterContainer))
        if isinstance(new_parameters, ParameterContainer):
            new_parameters_dict = new_parameters.parameters_dict()
        else:
            new_parameters_dict = new_parameters  # dictionary

        parameters_dict = self.parameters_dict()

        assert all(k in new_parameters_dict for k in
                   parameters_dict.keys()), """ Not all model parameters are in the new parameters dictionary. """

        for k, v in new_parameters_dict.items():
            if k in parameters_dict:  # if the parameter exists
                assert isinstance(v, (ParameterNode, ParameterContainer))
                parameters_dict[k]._set(v)
            else:  # if the parameter does not exist
                assert k not in self.__dict__
                setattr(self, k, v)


class Seq(ParameterContainer):
    """
    Seq is defined as having a length and an index.
    """

    def __init__(self, seq):
        assert hasattr(seq, "__len__") and hasattr(seq, "__getitem__")
        self.seq = seq

    def parameters_dict(self):
        """ Return a dictionary of all the parameters in the model, including
        both trainable and non-trainable parameters. The dict contains
        ParameterNodes or ParameterContainers.
        """
        parameters = {}
        for attr in self.seq:
            if isinstance(attr, ParameterNode):
                parameters[attr.name] = attr
            elif isinstance(attr, ParameterContainer):
                parameters[str(attr)] = attr  # TODO: what is the name of the container?

        assert all(isinstance(v, (ParameterNode, ParameterContainer)) for v in parameters.values())


class Map(ParameterContainer):
    """
    Map is defined as having a length and an index.
    """

    def __init__(self, mapping):
        assert hasattr(mapping, "items")
        self.mapping = mapping

    def parameters_dict(self):
        """ Return a dictionary of all the parameters in the model, including
        both trainable and non-trainable parameters. The dict contains
        ParameterNodes or ParameterContainers.
        """
        parameters = {}
        for k, v in self.mapping.items():
            if isinstance(v, ParameterNode):
                parameters[k] = v
            elif isinstance(v, ParameterContainer):
                parameters[str(v)] = v  # TODO: what is the name of the container?

        assert all(isinstance(v, (ParameterNode, ParameterContainer)) for v in parameters.values())
        return parameters
def to_data(obj):
    """Extract the data from a node or a container of nodes."""
    # For node containers (tuple, list, dict, set, NodeContainer), we need to recursively extract the data from the nodes.
    if isinstance(obj, Node):  # base case
        return obj.data
    elif isinstance(obj, tuple):
        return tuple(to_data(x) for x in obj)
    elif isinstance(obj, list):
        return [to_data(x) for x in obj]
    elif isinstance(obj, dict):
        return {k: to_data(v) for k, v in obj.items()}
    elif isinstance(obj, set):
        return {to_data(x) for x in obj}
    elif isinstance(obj, NodeContainer):
        output = copy.copy(obj)
        for k, v in obj.__dict__.items():
            setattr(output, k, to_data(v))
        return output
    else:
        return obj
    
def wrap_node(obj):
    """Wrap a node on top of the original object"""
    # For node containers (tuple, list, dict, set, NodeContainer), we need to recursively extract the data from the nodes.
    if isinstance(obj, Node):  # base case
        return obj
    elif isinstance(obj, tuple):
        return tuple(wrap_node(x) for x in obj)
    elif isinstance(obj, list):
        return [wrap_node(x) for x in obj]
    elif isinstance(obj, dict):
        return {k: wrap_node(v) for k, v in obj.items()}
    elif isinstance(obj, set):
        return {wrap_node(x) for x in obj}
    elif isinstance(obj, NodeContainer):
        output = copy.copy(obj)
        for k, v in obj.__dict__.items():
            setattr(output, k, wrap_node(v))
        return output
    else:
        return node(obj)
    
def detach_inputs(obj):
    """Detach a node or a container of nodes."""
    # For node containers (tuple, list, dict, set, NodeContainer), we need to recursively extract the data from the nodes.
    if isinstance(obj, Node):  # base case
        return obj.detach()
    elif isinstance(obj, tuple):
        return tuple(detach_inputs(x) for x in obj)
    elif isinstance(obj, list):
        return [detach_inputs(x) for x in obj]
    elif isinstance(obj, dict):
        return {k: detach_inputs(v) for k, v in obj.items()}
    elif isinstance(obj, set):
        return {detach_inputs(x) for x in obj}
    elif isinstance(obj, NodeContainer):
        output = copy.copy(obj)
        for k, v in obj.__dict__.items():
            setattr(output, k, detach_inputs(v))
        return output
    else:
        return obj

