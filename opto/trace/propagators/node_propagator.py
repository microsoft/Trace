from dataclasses import dataclass
from typing import Any, List, Dict, Tuple
from opto.trace.nodes import Node, MessageNode
from opto.trace.propagators.propagators import Propagator, AbstractFeedback
import heapq


@dataclass
class NodeFeedback(AbstractFeedback):
    """Feedback container used by NodePropagator."""

    graph: List[Node]  # a priority queue of nodes in the subgraph
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
        return NodeFeedback(graph=graph, user_feedback=user_feedback)


class NodePropagator(Propagator):
    """A propagator that collects all the nodes seen in the path."""

    def init_feedback(self, node, feedback: Any):
        return NodeFeedback(graph=[(node.level, node)], user_feedback=feedback)

    def _propagate(self, child: MessageNode):
        graph = [(p.level, p) for p in child.parents] + [(child.level, child)]
        feedback = self.aggregate(child.feedback) + NodeFeedback(graph=graph, user_feedback=None)
        assert isinstance(feedback, NodeFeedback)
        return {parent: feedback for parent in child.parents}

    def aggregate(self, feedback: Dict[Node, List[NodeFeedback]]):
        """Aggregate feedback from multiple children"""
        assert all(len(v) == 1 for v in feedback.values())
        assert all(isinstance(v[0], NodeFeedback) for v in feedback.values())
        values = [v[0] for v in feedback.values()]
        if len(values) == 0:
            return NodeFeedback(graph=[], user_feedback=None)
        elif len(values) == 1:
            return values[0]
        else:  # sum the feedbacks
            return sum(values[1:], values[0])
