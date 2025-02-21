from dataclasses import dataclass
from typing import Any, List, Dict, Tuple
from opto.trace.nodes import (
    Node,
    MessageNode,
    ParameterNode,
    get_op_name,
    IDENTITY_OPERATORS,
    NodeVizStyleGuideColorful,
)
from opto.trace.propagators.propagators import Propagator, AbstractFeedback
import heapq
from opto.trace.utils import sum_feedback, contain


@dataclass
class TraceGraph(AbstractFeedback):
    """Feedback container used by GraphPropagator."""

    graph: List[
        Tuple[int, Node]
    ]  # a priority queue of nodes in the subgraph, ordered from roots to leaves
    user_feedback: Any

    def empty(self):
        return len(self.graph) == 0 and self.user_feedback is None

    def __add__(self, other):
        if self.empty() and other.empty():
            return TraceGraph(graph=[], user_feedback=None)
        # If one of them is not empty, one must contain the user feedback
        assert not (
            self.user_feedback is None and other.user_feedback is None
        ), "One of the user feedback should not be None."
        if self.user_feedback is None or other.user_feedback is None:
            user_feedback = (
                self.user_feedback
                if other.user_feedback is None
                else other.user_feedback
            )
        else:  # both are not None
            assert (
                self.user_feedback == other.user_feedback
            ), "user feedback should be the same for all children"
            user_feedback = self.user_feedback

        other_names = [id(n[1]) for n in other.graph]
        complement = [
            x for x in self.graph if id(x[1]) not in other_names
        ]  # `in` uses __eq__ which checks the value not the identity  # TODO
        graph = [x for x in heapq.merge(complement, other.graph, key=lambda x: x[0])]
        return TraceGraph(graph=graph, user_feedback=user_feedback)

    @classmethod
    def expand(cls, node: MessageNode):
        """Return the subgraph within a MessageNode."""
        assert isinstance(node, MessageNode)
        if isinstance(node.info["output"], MessageNode):
            # these are the nodes where we will collect the feedback
            roots = (
                list(node.info["output"].parameter_dependencies)
                + list(node.info["output"].expandable_dependencies)
                + node.info["inputs"]["args"]
                + [v for v in node.info["inputs"]["kwargs"].values()]
            )
            # remove old feedback, since we need to call backard again; we will restore it later
            old_feedback = {p: p._feedback for p in roots}
            for p in roots:
                p.zero_feedback()
            node.info["output"].backward("", retain_graph=True)
            subgraph = sum_feedback(roots)
            # restore the old feedback
            for p, feedback in old_feedback.items():
                p._feedback = feedback
        else:
            subgraph = TraceGraph(graph=[], user_feedback=None)
        return subgraph

    def __len__(self):
        return len(self.graph)

    def __iter__(self):
        return iter(self.graph)

    def _itemize(self, node):
        return (node.level, node)

    def visualize(self, simple_visualization=True, reverse_plot=False, print_limit=100):
        from graphviz import Digraph

        nvsg = NodeVizStyleGuideColorful(print_limit=print_limit)

        queue = sorted(self.graph, key=lambda x: x[0])  # sort by level
        digraph = Digraph()

        if (
            len(queue) == 1 and len(queue[0][1].parents) == 0
        ):  # This is a root. Nothing to propagate
            digraph.node(queue[0][1].py_name, **nvsg.get_attrs(queue[0][1]))
            return digraph

        # traverse the list to determine the relationship between nodes
        # and add edge if there's a relationship

        # we still use queue here because only lower level node can have a parent to higher level
        nodes_in_queue = set([node for level, node in queue])
        for level, node in queue:
            digraph.node(node.py_name, **nvsg.get_attrs(node))
            # is there a faster way to determine child/parent relationship!?
            if all( contain(nodes_in_queue, parent) for parent in node.parents):
                for parent in node.parents:
                    # if there's a parent, add an edge, otherwise no need
                    edge = (
                        (node.py_name, parent.py_name)
                        if reverse_plot
                        else (parent.py_name, node.py_name)
                    )
                    digraph.edge(*edge)
                    digraph.node(parent.py_name, **nvsg.get_attrs(parent))

        return digraph


class GraphPropagator(Propagator):
    """A propagator that collects all the nodes seen in the path."""

    def init_feedback(self, node, feedback: Any):
        return TraceGraph(graph=[(node.level, node)], user_feedback=feedback)

    def _propagate(self, child: MessageNode):
        graph = [(p.level, p) for p in child.parents]  # add the parents
        feedback = self.aggregate(child.feedback) + TraceGraph(
            graph=graph, user_feedback=None
        )
        assert isinstance(feedback, TraceGraph)

        # For including the external dependencies on parameters not visible
        # in the current graph level
        for param in child.hidden_dependencies:
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
