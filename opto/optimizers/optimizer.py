from typing import Any, List, Dict

from opto.trace.nodes import ParameterNode, Node
from opto.trace.propagators import GraphPropagator
from opto.trace.propagators.propagators import Propagator
from opto.trace.utils import sum_feedback


class AbstractOptimizer:
    """An optimizer is responsible for updating the parameters based on the feedback."""

    def __init__(self, parameters: List[ParameterNode], *args, **kwargs):
        assert type(parameters) is list
        assert all([isinstance(p, ParameterNode) for p in parameters])
        self.parameters = parameters

    def step(self):
        """Update the parameters based on the feedback."""
        raise NotImplementedError

    def zero_feedback(self):
        """Reset the feedback."""
        raise NotImplementedError

    @property
    def propagator(self):
        """Return a Propagator object that can be used to propagate feedback in backward."""
        raise NotImplementedError


class Optimizer(AbstractOptimizer):
    def __init__(self, parameters: List[ParameterNode], *args, propagator: Propagator = None, **kwargs):
        super().__init__(parameters)
        propagator = propagator if propagator is not None else self.default_propagator()
        assert isinstance(propagator, Propagator)
        self._propagator = propagator

    @property
    def propagator(self):
        return self._propagator

    @property
    def trace_graph(self):
        """ Aggregate the graphs of all the parameters. """
        return sum_feedback(self.parameters)

    def step(self, *args, **kwargs):
        update_dict = self.propose(*args, **kwargs)
        self.update(update_dict)

    def propose(self, *args, **kwargs):
        """Propose the new data of the parameters based on the feedback."""
        return self._step(*args, **kwargs)

    def update(self, update_dict: Dict[ParameterNode, Any]):
        """Update the trainable parameters given a dictionary of new data."""
        for p, d in update_dict.items():
            if p.trainable:
                p._data = d

    def zero_feedback(self):
        for p in self.parameters:
            p.zero_feedback()

    # Subclass should implement the methods below.
    def _step(self, *args, **kwargs) -> Dict[ParameterNode, Any]:
        """Return the new data of parameter nodes based on the feedback."""
        raise NotImplementedError

    def default_propagator(self):
        """Return the default Propagator object of the optimizer."""
        return GraphPropagator()

    def backward(self, node: Node, *args, **kwargs):
        """Propagate the feedback backward."""
        return node.backward(*args, propagator=self.propagator, **kwargs)
