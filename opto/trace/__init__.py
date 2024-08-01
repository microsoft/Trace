from opto.trace.bundle import bundle, ExecutionError
from opto.trace.modules import Module, model
from opto.trace.containers import NodeContainer
from opto.trace.broadcast import apply_op
import opto.trace.propagators as propagators

from opto.trace.nodes import Node, GRAPH
from opto.trace.nodes import node

class stop_tracing:
    """A contextmanager to disable tracing."""

    def __enter__(self):
        GRAPH.TRACE = False

    def __exit__(self, type, value, traceback):
        GRAPH.TRACE = True


__all__ = [
    'node', 'stop_tracing', 'GRAPH', 'Node',
    'bundle', 'ExecutionError',
    'Module', 'NodeContainer', 'model',
    'apply_op',
    'propagators'
]