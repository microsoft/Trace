import warnings
from typing import Optional, List, Dict, Callable, Union, Type, Any
import copy
from collections import defaultdict
from typing import TypeVar, Generic
import re
from opto.trace.utils import MinHeap
from opto import trace


def node(message, name=None, trainable=False, constraint=None):
    """Create a Node from a message. If message is already a Node, return it.
    This method is for the convenience of the user, it should be used over
    directly invoking Node."""
    if trainable:
        if isinstance(message, Node):
            message = message._data
            name = name or message.name
        return ParameterNode(message, name=name, trainable=True, constraint=constraint)
    else:
        if isinstance(message, Node):
            if name is not None:
                warnings.warn(f"Name {name} is ignored because message is already a Node.")
            return message
        else:
            return Node(message, name=name, constraint=constraint)


NAME_SCOPES = []  # A stack of name scopes


class Graph:
    """This a registry of all the nodes. All the nodes form a Directed Acyclic Graph."""

    TRACE = True  # When True, we trace the graph when creating MessageNode. When False, we don't trace the graph.

    def __init__(self):
        self._nodes = defaultdict(list)  # a lookup table to find nodes by name
        # self._levels = defaultdict(list)  # a lookup table to find nodes at a certain level # TODO do we need this?

    def clear(self):
        for node in self._nodes.values():
            del node
        self._nodes = defaultdict(list)
        # self._levels = defaultdict(list)

    def register(self, node):
        assert isinstance(node, Node)
        assert len(node.name.split(":")) == 2
        name, _ = node.name.split(":")
        if len(NAME_SCOPES) > 0:
            name = NAME_SCOPES[-1] + "/" + name
        self._nodes[name].append(node)
        node._name = (
            name + ":" + str(len(self._nodes[name]) - 1)
        )  # NOTE assume elements in self._nodes never get removed.
        # self._levels[node._level].append(node)

    def get(self, name):
        name, id = name.split(":")
        return self._nodes[name][int(id)]

    @property
    def roots(self):
        return [v for vv in self._nodes.values() for v in vv if v.is_root]

    def __str__(self):
        return str(self._nodes)

    def __len__(self):
        # This is the number of nodes in the graph
        return sum([len(v) for v in self._nodes.values()])


GRAPH = Graph()  # This is a global registry of all the nodes.

USED_NODES = list()  # A stack of sets. This is a global registry to track which nodes are read.

T = TypeVar("T")


