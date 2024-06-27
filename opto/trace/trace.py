from typing import Optional, List, Dict, Callable, Union, Type, Any, Tuple
from opto.trace.nodes import Node, GRAPH
from opto.trace.nodes import node

class stop_tracing:
    """A contextmanager to disable tracing."""

    def __enter__(self):
        GRAPH.TRACE = False

    def __exit__(self, type, value, traceback):
        GRAPH.TRACE = True
