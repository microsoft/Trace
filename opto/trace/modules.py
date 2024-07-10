from typing import List, Union, Dict, Any
from collections import UserDict, UserList
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
    Wrap a class with this decorator. This helps collect parameters for the optimizer. This decorated class cannot be pickled.
    """

    class ModelWrapper(Module, cls):
        pass

    return ModelWrapper


class Module(ParameterContainer):
    """ Module is a ParameterContainer which has a forward method. """

    def forward(self, *args, **kwargs):
        raise NotImplementedError

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
