import warnings
from typing import Optional, List, Dict, Callable, Union, Type, Any
import copy
from collections import defaultdict
from typing import TypeVar, Generic
import re
import heapq



def node(data, name=None, trainable=False, description=None, constraint=None):
    """Create a Node from a data. If data is already a Node, return it.
    This method is for the convenience of the user, it should be used over
    directly invoking Node."""
    assert type(description) is str or description is None

    if trainable:
        if isinstance(data, Node):
            name = name or data.name.split(':')[0]
            data = data._data

        return ParameterNode(data, name=name, trainable=True, description=description, constraint=constraint)
    else:
        if isinstance(data, Node):
            if name is not None:
                warnings.warn(f"Name {name} is ignored because data is already a Node.")
            return data
        else:
            return Node(data, name=name, description=description, constraint=constraint)


NAME_SCOPES = []  # A stack of name scopes


class Graph:
    """This a registry of all the nodes. All the nodes form a Directed Acyclic Graph."""

    TRACE = True  # When True, we trace the graph when creating MessageNode. When False, we don't trace the graph.

    def __init__(self):
        self._nodes = defaultdict(list)  # a lookup table to find nodes by name

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


# These are operators that do not change the data type and can be viewed as identity operators.
IDENTITY_OPERATORS = ("identity", "clone")


def get_op_name(description):
    """Extract the operator type from the description."""
    assert type(description) is str, f"Description must be a string, but it is {type(description)}: {description}."
    match = re.search(r"^\[([^\[\]]+)\]", description)
    if match:
        operator_type = match.group(1)
        return operator_type
    else:
        raise ValueError(f"The description '{description}' must contain the operator type in square brackets.")

class NodeVizStyleGuide:
    def __init__(self, style='default', print_limit=100):
        self.style = style
        self.print_limit = print_limit

    def get_attrs(self, x):
        attrs= {
            'label': self.get_label(x),
            'shape': self.get_node_shape(x),
            'fillcolor': self.get_color(x),
            'style': self.get_style(x)
        }
        return attrs

    def get_label(self, x):
        # using colon in the name causes problems in graphviz
        description = x.description
        if len(x.description) > self.print_limit:
            description = x.description[:self.print_limit] + "..."

        text = x.py_name + "\n" + description + "\n"
        content = str(x.data)
        if isinstance(x.data, dict):
            if "content" in x.data:
                content = str(x.data["content"])

        if len(content) > self.print_limit:
            content = content[:self.print_limit] + "..."
        return text + content

    def get_node_shape(self, x):
        if type(x) == ParameterNode:
            return 'box'
        else:
            return "ellipse"

    def get_color(self, x):
        if type(x) == ExceptionNode:
            return 'firebrick1'
        elif type(x) == ParameterNode:
            return '#DEEBF6'

        return ""

    def get_style(self, x):
        return 'filled,solid' if x.trainable else ""

class NodeVizStyleGuideColorful(NodeVizStyleGuide):
    def __init__(self, style='default', print_limit=100):
        self.style = style
        self.print_limit = print_limit

    def get_attrs(self, x):
        attrs= {
            'label': self.get_label(x),
            'shape': self.get_node_shape(x),
            'fillcolor': self.get_color(x),
            'style': self.get_style(x),
            'color': self.get_border_color(x),
            'penwidth': "1.2"
        }
        return attrs

    def get_border_color(self, x):
        if type(x) == ExceptionNode:
            return 'black'
        elif type(x) == ParameterNode:
            return '#FF7E79'

        return "#5C9BD5"
    def get_color(self, x):
        if type(x) == ExceptionNode:
            return 'firebrick1'
        elif type(x) == ParameterNode:
            return '#FFE5E5'

        return "#DEEBF6"
    def get_style(self, x):
        return 'filled,solid'