class AbstractNode(Generic[T]):
    """An abstract data node in a directed graph (parents <-- children)."""

    def __init__(self, value, *, name=None, trainable=False) -> None:
        self._parents = []
        self._children = []
        self._parameter_dependencies = set()
        self._level = 0  # roots are at level 0
        default_name = str(type(value).__name__) + ":0" if name is None else name + ":0"  # name:version
        if isinstance(value, Node):  # just a reference
            self._data = value._data
            self._name = value._name if name is None else default_name
        else:
            self._data = value
            self._name = default_name
        GRAPH.register(self)  # When created, register the node to the graph.

    @property
    def data(self):
        if len(USED_NODES) > 0 and GRAPH.TRACE:  # We're within trace_nodes context.
            USED_NODES[-1].add(self)
        return self.__getattribute__("_data")

    @property
    def parents(self):
        return self._parents

    @property
    def children(self):
        return self._children
    
    @property
    def parameter_dependencies(self):
        return self._parameter_dependencies
    

    @property
    def has_external_dependency(self):
        if self.info and isinstance(self.info['output'], Node):
            if len(self.info['output'].parameter_dependencies) > len(self.parameter_dependencies):
                return True
        return False

    @property
    def name(self):
        return self._name

    @property
    def py_name(self):
        return self.name.replace(":", "")

    @property
    def id(self):
        return self.name.split(":")[1]

    @property
    def level(self):
        return self._level

    @property
    def is_root(self):
        return len(self.parents) == 0

    @property
    def is_leaf(self):
        return len(self.children) == 0

    def _add_child(self, child):
        assert child is not self, "Cannot add self as a child."
        assert isinstance(child, Node), f"{child} is not a Node."
        child._add_parent(self)

    def _add_parent(self, parent):
        assert parent is not self, "Cannot add self as a parent."
        assert isinstance(parent, Node), f"{parent} is {type(parent)}, which is not a Node."
        parent._children.append(self)
        self._parents.append(parent)
        self._update_level(max(self._level, parent._level + 1))  # Update the level, because the parent is added


    def _add_parameter_dependencies(self, parent):
        assert parent is not self, "Cannot add self as a parent."
        assert isinstance(parent, Node), f"{parent} is {type(parent)}, which is not a Node."
        self._parameter_dependencies = self._parameter_dependencies | parent._parameter_dependencies


    def _update_level(self, new_level):
        # GRAPH._levels[self._level].remove(self)  # this uses the == operator which compares values. We need to compare references.
        self._level = new_level
        # GRAPH._levels[new_level].append(self)
        # assert all([len(GRAPH._levels[i]) > 0 for i in range(len(GRAPH._levels))]), "Some levels are empty."

    def __str__(self) -> str:
        # str(node) allows us to look up in the feedback dictionary easily
        return f"Node: ({self.name}, dtype={type(self._data)}, data={self._data})"

    def __deepcopy__(self, memo):
        """This creates a deep copy of the node, which is detached from the original graph."""
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            if k == "_parents" or k == "_children":
                setattr(result, k, [])
            else:
                setattr(result, k, copy.deepcopy(v, memo))
        return result

    def lt(self, other):
        return -self._level < -other._level

    def gt(self, other):
        return -self._level > -other._level


# TODO Update these
# These are operators that do not change the data type and can be viewed as identity operators.
IDENTITY_OPERATORS = ("identity", "clone", "message_to_dict", "oai_message")


def get_op_name(description):
    """Extract the operator type from the description."""
    match = re.search(r"^\[([^\[\]]+)\]", description)
    if match:
        operator_type = match.group(1)
        return operator_type
    else:
        raise ValueError(f"The description '{description}' must contain the operator type in square brackets.")


