from typing import Any, List, Dict, Tuple
from opto.trace.nodes import Node, MessageNode, get_op_name


class AbstractPropagator:
    def __call__(self, child: MessageNode):
        """Calling this method would propagte the feedback from the child to the parents."""
        assert isinstance(child, MessageNode)
        assert all(
            [len(f) <= 1 for f in child.feedback.values()]
        )  # All MessageNode feedback should be at most length 1
        propagated_feedback = self.propagate(child)
        # Check propagated feedback has the right format
        # It should be a dictionary with the parents as keys and the feedback as values
        assert isinstance(propagated_feedback, dict)
        assert all((p in propagated_feedback for p in child.parents))
        return propagated_feedback

    def propagate(self, child: MessageNode) -> Dict[Node, Any]:
        """Compute propagated feedback to node.parents of a node. Return a dict where
        the keys are the parents and the values are the
        propagated feedback.
        """
        raise NotImplementedError


class AbstractFeedback:
    """Feedback container used by propagators. It needs to support addition."""

    def __add__(self, other):
        raise NotImplementedError

    def __radd__(self, other):
        if other == 0:  # for support sum
            return self
        else:
            return self.__add__(other)


class Propagator(AbstractPropagator):
    def __init__(self):
        self.override = dict()  # key: operator name: data: override propagate function

    def register(self, operator_name, propagate_function):
        self.override[operator_name] = propagate_function

    def propagate(self, child: MessageNode) -> Dict[Node, Any]:
        operator_name = get_op_name(child.description)
        if operator_name in self.override:
            return self.override[operator_name](child)
        else:
            return self._propagate(child)

    def init_feedback(self, node: Node, feedback: Any):
        """
        Given raw feedback, create the feedback object that will be propagated recursively.

        """
        raise NotImplementedError

    def _propagate(self, child: MessageNode) -> Dict[Node, Any]:
        """Compute propagated feedback to node.parents based on
        node.description, node.data, and node.feedback. Return a dict where
        the keys are the parents and the values are the
        propagated feedback.
        """
        raise NotImplementedError


# Note:
# if len(feedback) > 1, it means there are two or more child nodes from this node,
# we might need to perform a "merge" feedback action


# # TODO test
class SumPropagator(Propagator):
    def init_feedback(self, feedback: Any):
        return feedback

    def _propagate(self, child: MessageNode):
        if "user" in child.feedback:
            assert len(child.feedback) == 1, "user feedback should be the only feedback"
            assert len(child.feedback["user"]) == 1
            feedback = child.feedback["user"][0]
        else:
            # Simply sum the feedback
            feedback_list = [v[0] for k, v in child.feedback.items()]
            assert len(feedback_list) > 0
            assert all(
                [type(feedback_list[0]) is type(f) for f in feedback_list]
            ), "error in propagate"
            if isinstance(feedback_list[0], str):
                feedback = "".join(feedback_list)
            else:
                feedback = sum(feedback_list)
        return {parent: feedback for parent in child.parents}