class Node(AbstractNode[T]):
    """A data node in a directed graph, where the direction is from parents to children. This is basic data type of Trace. """

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
        if description == "" or description is None:
            description = "[Node] This is a node in a computational graph."

        matched = re.match(r"^\[([^\[\]]+)\]", description)
        if not matched:
            description = '[Node] ' + description.strip()

        super().__init__(value, name=name)
        self.trainable = trainable
        self._feedback = defaultdict(
            list
        )  # (analogous to gradient) this is the feedback from the user. Each key is a child and the value is a list of feedbacks from the child.
        # We keep the propagated feedback as dict and let the propagator performs
        # the aggreation, rather than doing the aggregation incrementally. This is
        # to support implementing aggregation that is not commutable.
        self._description = description  # Information to describe of the node
        self._constraint = constraint  # A constraint on the node
        self._backwarded = False  # True if backward has been called
        self._info = info  # Additional information about the node
        self._dependencies = {'parameter': set(), 'expandable': set()}  # A dictionary of dependencies on parameters and expandable nodes; expandable nodes are those who depened on parameters not visible in the current graph level.

    def zero_feedback(self):  # set feedback to zero
        self._feedback = defaultdict(list)

    @property
    def feedback(self):
        return self._feedback

    @property
    def description(self):
        # return a textual description of the node
        return self._description

    @property
    def info(self):
        return self._info

    @property
    def type(self):
        return type(self._data)

    @property
    def parameter_dependencies(self):
        """ The depended parameters. """
        return self._dependencies['parameter']

    @property
    def expandable_dependencies(self):
        """ The depended expandable nodes, where expandable nodes are those who depend on parameters not visible in the current graph level. """
        return self._dependencies['expandable']

    def _add_feedback(self, child, feedback):
        """Add feedback from a child."""
        self._feedback[child].append(feedback)

    # This is not traced
    def _set(self, value: Any):
        """Set the value of the node. If value is Node, it will be unwrapped."""
        if isinstance(value, Node):
            value = value.data
        self._data = value

    def _itemize(self):  # for priority queue
        return (-self.level, id(self), self)

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
            from opto.trace.propagators.graph_propagator import GraphPropagator  # this avoids circular import

            propagator = GraphPropagator()

        # Setup for visualization
        digraph = None
        nvsg = NodeVizStyleGuideColorful(print_limit=print_limit)

        if visualize:
            from graphviz import Digraph

            digraph = Digraph()
            visited = set()

        # Check for root node with no parents
        if self._backwarded:
            raise AttributeError(f"{self} has been backwarded.")
        self._add_feedback(Node("FEEDBACK_ORACLE"), propagator.init_feedback(self, feedback))

        if len(self.parents) == 0:  # This is a root. Nothing to propagate
            if visualize:
                digraph.node(self.py_name, **nvsg.get_attrs(self))
            # self._backwarded = not retain_graph  # only need to be set for MessageNode
            return digraph

        # TODO check memory leak
        queue = [self._itemize()]  # priority queue; add id() since __eq__ is overloaded to compare values.
        while True:
            try:
                _, _, node = heapq.heappop(queue)  # All the children of this node have been visited
                # Each node is a MessageNode, which has at least one parent.
                assert len(node.parents) > 0 and isinstance(node, MessageNode)
                if node._backwarded:
                    raise AttributeError(f"{node} has been backwarded.")

                # Propagate information from node to its parents
                propagated_feedback = propagator(node)

                # Zero-out the feedback once it's propagated.
                # This is to ensure the feedback is not double counted when retain_graph is True.
                node.zero_feedback()

                for parent in node.parents:
                    if parent in propagated_feedback:
                        parent._add_feedback(node, propagated_feedback[parent])

                    # Put parent in the queue if it has not been visited and it's not a root
                    if len(parent.parents) > 0 and parent._itemize() not in queue:  # and parent not in queue:
                        heapq.heappush(queue, parent._itemize())  # put parent in the priority queue

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
                            digraph.node(node.py_name, **nvsg.get_attrs(node))
                            digraph.node(parent.py_name, **nvsg.get_attrs(parent))

                node._backwarded = not retain_graph  # set backwarded to True

            except IndexError:  # queue is empty
                break

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
        return self + node(other)

    def __sub__(self, other):
        import opto.trace.operators as ops

        return ops.subtract(self, node(other))

    def __rsub__(self, other):
        return node(other) - self

    def __mul__(self, other):
        import opto.trace.operators as ops

        return ops.multiply(self, node(other))

    def __rmul__(self, other):
        return self * node(other)

    def __floordiv__(self, other):
        import opto.trace.operators as ops

        return ops.floor_divide(self, node(other))

    def __rfloordiv__(self, other):
        return node(other) // self

    def __truediv__(self, other):
        import opto.trace.operators as ops

        return ops.divide(self, node(other))

    def __rtruediv__(self, other):
        return node(other) / self

    def __div__(self, other):
        import opto.trace.operators as ops

        return ops.divide(self, node(other))

    def __rdiv__(self, other):
        return node(other) / self

    def __mod__(self, other):
        import opto.trace.operators as ops

        return ops.mod(self, node(other))

    def __rmod__(self, other):
        return  node(other) % self

    def __divmod__(self, other):
        import opto.trace.operators as ops

        return ops.node_divmod(self, node(other))

    def __rdivmod__(self, other):
        return divmod(node(other), self)

    def __pow__(self, other):
        import opto.trace.operators as ops

        return ops.power(self, node(other))

    def __rpow__(self, other):
        return node(other) ** self

    def __lshift__(self, other):
        import opto.trace.operators as ops

        return ops.lshift(self, node(other))

    def __rlshift__(self, other):
        return node(other) << self

    def __rshift__(self, other):
        import opto.trace.operators as ops

        return ops.rshift(self, node(other))

    def __rrshift__(self, other):
        return node(other) >> self

    def __and__(self, other):
        import opto.trace.operators as ops

        return ops.and_(self, node(other))

    def __rand__(self, other):
        return node(other) & self

    def __or__(self, other):
        import opto.trace.operators as ops

        return ops.or_(self, node(other))

    def __ror__(self, other):
        return node(other) | self

    def __xor__(self, other):
        import opto.trace.operators as ops

        return ops.xor(self, node(other))

    def __rxor__(self, other):
        return node(other) ^ self

    def __iter__(self):
        import opto.trace.iterators as it

        return it.iterate(self)

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

    def eq(self, other):
        import opto.trace.operators as ops
        return ops.eq(self, node(other))

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
        if not isinstance(self._data, dict):
            raise AttributeError(f"{type(self._data)} object has no attribute 'items'.")
        import opto.trace.iterators as it

        return it.DictIterable(self)

    def values(self):
        import opto.trace.operators as ops

        return ops.values(self)

    def keys(self):
        if not isinstance(self._data, dict):
            raise AttributeError(f"{type(self._data)} object has no attribute 'keys'.")

        import opto.trace.operators as ops

        return ops.keys(self)

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
        if description is None or description == "":
            description = "[ParameterNode] This is a ParameterNode in a computational graph."

        matched = re.match(r"^\[([^\[\]]+)\]", description)
        if not matched:
            description = '[ParameterNode] ' + description.strip()

        super().__init__(
            value, name=name, trainable=trainable, description=description, constraint=constraint, info=info
        )
        self._dependencies['parameter'].add(self)

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
    # TODO document what needs to go into info

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
            self._add_dependencies(v)  # Initializes the dependencies on parameter and expandable nodes

        if len(self.hidden_dependencies)>0:
            self._dependencies['expandable'].add(self)


    @property
    def inputs(self):
        return copy.copy(self._inputs)

    def __str__(self) -> str:
        # str(node) allows us to look up in the feedback dictionary easily
        return f"MessageNode: ({self.name}, dtype={type(self._data)}, data={self._data})"

    def _add_feedback(self, child, feedback):
        """Add feedback from a child."""
        super()._add_feedback(child, feedback)
        assert len(self._feedback[child]) == 1, "MessageNode should have only one feedback from each child."

    @property
    def hidden_dependencies(self):
        """ Returns the set of hidden dependencies that are not visible in the current graph level."""
        if isinstance(self.info, dict) and isinstance(self.info.get('output'), Node):
            if len(self.info['output'].parameter_dependencies) > len(self.parameter_dependencies):
                return self.info['output'].parameter_dependencies - self.parameter_dependencies
        return set()

    def _add_dependencies(self, parent):
        assert parent is not self, "Cannot add self as a parent."
        assert isinstance(parent, Node), f"{parent} is {type(parent)}, which is not a Node."
        self._dependencies['parameter'] = self._dependencies['parameter'] | parent._dependencies['parameter']
        self._dependencies['expandable'] = self._dependencies['expandable'] | parent._dependencies['expandable']


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
        from opto import trace
        value = f"({error_type}) {str(e)}"
        super().__init__(value, inputs=inputs, description=description, constraint=constraint, name=name, info=info)

    def create_feedback(self, style='simple'):
        assert style in ('simple', 'full')
        feedback = self._data
        if style in ('line', 'full'):
            if type(self.info)==dict and self.info.get('error_comment') is not None:
                feedback = self.info['error_comment']
        return feedback


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