class Node(AbstractNode[T]):
    """A data node in a directed graph (parents <-- children)."""  # TODO update this
    def __init__(
        self,
        value: Any,
        *,
        name: str = None,
        trainable: bool = False,
        description: str = "[Node] This is a node in a computational graph.",
        constraint: Union[None, str] = None,
        info: Union[None, Dict] = None,
    ) -> None:
        super().__init__(value, name=name)
        self.trainable = trainable
        self._feedback = defaultdict(
            list
        )  # (analogous to gradient) this is the feedback from the user. Each key is a child and the value is a list of feedbacks from the child.
        self._description = description  # Information to describe of the node
        self._constraint = constraint  # A constraint on the node
        self._backwarded = False  # True if backward has been called
        self._info = info  # Additional information about the node

    def zero_feedback(self):  # set feedback to zero
        self._feedback = defaultdict(list)

    @property
    def feedback(self):
        return self._feedback

    @property
    def description(self):
        return self._description  # TODO return a textual description of the node

    @property
    def info(self):
        return self._info

    def _add_feedback(self, child, feedback):
        """Add feedback from a child."""
        self.feedback[child].append(feedback)

    def backward(
        self,
        feedback: Any = "",
        propagator=None,
        retain_graph=False,
        visualize=False,
        simple_visualization=True,
        reverse_plot=False,
        print_limit=100,
    ):
        """Backward pass.

        feedback: feedback given to the current node
        propagate: a function that takes in a node and a feedback, and returns a dict of {parent: parent_feedback}.

            def propagate(node, feedback):
                return {parent: propagated feedback for parent in node.parents}

        visualize: if True, plot the graph using graphviz
        reverse_plot: if True, plot the graph in reverse order (from child to parent).
        print_limit: the maximum number of characters to print in the graph.

        """
        if propagator is None:
            from opto.trace.propagators.node_propagator import NodePropagator  # this avoids circular import

            propagator = NodePropagator()

        # assert type(feedback) == str, f"Feedback must be a string, but got {type(feedback)}."

        # Setup for visualization
        digraph = None
        if visualize:
            from graphviz import Digraph

            digraph = Digraph()

            # using colon in the name causes problems in graphviz
            def get_label(x):
                description = x.description
                if len(x.description) > print_limit:
                    description = x.description[:print_limit] + "..."

                text = x.py_name + "\n" + description + "\n"
                content = str(x.data)
                if isinstance(x.data, dict):
                    if "content" in x.data:
                        content = str(x.data["content"])
                # content = str(x.data["content"] if isinstance(x.data, dict) else x.data)
                if len(content) > print_limit:
                    content = content[:print_limit] + "..."
                return text + content

            visited = set()

        # Check for root node with no parents
        if self._backwarded:
            raise AttributeError(f"{self} has been backwarded.")
        self._add_feedback(Node("FEEDBACK_ORACLE"), propagator.init_feedback(self, feedback))
        if len(self.parents) == 0:  # This is a root. Nothing to propagate
            if visualize:
                digraph.node(self.py_name, label=get_label(self))
            # self._backwarded = not retain_graph
            return digraph

        # TODO optimize for efficiency
        # TODO check memory leak
        # queue = [self]  # priority queue
        queue = MinHeap([self])
        while True:
            try:
                # node = heapq.heappop(queue)
                node = queue.pop()
                # Each node is a MessageNode, which has at least one parent.
                assert len(node.parents) > 0 and isinstance(node, MessageNode)
                if node._backwarded:
                    raise AttributeError(f"{node} has been backwarded.")

                # Propagate information from child to parent
                propagated_feedback = propagator(node)

                # Zero-out the feedback once it's propagated.
                # This is to ensure the feedback is not double counted when retain_graph is True.
                # node.zero_feedback()

                for parent in node.parents:
                    if parent in propagated_feedback:
                        parent._add_feedback(node, propagated_feedback[parent])
                        if parent.info and isinstance(parent.info['output'], MessageNode) and not parent.info['output']._backwarded:
                            parent.info['output'].backward(feedback=feedback,
                                                            propagator=propagator,
                                                            retain_graph=retain_graph,
                                                            visualize=visualize,
                                                            simple_visualization=simple_visualization,
                                                            reverse_plot=reverse_plot,
                                                            print_limit=print_limit,)

                    # Put parent in the queue if it has not been visited and it's not a root
                    if len(parent.parents) > 0 and parent not in queue:  # and parent not in queue:
                        # heapq.heappush(queue, parent)  # put parent in the priority queue
                        queue.push(parent)  # put parent in the priority queue

                    if visualize:
                        # Plot the edge from parent to node
                        # Bypass chain of identity operators (for better visualization)
                        while (get_op_name(parent.description) in IDENTITY_OPERATORS) and simple_visualization:
                            assert len(parent.parents) == 1  # identity operators should have only one parent
                            visited.add(parent.py_name)  # skip this node in visualization
                            parent = parent.parents[0]

                        edge = (node.py_name, parent.py_name) if reverse_plot else (parent.py_name, node.py_name)
                        # Just plot the edge once, since the same node can be
                        # visited multiple times (e.g., when that node has
                        # multiple children).
                        if edge not in visited and node.py_name not in visited:
                            digraph.edge(*edge)
                            visited.add(edge)
                            digraph.node(node.py_name, label=get_label(node))
                            digraph.node(parent.py_name, label=get_label(parent))

                node._backwarded = not retain_graph  # set backwarded to True

            except IndexError:  # queue is empty
                break
        
        if self.has_external_dependency:
            self.info['output'].backward(feedback=feedback,
                                        propagator=propagator,
                                        retain_graph=retain_graph,
                                        visualize=visualize,
                                        simple_visualization=simple_visualization,
                                        reverse_plot=reverse_plot,
                                        print_limit=print_limit,)
        
        ### This is a nested error
        elif isinstance(self.data, trace.TraceExecutionError):
            self.data.exception_node.backward(feedback=feedback,
                                propagator=propagator,
                                retain_graph=retain_graph,
                                visualize=visualize,
                                simple_visualization=simple_visualization,
                                reverse_plot=reverse_plot,
                                print_limit=print_limit,)

        return digraph

    def clone(self):
        import opto.trace.operators as ops

        return ops.clone(self)

    def detach(self):
        return copy.deepcopy(self)

    # Get attribute and call operators
    def getattr(self, key):
        import opto.trace.operators as ops

        return ops.node_getattr(self, node(key))

    def call(self, fun: str, *args, **kwargs):
        args = (node(arg) for arg in args)  # convert args to nodes
        kwargs = {k: node(v) for k, v in kwargs.items()}
        return self.getattr(fun)(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        import opto.trace.operators as ops

        output = ops.call(self, *args, **kwargs)
        return output

    # We overload magic methods that return a value. These methods return a MessageNode.
    # container magic methods
    def len(self):
        import opto.trace.operators as ops

        return ops.len_(self)

    def __getitem__(self, key):
        import opto.trace.operators as ops

        return ops.getitem(self, node(key))

    def __contains__(self, item):
        import opto.trace.operators as ops

        return ops.in_(node(item), self)

    # Unary operators and functions
    def __pos__(self):
        import opto.trace.operators as ops

        return ops.pos(self)

    def __neg__(self):
        import opto.trace.operators as ops

        return ops.neg(self)

    def __abs__(self):
        import opto.trace.operators as ops

        return ops.abs(self)

    def __invert__(self):
        import opto.trace.operators as ops

        return ops.invert(self)

    def __round__(self, n=None):
        import opto.trace.operators as ops

        return ops.round(self, node(n) if n is not None else None)

    def __floor__(self):
        import opto.trace.operators as ops

        return ops.floor(self)

    def __ceil__(self):
        import opto.trace.operators as ops

        return ops.ceil(self)

    def __trunc__(self):
        import opto.trace.operators as ops

        return ops.trunc(self)

    ## Normal arithmetic operators
    def __add__(self, other):
        import opto.trace.operators as ops

        if type(self._data) is str:
            return ops.concat(self, node(other))
        else:
            return ops.add(self, node(other))

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        import opto.trace.operators as ops

        return ops.subtract(self, node(other))

    def __mul__(self, other):
        import opto.trace.operators as ops

        return ops.multiply(self, node(other))

    def __floordiv__(self, other):
        import opto.trace.operators as ops

        return ops.floor_divide(self, node(other))

    def __truediv__(self, other):
        import opto.trace.operators as ops

        return ops.divide(self, node(other))

    def __mod__(self, other):
        import opto.trace.operators as ops

        return ops.mod(self, node(other))

    def __divmod__(self, other):
        import opto.trace.operators as ops

        return ops.divmod(self, node(other))

    def __pow__(self, other):
        import opto.trace.operators as ops

        return ops.power(self, node(other))

    def __lshift__(self, other):
        import opto.trace.operators as ops

        return ops.lshift(self, node(other))

    def __rshift__(self, other):
        import opto.trace.operators as ops

        return ops.rshift(self, node(other))

    def __and__(self, other):
        import opto.trace.operators as ops

        return ops.and_(self, node(other))

    def __or__(self, other):
        import opto.trace.operators as ops

        return ops.or_(self, node(other))

    def __xor__(self, other):
        import opto.trace.operators as ops

        return ops.xor(self, node(other))

    def __iter__(self):
        import opto.trace.containers as ct

        return ct.iterate(self)

    def __len__(self):
        # __len__ restricts return type to be integer
        # therefore, we only return integer here
        # if users want a Node, they need to call node.len() instead
        return len(self._data)

    # for logic operators
    # case 1: used in if-statement, then we should return a bool
    # case 2: used else-where, then we should return Node(bool)
    # we can't quite distinguish myopically, so...in here, we prioritize case 1
    def __lt__(self, other):
        import opto.trace.operators as ops

        return ops.lt(self, node(other))
        # if isinstance(other, Node):
        #     other = other.data
        # return self._data < other

    def __le__(self, other):
        import opto.trace.operators as ops

        return ops.le(self, node(other))
        # if isinstance(other, Node):
        #     other = other.data
        # return self._data <= other

    def __gt__(self, other):
        import opto.trace.operators as ops

        return ops.gt(self, node(other))
        # if isinstance(other, Node):
        #     other = other.data
        # return self._data > other

    def __ge__(self, other):
        import opto.trace.operators as ops

        return ops.ge(self, node(other))
        # if isinstance(other, Node):
        #     other = other.data
        # return self._data >= other

    # this creates a lot of issues if we return Node
    # instead of bool (for example "in" operator will not work)
    def __eq__(self, other):
        # import opto.trace.operators as ops
        # return ops.eq(self, node(other))
        if isinstance(other, Node):
            other = other.data
        return self._data == other

    def __hash__(self):
        return super().__hash__()

    def __bool__(self):
        # not tracing this conversion
        return bool(self._data)

    # string operators
    def format(self, *args, **kwargs):
        if type(self._data) is not str:
            raise AttributeError(f"{type(self._data)} object has no attribute 'format'.")

        import opto.trace.operators as ops

        return ops.format(self, *args, **kwargs)

    def capitalize(self):
        if type(self._data) is not str:
            raise AttributeError(f"{type(self._data)} object has no attribute 'capitalize'.")
        import opto.trace.operators as ops

        return ops.capitalize(self)

    def lower(self):
        if type(self._data) is not str:
            raise AttributeError(f"{type(self._data)} object has no attribute 'lower'.")
        import opto.trace.operators as ops

        return ops.lower(self)

    def upper(self):
        if type(self._data) is not str:
            raise AttributeError(f"{type(self._data)} object has no attribute 'upper'.")
        import opto.trace.operators as ops

        return ops.upper(self)

    def swapcase(self):
        if type(self._data) is not str:
            raise AttributeError(f"{type(self._data)} object has no attribute 'swapcase'.")
        import opto.trace.operators as ops

        return ops.swapcase(self)

    def title(self):
        if type(self._data) is not str:
            raise AttributeError(f"{type(self._data)} object has no attribute 'title'.")
        import opto.trace.operators as ops

        return ops.title(self)

    def split(self, sep=None, maxsplit=-1):
        if type(self._data) is not str:
            raise AttributeError(f"{type(self._data)} object has no attribute 'split'.")
        import opto.trace.operators as ops

        return ops.split(self, sep, maxsplit)

    def strip(self, chars=None):
        if type(self._data) is not str:
            raise AttributeError(f"{type(self._data)} object has no attribute 'strip'.")
        import opto.trace.operators as ops

        return ops.strip(self, chars)

    def replace(self, old, new, count=-1):
        if type(self._data) is not str:
            raise AttributeError(f"{type(self._data)} object has no attribute 'replace'.")
        import opto.trace.operators as ops

        return ops.replace(self, node(old), node(new), count)

    # container specific methods
    def items(self):
        import opto.trace.containers as ct

        return ct.items(self)

    def pop(self, __index=-1):
        # python does hidden type checks
        import opto.trace.operators as ops

        return ops.pop(self, node(__index))

    def append(self, *args, **kwargs):
        return self.call("append", *args, **kwargs)


class ParameterNode(Node[T]):
    # This is a shorthand of a trainable Node.
    def __init__(
        self,
        value,
        *,
        name=None,
        trainable=True,
        description="[ParameterNode] This is a ParameterNode in a computational graph.",
        constraint=None,
        info=None,
    ) -> None:
        super().__init__(
            value, name=name, trainable=trainable, description=description, constraint=constraint, info=info
        )
        self._parameter_dependencies = set({self})

    def __str__(self) -> str:
        # str(node) allows us to look up in the feedback dictionary easily
        return f"ParameterNode: ({self.name}, dtype={type(self._data)}, data={self._data})"


class MessageNode(Node[T]):
    """Output of an operator.

    description: a string to describe the operator it begins with
    [operator_name] and then describes the operator. When referring to
    inputs use the keys in args (if args is a dict), or the names of the
    nodes in args (if args is a list). Here're some examples:

    MessageNode(node_a, inputs=[node_a], description="[identity] This is an identity operator.")
    MessageNode(copy_node_a, inputs=[node_a], description="[copy] This is a copy operator.")
    MesssageNode(1, inputs={'a':node_a, 'b':node_b}, description="[Add] This is an add operator of a and b.")
    """

    def __init__(
        self,
        value,
        *,
        inputs: Union[List[Node], Dict[str, Node]],  # extra
        description: str,
        constraint=None,
        name=None,
        info=None,
    ) -> None:
        super().__init__(value, name=name, description=description, constraint=constraint, info=info)

        assert isinstance(inputs, list) or isinstance(inputs, dict), "Inputs to MessageNode must be a list or a dict."
        # If inputs is not a dict, we create a dict with the names of the nodes as keys
        if isinstance(inputs, list):
            inputs = {v.name: v for v in inputs}
        self._inputs = inputs

        # If not tracing, MessageNode would just behave like a Node.
        if not GRAPH.TRACE:
            assert len(self._inputs) == 0, "MessageNode should have no inputs when not tracing."

        # Add parents if we are tracing
        for k, v in self._inputs.items():
            assert isinstance(v, Node), f"Input {k} is not a Node."
            self._add_parent(v)
            self._add_parameter_dependencies(v)

    @property
    def inputs(self):
        return copy.copy(self._inputs)

    def __str__(self) -> str:
        # str(node) allows us to look up in the feedback dictionary easily
        return f"MessageNode: ({self.name}, dtype={type(self._data)}, data={self._data})"

    def _add_feedback(self, child, feedback):
        """Add feedback from a child."""
        super()._add_feedback(child, feedback)
        assert len(self.feedback[child]) == 1, "MessageNode should have only one feedback from each child."


class ExceptionNode(MessageNode[T]):
    """Node containing the exception message."""

    def __init__(
        self,
        value: Exception,
        *,
        inputs: Union[List[Node], Dict[str, Node]],
        description: str = "[ExceptionNode] This is node containing the error of execution.",
        constraint=None,
        name=None,
        info=None,
    ) -> None:
        e = value
        error_type = re.search(r"<class '(.*)'>", str(type(e))).group(1)
        if not isinstance(value, trace.TraceExecutionError):
            value = f"({error_type}) {str(e)}"
        super().__init__(value, inputs=inputs, description=description, constraint=constraint, name=name, info=info)


if __name__ == "__main__":
    x = node("Node X")
    y = node("Node Y")
    z = MessageNode("Node Z", inputs={"x": x, "y": y}, description="[Add] This is an add operator of x and y.")
    print(x.name, y.name)
    print([p.name for p in z.parents])

    x: AbstractNode[str] = node("Node X")
    x: Node[str] = node("Node X")
    x: ParameterNode[str] = ParameterNode("Node X", trainable=True)
    x: MessageNode[str] = MessageNode(
        "Node X", inputs={"x": x, "y": y}, description="[Add] This is an add operator of x and y."
    )
