from typing import List, Union, Dict
from opto.trace.nodes import Node, ParameterNode
import inspect
import functools
import pickle
import os


class NodeContainer:
    """ An identifier for a container of nodes."""
    pass

class ParameterContainer(NodeContainer):
    """ A container of parameter nodes. """

    def parameters(self) -> List[Node]:
        """ Return a list of all the parameters in the model. """
        return [v for v in self.parameters_dict().values()]

    def parameters_dict(self) -> Dict[str, Union[Node, Dict]]:
        """ Return a dictionary of all the parameters in the model, including
        both trainable and non-trainable parameters."""
        parameters = {}
        for name, attr in inspect.getmembers(self):
            if isinstance(attr, functools.partial):  # this is a class method
                method = attr.func.__self__
                if callable(method) and hasattr(method, "parameter"):
                    parameters[name] = method.parameter
            elif callable(attr) and hasattr(attr, "parameter"):  # method attribute
                parameters[name] = method.parameter
            elif isinstance(attr, ParameterNode):
                parameters[name] = attr
            elif isinstance(attr, NodeContainer):
                parameters[name] = attr.parameters_dict()

        return parameters  # include both trainable and non-trainable parameters

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
        for name, param in self.parameters_dict().items():
            assert name in loaded_data, f"Parameter {name} not found in the loaded data."
            param._data = loaded_data[name]


def model(cls):
    """
    Wrap a class with this decorator. This helps collect parameters for the optimizer.
    """
    class ModelWrapper(ParameterContainer, cls):
        pass
    return ModelWrapper


class Module(ParameterContainer):
    """ Module is a ParameterContainer which has a forward method. """

    def forward(self, *args, **kwargs):
        pass

    def __call__(self, *args, **kwargs):
        return self.forward(*args, **kwargs)
