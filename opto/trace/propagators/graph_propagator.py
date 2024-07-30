from dataclasses import dataclass
from typing import Any, List, Dict, Tuple
from opto.trace.nodes import Node, MessageNode, ParameterNode, get_op_name, IDENTITY_OPERATORS, NodeVizStyleGuideColorful
from opto.trace.propagators.propagators import Propagator, AbstractFeedback
import heapq


@dataclass
class TraceGraph(AbstractFeedback):
    """Feedback container used by GraphPropagator."""

    graph: List[Node]  # a priority queue of nodes in the subgraph, ordered from roots to leaves
    user_feedback: Any

    def __add__(self, other):
        assert not (
            self.user_feedback is None and other.user_feedback is None
        ), "One of the user feedback should not be None."
        if self.user_feedback is None or other.user_feedback is None:
            user_feedback = self.user_feedback if other.user_feedback is None else other.user_feedback
        else:  # both are not None
            assert self.user_feedback == other.user_feedback, "user feedback should be the same for all children"
            user_feedback = self.user_feedback

        other_names = [n[1].name for n in other.graph]
        complement = [
            x for x in self.graph if x[1].name not in other_names
        ]  # `in` uses __eq__ which checks the value not the identity
        graph = [x for x in heapq.merge(complement, other.graph, key=lambda x: x[0])]
        return TraceGraph(graph=graph, user_feedback=user_feedback)

    # TODO add expand
    def _itemize(self, node):
        return (node.level, node)

    def visualize(self, simple_visualization=True, reverse_plot=False, print_limit=100):
        from graphviz import Digraph

        nvsg = NodeVizStyleGuideColorful(print_limit=print_limit)

        queue = self.graph.copy()
        digraph = Digraph()

        if len(queue) == 1 and len(queue[0][1].parents) == 0:  # This is a root. Nothing to propagate
            digraph.node(queue[0][1].py_name, **nvsg.get_attrs(queue[0][1]))
            return digraph

        # traverse the list to determine the relationship between nodes
        # and add edge if there's a relationship

        # we still use queue here because only lower level node can have a parent to higher level
        while True:
            try:
                _, node = heapq.heappop(queue)
                # add the current node
                digraph.node(node.py_name, **nvsg.get_attrs(node))
                # is there a faster way to determine child/parent relationship!?
                for parent in node.parents:
                    if self._itemize(parent) in queue:
                        # if there's a parent, add an edge, otherwise no need
                        edge = (node.py_name, parent.py_name) if reverse_plot else (parent.py_name, node.py_name)
                        digraph.edge(*edge)
                        digraph.node(parent.py_name, **nvsg.get_attrs(parent))

            except IndexError:  # queue is empty
                break

        return digraph

class GraphPropagator(Propagator):
    """A propagator that collects all the nodes seen in the path."""

    def init_feedback(self, node, feedback: Any):
        return TraceGraph(graph=[(node.level, node)], user_feedback=feedback)

    def _propagate(self, child: MessageNode):
        graph = [(p.level, p) for p in child.parents]  # add the parents
        feedback = self.aggregate(child.feedback) + TraceGraph(graph=graph, user_feedback=None)
        assert isinstance(feedback, TraceGraph)

        # For including the external dependencies on parameters not visible
        # in the current graph level
        for param in child.external_dependencies:
            assert isinstance(param, ParameterNode)
            param._add_feedback(child, feedback)

        return {parent: feedback for parent in child.parents}

    def aggregate(self, feedback: Dict[Node, List[TraceGraph]]):
        """Aggregate feedback from multiple children"""
        assert all(len(v) == 1 for v in feedback.values())
        assert all(isinstance(v[0], TraceGraph) for v in feedback.values())
        values = [sum(v) for v in feedback.values()]
        if len(values) == 0:
            return TraceGraph(graph=[], user_feedback=None)
        else:
            return sum(values)
