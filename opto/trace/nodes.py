import warnings
from typing import Optional, List, Dict, Callable, Union, Type, Any
import copy
from collections import defaultdict
from typing import TypeVar, Generic
import re
import heapq


def node(data, name=None, trainable=False, description=None, constraint=None):
    """Create a Node object from data.

    Args:
        data: The data to create the Node from.
        name (str, optional): The name of the Node.
        trainable (bool, optional): Whether the Node is trainable. Defaults to False.
        description (str, optional): A string describing the data.
        constraint (str, optional): A string describing any constraint that the data should obey.

    Returns:
        Node: A Node object containing the data.

    Notes:
        If trainable=True:
            - If data is already a Node, extracts underlying data and updates name
            - Creates ParameterNode with extracted data, name, trainable=True and constraint

        If trainable=False:
            - If data is already a Node, returns it (with warning if name provided)
            - Otherwise creates new Node with data, name and constraint
    """
    assert type(description) is str or description is None

    if trainable:
        if isinstance(data, Node):
            name = name or data.name.split(":")[0]
            data = data._data

        return ParameterNode(
            data,
            name=name,
            trainable=True,
            description=description,
            constraint=constraint,
        )
    else:
        if isinstance(data, Node):
            if name is not None:
                warnings.warn(f"Name {name} is ignored because data is already a Node.")
            return data
        else:
            return Node(data, name=name, description=description, constraint=constraint)


NAME_SCOPES = []  # A stack of name scopes


class Graph:
    """Graph is a registry of all the nodes, forming a Directed Acyclic Graph (DAG).

    Attributes:
        _nodes (defaultdict): An instance-level attribute, which is a defaultdict of lists, used as a lookup table to find nodes by name.

    Notes:
        The Graph class manages and organizes nodes in a Directed Acyclic Graph (DAG).
        It provides methods to register nodes, clear the graph, retrieve nodes by name, and identify root nodes.
        The `register` method assumes that elements in `_nodes` are never removed,
        which is important for maintaining the integrity of node names.
    """

    TRACE = True  # When True, we trace the graph when creating MessageNode. When False, we don't trace the graph.

    def __init__(self):
        """Initialize the Graph object.

        The initialization sets up the `_nodes` attribute as a defaultdict of lists to store nodes by their names.
        """
        self._nodes = defaultdict(list)  # a lookup table to find nodes by name

    def clear(self):
        """Remove all nodes from the graph.

        The clear function iterates over the current nodes stored in the _nodes attribute and deletes each node.
        After all nodes have been deleted, it reinitializes the _nodes attribute to an empty defaultdict of lists.
        This ensures that the graph is completely cleared and ready to be repopulated with new nodes if necessary.

        Notes:
            After calling clear, any references to the previously stored nodes will become invalid.
            The function is called in unit tests to reset the state of the graph between test cases,
            ensuring that each test runs with a clean slate and is not affected by the state left by previous tests.
        """
        for node in self._nodes.values():
            del node
        self._nodes = defaultdict(list)
        # self._levels = defaultdict(list)

    def register(self, node):
        """Add a node to the graph.

        Args:
            node: The node object to be registered in the graph.

        Notes:
            The register function should only be called after the node has been properly initialized and its name has been set.
            The function assumes that elements in the `_nodes` dictionary never get removed.
            After checking that the input is a `Node` and its name has the right format, the function splits the name of the node into the `name` variable and the identifier.
            The function then checks if there are any name scopes defined in the `NAME_SCOPES` list. If the length of the list is greater than 0, the name is prefixed with the last scope in the list followed by a "/". This allows for scoping of node names.
            Finally, the function adds the node to the `_nodes` dictionary using the modified name as the key. The `_name` attribute of the node is set to the modified name followed by the index of the node in the list of nodes with the same name.
        """
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
        """Retrieve a node from the graph by its name.

        Args:
            name (str): A string in the format "name:id", where "name" is the name of the node and "id" is the identifier of the node.

        Returns:
            Node: The requested node from the graph.

        Notes:
            Ensure that the 'name' parameter is correctly formatted as "name:id" before calling this function.
            The function assumes that the '_nodes' attribute is a dictionary where each key is a node name and the corresponding value is a list of nodes.
            The 'id' should be a valid index within the list of nodes for the given 'name'.
        """
        name, id = name.split(":")
        return self._nodes[name][int(id)]

    @property
    def roots(self):
        """Get all root nodes in the graph.

        Returns:
            list: A list of all root nodes in the graph. A root node is identified by its `is_root` attribute.
        """
        return [v for vv in self._nodes.values() for v in vv if v.is_root]

    def __str__(self):
        """Get string representation of the graph.

        Returns:
            str: String representation of the `_nodes` attribute, useful for debugging and logging.
        """
        return str(self._nodes)

    def __len__(self):
        """Get total number of nodes in the graph.

        Returns:
            int: The total number of nodes in the graph by summing the lengths of all lists in the `_nodes` dictionary.
        """
        # This is the number of nodes in the graph
        return sum([len(v) for v in self._nodes.values()])


GRAPH = Graph()  # This is a global registry of all the nodes.

USED_NODES = (
    list()
)  # A stack of sets. This is a global registry to track which nodes are read.

T = TypeVar("T")


class AbstractNode(Generic[T]):
    """AbstractNode represents an abstract data node in a directed graph.

    Notes:
        The `AbstractNode` class is meant to be subclassed and extended to create specific types of nodes.
        The node can have multiple parents and children, forming a directed graph structure.
        The node has a name, which is used to identify it within the graph.
        The `py_name` attribute is the same as the name attribute, but with the ":" character removed.

        The node can be initialized with a value, an optional name, and an optional trainable flag.
        If the value is an instance of the `Node` class, the node will be initialized as a reference to that node, otherwise, the value will be stored directly in the node.
        The default name is generated based on the type of the value and a version number which serves as the identifier, separated by ":".

        The `AbstractNode` class provides several properties to access its attributes. The `data` property allows access to the stored data.
        If the node is being traced within a context, the `data` property adds the node to the list of nodes used in that context.
        The `parents` property returns a list of parent nodes, and the `children` property returns a list of child nodes.
        The `name` property returns the name of the node, and the `py_name` property returns the name without the ":" character.
        The `id` property returns the version number/identifier extracted from the name.
        The `level` property returns the level of the node in the DAG.
        The `is_root` property returns True if the node has no parents, and the `is_leaf` property returns True if the node has no children.

        The `AbstractNode` class also provides internal methods to add parents and children to the node.
        The `_add_child` method adds a child node to the node's list of children.
        The `_add_parent` method adds a parent node to the node's list of parents and updates the level of the node based on the parent's level.

        The `AbstractNode` class overrides the `__str__` method to provide a string representation of the node. The representation includes the name, the type of the data, and the data itself.
        The `AbstractNode` class implements the `__deepcopy__` method to create a deep copy of the node. This allows the node to be detached from the original graph.
        The `AbstractNode` class provides comparison methods `lt` and `gt` to compare the levels of two nodes in the DAG.
    """

    def __init__(self, value, *, name=None, trainable=False) -> None:
        """Initialize an instance of the AbstractNode class.

        Args:
            value: The value to be assigned to the node.
            name (str, optional): The name of the node. Defaults to None.
            trainable (bool, optional): Whether the node is trainable or not. Defaults to False.

        Notes:
            During initialization, this function generates a default name for the node based on the type of the `value` parameter.
            If the `name` parameter is provided, it is appended to the default name. The format of the name is "type:version", where the version is set to 0 if no name is provided.
            If the `value` parameter is an instance of the Node class, the `_data` attribute of the current node is set to the `_data` attribute of the `value` parameter,
            and the `_name` attribute is set to the `_name` attribute of the `value` parameter if no name is provided.
            Otherwise, the `_data` attribute is set to the `value` parameter itself, and the `_name` attribute is set to the default name.
            Finally, the function calls the `register` function of the GRAPH object to register the current node in the graph.
        """
        self._parents = []
        self._children = []
        self._level = 0  # roots are at level 0
        default_name = (
            str(type(value).__name__) + ":0" if name is None else name + ":0"
        )  # name:version
        if isinstance(value, Node):  # just a reference
            self._data = value._data
            self._name = value._name if name is None else default_name
        else:
            self._data = value
            self._name = default_name
        GRAPH.register(self)  # When created, register the node to the graph.

    @property
    def data(self):
        """Retrieve the internal data of a node.

        Returns:
            Any: The internal data stored in the node.

        Notes:
            If within a trace_nodes context and GRAPH.TRACE is True, adds the node to USED_NODES.
            This function assumes that the "_data" attribute exists within the node object.
            If this attribute is not present, an AttributeError will be raised.
        """
        if len(USED_NODES) > 0 and GRAPH.TRACE:  # We're within trace_nodes context.
            USED_NODES[-1].add(self)
        return self.__getattribute__("_data")

    @property
    def parents(self):
        """Get the parents of a node.

        Returns:
            list: The list of parent nodes.

        Notes:
            This property is an essential part of the graph structure and is used in various operations
            such as graph traversal and feedback propagation.
        """
        return self._parents

    @property
    def children(self):
        """Get the children of a node.

        Returns:
            list: The list of child nodes.

        Notes:
            This property is essential for accessing the hierarchical structure of nodes,
            allowing traversal and manipulation of the DAG.
        """
        return self._children

    @property
    def name(self):
        """Get the name of the node.

        Returns:
            str: The name of the node.

        Notes:
            This property is set when the node is registered in the graph.
            It is a combination of the node's name and its index in the list of nodes with the same name.
            The index is incremented each time a new node with the same name is registered.
            This assumes that elements in the `_nodes` dictionary of the graph never get removed.
        """
        return self._name

    @property
    def py_name(self):
        """Get the Python-friendly name of the node.

        Returns:
            str: The name of the node with ":" characters removed.
        """
        return self.name.replace(":", "")

    @property
    def id(self):
        """Get the identifier part of the node's name.

        Returns:
            str: The identifier portion of the node's name (part after the colon).

        Notes:
            The `name` property is a string formatted as "name:identifier".
            This property splits that string using the colon (":") delimiter and returns the second part,
            which corresponds to the identifier.
            Ensure that the `name` attribute contains a colon (":") to avoid index errors during the split operation.
        """
        return self.name.split(":")[1]

    @property
    def level(self):
        """Get the level of the node in the graph.

        Returns:
            int: The level of the node.

        Notes:
            The level is determined by the maximum level of its parents plus one.
            The level of a root node is 0.
        """
        return self._level

    @property
    def is_root(self):
        """Check if the node is a root node.

        Returns:
            bool: True if the node has no parents, False otherwise.
        """
        return len(self.parents) == 0

    @property
    def is_leaf(self):
        """Check if the node is a leaf node.

        Returns:
            bool: True if the node has no children, False otherwise.
        """
        return len(self.children) == 0

    def _add_child(self, child):
        """Add a child node to the current node.

        Args:
            child: The child node to be added.

        Notes:
            The function first checks if the child node is not the same as the current node itself.
            If it is, it raises an assertion error (no self-loops allowed in the DAG).
            It then checks if the child node is an instance of the `Node` class.
            If it is not, it raises a different assertion error.
            Finally, it calls the `_add_parent` function of the child node, passing the current node as the parent.
        """
        assert child is not self, "Cannot add self as a child."
        assert isinstance(child, Node), f"{child} is not a Node."
        child._add_parent(self)

    def _add_parent(self, parent):
        """Add a parent node to the current node.

        Args:
            parent: The parent node to be added.

        Notes:
            The function asserts that the parent node is not the same as the current node itself.
            This check prevents self-loops in the DAG.
            It then asserts that the parent node is an instance of the `Node` class.
            This check ensures that only valid nodes can be added as parents.
            If both checks pass, the function proceeds to add the current node as a child to the parent node
            by appending it to the parent's `_children` attribute. Similarly, it adds the parent node to
            the current node's `_parents` attribute.
            Finally, the function calls the _update_level method to update the level attribute of the current node.
            It passes the maximum value between the current node's _level attribute and the parent node's _level
            attribute plus one as the new level value.
            This ensures that the hierarchical structure of the nodes is maintained correctly,
            with child nodes always having a level greater than or equal to their parent nodes.
        """
        assert parent is not self, "Cannot add self as a parent."
        assert isinstance(
            parent, Node
        ), f"{parent} is {type(parent)}, which is not a Node."
        parent._children.append(self)
        self._parents.append(parent)
        self._update_level(
            max(self._level, parent._level + 1)
        )  # Update the level, because the parent is added

    def _update_level(self, new_level):
        """Update the level attribute of the current node.

        Args:
            new_level (int): The new level to which the node's level attribute should be updated.

        Notes:
            The function does not perform any validation or checks on the new_level parameter;
            it directly assigns it to the _level attribute.
        """
        # GRAPH._levels[self._level].remove(self)  # this uses the == operator which compares values. We need to compare references.
        self._level = new_level
        # GRAPH._levels[new_level].append(self)
        # assert all([len(GRAPH._levels[i]) > 0 for i in range(len(GRAPH._levels))]), "Some levels are empty."

    def __str__(self) -> str:
        """Get string representation of the node.

        Returns:
            str: A string containing the node's name, data type, and data value.

        Notes:
            The `__str__` method constructs a string representation of the node by concatenating
            the node's name, the data type of the node's data, and the actual data stored in the node.
            Doing str(node) allows us to look up the node in the feedback dictionary maintained by
            Trace during the backward pass easily.
            Ensure that the node has been properly initialized and registered before calling this
            method to avoid any unexpected behavior.
        """
        # str(node) allows us to look up in the feedback dictionary easily
        return f"Node: ({self.name}, dtype={type(self._data)}, data={self._data})"

    def __deepcopy__(self, memo):
        """Create a deep copy of the node.

        Args:
            memo (dict): A dictionary used to keep track of objects that have already been copied.

        Returns:
            AbstractNode: A new instance that is a deep copy of the current node.

        Notes:
            The new instance will be a completely independent copy of the original,
            with no shared references to mutable objects.
            1. The function starts by obtaining the class of the current instance (`cls = self.__class__`).
            2. It then creates a new, uninitialized instance of this class (`result = cls.__new__(cls)`).
            3. The `memo` dictionary is updated to associate the original instance's ID with the new instance.
            This helps in tracking already copied objects to prevent infinite loops.
            4. The function iterates over all the attributes of the original instance.
            5. For attributes named `_parents` or `_children`, it sets these attributes in the new instance
            to empty lists. This ensures that the new instance starts with no parent or child nodes.
            6. For all other attributes, it performs a deep copy of the attribute's value and assigns it
            to the new instance.
            7. Finally, the new instance is returned.
        """
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            if k == "_parents" or k == "_children":
                setattr(result, k, [])
            elif k == "_feedback":
                setattr(result, k, defaultdict(list))
            else:
                setattr(result, k, copy.deepcopy(v, memo))
        GRAPH.register(result)
        return result

    def lt(self, other):
        """Compare if this node's level is less than another node's level.

        Args:
            other: The other node to compare against.

        Returns:
            bool: True if this node's level is less than the other node's level.

        Notes:
            This method is used to compare the levels of two nodes in the DAG.
            Therefore it checks if the negated level of the current node (`-self._level`)
            is less than the negated level of the other node (`-other._level`)
        """
        return -self._level < -other._level

    def gt(self, other):
        """Compare if this node's level is greater than another node's level.

        Args:
            other: The other node to compare against.

        Returns:
            bool: True if this node's level is greater than the other node's level.

        Notes:
            This method is used to compare the levels of two nodes in the DAG.
            Therefore it checks if the negated level of the current node (`-self._level`)
            is greater than the negated level of the other node (`-other._level`)
        """
        return -self._level > -other._level


# These are operators that do not change the data type and can be viewed as identity operators.
IDENTITY_OPERATORS = ("identity", "clone")


def get_op_name(description):
    """Extract the operator type from the description.

    Args:
        description (str): A string containing the description of the node.

    Returns:
        str: The extracted operator type.

    Raises:
        ValueError: If the description does not contain an operator type in square brackets.

    Notes:
        The `get_op_name` function takes a description as input and uses regular expression
        to search for the operator type enclosed in square brackets at the beginning of the description.
        If a match is found, the operator type is extracted and returned.
        Otherwise, a `ValueError` is raised with a specific error message.
    """
    assert (
        type(description) is str
    ), f"Description must be a string, but it is {type(description)}: {description}."
    match = re.search(r"^\[([^\[\]]+)\]", description)
    if match:
        operator_type = match.group(1)
        return operator_type
    else:
        raise ValueError(
            f"The description '{description}' must contain the operator type in square brackets."
        )


class NodeVizStyleGuide:
    """A class to provide a standardized way to visualize nodes in a graph.

    Attributes:
        style (str): Defines the style of the visualization. Default is 'default'.
        print_limit (int): Sets the maximum number of characters to print for node descriptions and content. Default is 100.
    """

    def __init__(self, style="default", print_limit=100):
        """Initialize the NodeVizStyleGuide.

        Args:
            style (str, optional): The style of visualization to use. Defaults to 'default'.
            print_limit (int, optional): Maximum characters to print for descriptions and content. Defaults to 100.
        """
        self.style = style
        self.print_limit = print_limit

    def get_attrs(self, x):
        """Get the attributes for a node based on the style guide.

        Args:
            x: The node for which attributes are to be generated.

        Returns:
            dict: Dictionary of visualization attributes for the node.

        Notes:
            The attributes include the label, shape, fill color, and style of the node,
            which are determined based on the node's properties and the style guide.
            The method calls other helper methods to construct the label, determine the node shape,
            assign a color, and set the style.
        """
        attrs = {
            "label": self.get_label(x),
            "shape": self.get_node_shape(x),
            "fillcolor": self.get_color(x),
            "style": self.get_style(x),
        }
        return attrs

    def get_label(self, x):
        """Construct a label for a node.

        Args:
            x: The node for which the label is to be constructed.

        Returns:
            str: The constructed label string.

        Notes:
            Using a colon in the name can cause problems in graph visualization tools like Graphviz.
            To avoid issues, the label is constructed by combining the node's Python name,
            truncated description, and content.
            If the description or content exceeds the print limit, it is truncated and appended with an ellipsis.
        """
        # using colon in the name causes problems in graphviz
        description = x.description
        if len(x.description) > self.print_limit:
            description = x.description[: self.print_limit] + "..."

        text = x.py_name + "\n" + description + "\n"
        content = str(x.data)
        if isinstance(x.data, dict):
            if "content" in x.data:
                content = str(x.data["content"])

        if len(content) > self.print_limit:
            content = content[: self.print_limit] + "..."
        return text + content

    def get_node_shape(self, x):
        """Determine the shape of a node.

        Args:
            x: The node for which the shape is to be determined.

        Returns:
            str: The shape to use for the node.

        Notes:
            The shape of a node is determined based on its type.
            ParameterNode types are represented as 'box',
            while other types are represented as 'ellipse'.
        """
        if type(x) is ParameterNode:
            return "box"
        else:
            return "ellipse"

    def get_color(self, x):
        """Assign a color to a node.

        Args:
            x: The node for which the color is to be assigned.

        Returns:
            str: The color to use for the node.

        Notes:
            The color of a node is determined based on its type.
            ExceptionNode types are colored 'firebrick1',
            and ParameterNode types are colored 'lightgray'.
        """
        if type(x) is ExceptionNode:
            return "firebrick1"
        elif type(x) is ParameterNode:
            return "#DEEBF6"

        return ""

    def get_style(self, x):
        """Set the style of a node.

        Args:
            x: The node for which the style is to be set.

        Returns:
            str: The style string for the node.

        Notes:
            The style of a node is set to 'filled,solid' if the node is trainable;
            otherwise, it returns an empty string.
        """
        return "filled,solid" if x.trainable else ""


class NodeVizStyleGuideColorful(NodeVizStyleGuide):
    """A class to provide a colorful style guide for visualizing nodes in a graph.

    Attributes:
        style (str): Defines the style of the visualization. Default is 'default'.
        print_limit (int): Sets the maximum number of characters to print for node descriptions and content. Default is 100.
    """

    def __init__(self, style="default", print_limit=100):
        """Initialize the NodeVizStyleGuideColorful.

        Args:
            style (str, optional): The style of visualization to use. Defaults to 'default'.
            print_limit (int, optional): Maximum characters to print for descriptions and content. Defaults to 100.
        """
        self.style = style
        self.print_limit = print_limit

    def get_attrs(self, x):
        """Get the attributes for a node based on the colorful style guide.

        Args:
            x: The node for which attributes are to be generated.

        Returns:
            dict: Dictionary of visualization attributes for the node.

        Notes:
            The attributes include the label, shape, fill color, style, border color,
            and border width of the node, which are determined based on the node's properties
            and the style guide. The method calls other helper methods to construct the label,
            determine the node shape, assign a color, and set the style.
        """
        attrs = {
            "label": self.get_label(x),
            "shape": self.get_node_shape(x),
            "fillcolor": self.get_color(x),
            "style": self.get_style(x),
            "color": self.get_border_color(x),
            "penwidth": "1.2",
        }
        return attrs

    def get_border_color(self, x):
        """Assign a border color to a node.

        Args:
            x: The node for which the border color is to be assigned.

        Returns:
            str: The border color to use for the node.

        Notes:
            The border color of a node is determined based on its type.
            ExceptionNode types are colored 'firebrick1',
            and ParameterNode types are colored 'black'.
        """
        if type(x) is ExceptionNode:
            return "black"
        elif type(x) is ParameterNode:
            return "#FF7E79"

        return "#5C9BD5"

    def get_color(self, x):
        """Assign a fill color to a node.

        Args:
            x: The node for which the fill color is to be assigned.

        Returns:
            str: The fill color to use for the node.

        Notes:
            The fill color of a node is determined based on its type.
            ExceptionNode types are colored 'firebrick1',
            and ParameterNode types are colored 'lightgray'.
        """
        if type(x) is ExceptionNode:
            return "firebrick1"
        elif type(x) is ParameterNode:
            return "#FFE5E5"

        return "#DEEBF6"

    def get_style(self, x):
        """Set the style of a node always as if it is trainable.

        Args:
            x: The node for which the style is to be set.

        Returns:
            str: The style string 'filled,solid'.
        """
        return "filled,solid"


class Node(AbstractNode[T]):
    """A data node in a directed graph, this is a basic data structure of Trace.

    Args:
        value (Any): The value to be assigned to the node.
        name (str, optional): The name of the node.
        trainable (bool, optional): Whether the node is trainable or not. Defaults to False.
        description (str, optional): String describing the node. Defaults to "[Node] This is a node in a computational graph."
        constraint (Union[None, str], optional): String describing constraints that the data should satisfy. Defaults to None.
        info (Union[None, Dict], optional): Dictionary containing additional information about the node. Defaults to None.

    Attributes:
        trainable (bool): Whether the node is trainable or not.
        _feedback (dict): Dictionary of feedback from children nodes.
        _description (str): String describing the node.
        _constraint (str): String describing all constraints that the data should satisfy.
        _backwarded (bool): Whether the backward method has been called.
        _info (dict): Dictionary containing additional information about the node.
        _dependencies (dict): Dictionary of dependencies on parameters and expandable nodes.

    Notes:
        The Node class extends AbstractNode to represent a data node in a directed graph.
        It includes attributes and methods to handle feedback, constraints, and dependencies.
        The node can be marked as trainable and store feedback from children nodes.
        The feedback mechanism is analogous to gradients in machine learning and propagates
        information back through the graph. The feedback mechanism supports non-commutative
        aggregation, so feedback should be handled carefully to maintain correct operation order.
        The node can track dependencies on parameters and expandable nodes (nodes that depend
        on parameters not visible in the current graph level).
    """

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
        """Initialize an instance of the Node class.

        Args:
            value: The value to be assigned to the node.
            name: The name of the node (optional).
            trainable: A boolean indicating whether the node is trainable or not (optional).
            description: A string describing the node (optional).
            constraint: A string describing constraints on the node (optional).
            info: A dictionary containing additional information about the node (optional).
        """

        if description == "" or description is None:
            description = "[Node] This is a node in a computational graph."

        matched = re.match(r"^\[([^\[\]]+)\]", description)
        if not matched:
            description = "[Node] " + description.strip()

        super().__init__(value, name=name)
        self.trainable = trainable
        # (analogous to gradient) this is the feedback from the user. Each key is a child and the value is a list of feedbacks from the child.
        # We keep the propagated feedback as dict and let the propagator performs
        # the aggreation, rather than doing the aggregation incrementally. This is
        # to support implementing aggregation that is not commutable.
        self._feedback = defaultdict(list)
        self._description = description
        self._constraint = constraint
        self._backwarded = False
        self._info = info
        self._dependencies = {"parameter": set(), "expandable": set()}

    def zero_feedback(self):  # set feedback to zero
        """Zero out the feedback of the node.

        Notes:
            zero_feedback should be used judiciously within the feedback propagation process to avoid unintended loss of feedback data.
            It is specifically designed to be used after feedback has been successfully propagated to parent nodes.
        """
        self._feedback = defaultdict(list)

    @property
    def feedback(self):
        """The feedback from children nodes."""
        return self._feedback

    @property
    def description(self):
        """A textual description of the node."""
        return self._description

    @property
    def info(self):
        """Additional information about the node."""
        return self._info

    @property
    def type(self):
        """The type of the data stored in the node."""
        return type(self._data)

    @property
    def parameter_dependencies(self):
        """The depended parameters.

        Notes:
            Ensure that the '_dependencies' attribute is properly initialized and contains a 'parameter' key
            with a corresponding value before calling the parameter_dependencies function to avoid potential
            KeyError exceptions.
        """
        return self._dependencies["parameter"]

    @property
    def expandable_dependencies(self):
        """The depended expandable nodes.

        Notes:
            Expandable nodes are those who depend on parameters not visible in the current graph level.
            Ensure that the '_dependencies' attribute is properly initialized and contains an 'expandable' key
            with a corresponding value before calling the expandable_dependencies function to avoid potential
            KeyError exceptions.
        """
        return self._dependencies["expandable"]

    def _add_feedback(self, child, feedback):
        """Add feedback from a child.

        Args:
            child: The child node from which feedback is received.
            feedback: The feedback received from the child node.
        """
        self._feedback[child].append(feedback)

    # This is not traced
    def _set(self, value: Any):
        """Set the value of the node. If value is Node, it will be unwrapped.

        Args:
            value: The value to be assigned to the node.

        Notes:
            The `_set` method sets the `_data` attribute of the node to the provided `value`.
            If the `value` is an instance of the `Node` class, the `_data` attribute of the current node
            is set to the `_data` attribute of the `value` parameter.
            Otherwise, the `_data` attribute is set to the `value` parameter itself.
            When `_data` is set using `_set`, that usage is not traced.
        """
        if isinstance(value, Node):
            value = value.data
        self._data = value

    def _itemize(self):  # for priority queue
        """Return a tuple containing the node's level.

        Returns:
            tuple: A tuple containing (-level, id, self) used for priority queue ordering.
        """
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
        """Performs a backward pass in a computational graph.

        This function propagates feedback from the current node to its parents, updates the graph
        visualization if required, and returns the resulting graph.

        Args:
            feedback: The feedback given to the current node.
            propagator: A function that takes in a node and a feedback, and returns a dict of {parent: parent_feedback}.
                If not provided, a default `GraphPropagator` object is used.
            retain_graph: If True, the graph will be retained after backward pass.
            visualize: If True, the graph will be visualized using graphviz.
            simple_visualization: If True, identity operators will be skipped in the visualization.
            reverse_plot: If True, plot the graph in reverse order (from child to parent).
            print_limit: The maximum number of characters to print for node descriptions and content.

        Returns:
            digraph: The visualization graph object if visualize=True, None otherwise.

        Raises:
            AttributeError: If the node has already been backwarded.

        Notes:
            The function checks if the current node has already been backwarded. If it has, an AttributeError is raised.
            For root nodes (no parents), only visualization is performed if enabled.
            For non-root nodes, feedback is propagated through the graph using a priority queue to ensure correct ordering.
            The propagator computes feedback for parent nodes based on the current node's description, data and feedback.
            Visualization is handled using graphviz if enabled, with options to simplify the graph by skipping identity operators.
        """
        if propagator is None:
            from opto.trace.propagators.graph_propagator import (
                GraphPropagator,
            )  # this avoids circular import

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
        self._add_feedback(
            Node("FEEDBACK_ORACLE"), propagator.init_feedback(self, feedback)
        )

        if len(self.parents) == 0:  # This is a root. Nothing to propagate
            if visualize:
                digraph.node(self.py_name, **nvsg.get_attrs(self))
            # self._backwarded = not retain_graph  # only need to be set for MessageNode
            return digraph

        # TODO check memory leak
        queue = [
            self._itemize()
        ]  # priority queue; add id() since __eq__ is overloaded to compare values.
        while True:
            try:
                _, _, node = heapq.heappop(
                    queue
                )  # All the children of this node have been visited
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
                    if (
                        len(parent.parents) > 0 and parent._itemize() not in queue
                    ):  # and parent not in queue:
                        heapq.heappush(
                            queue, parent._itemize()
                        )  # put parent in the priority queue

                    if visualize:
                        # Plot the edge from parent to node
                        # Bypass chain of identity operators (for better visualization)
                        while (
                            get_op_name(parent.description) in IDENTITY_OPERATORS
                        ) and simple_visualization:
                            assert (
                                len(parent.parents) == 1
                            )  # identity operators should have only one parent
                            visited.add(
                                parent.py_name
                            )  # skip this node in visualization
                            parent = parent.parents[0]

                        edge = (
                            (node.py_name, parent.py_name)
                            if reverse_plot
                            else (parent.py_name, node.py_name)
                        )
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
        """Create and return a duplicate of the current Node object.

        Returns:
            Node: A clone of the current node.
        """
        import opto.trace.operators as ops

        return ops.clone(self)

    def detach(self):
        """Create and return a deep copy of the current instance of the Node class.

        Returns:
            Node: A deep copy of the current node.
        """
        return copy.deepcopy(self)

    # Get attribute and call operators
    def getattr(self, key):
        """Get the attribute of the node with the specified key.

        Args:
            key: The key of the attribute to get.

        Returns:
            Node: A node containing the requested attribute.
        """
        import opto.trace.operators as ops

        return ops.node_getattr(self, node(key))

    def call(self, fun: str, *args, **kwargs):
        """Call the function with the specified arguments and keyword arguments.

        Args:
            fun: The function to call.
            *args: The arguments to pass to the function.
            **kwargs: The keyword arguments to pass to the function.

        Returns:
            Node: The result of the function call wrapped in a node.
        """
        args = (node(arg) for arg in args)  # convert args to nodes
        kwargs = {k: node(v) for k, v in kwargs.items()}
        return self.getattr(fun)(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        """Call the function with the specified arguments and keyword arguments.

        Args:
            *args: The arguments to pass to the function.
            **kwargs: The keyword arguments to pass to the function.

        Returns:
            Node: The result of the function call wrapped in a node.

        Notes:
            By using the __call__ method, the Node object can be used as if it were a regular
            callable function, providing a seamless interface for function invocation.
        """
        import opto.trace.operators as ops

        output = ops.call(self, *args, **kwargs)
        return output

    # We overload magic methods that return a value. These methods return a MessageNode.
    # container magic methods
    def len(self):
        """Return the length of the node.

        Returns:
            Node: A node containing the length value.

        Notes:
            We overload magic methods that return a value. This method returns a MessageNode.
        """
        import opto.trace.operators as ops

        return ops.len_(self)

    def __getitem__(self, key):
        """Get the item at the specified key.

        Args:
            key: The key of the item to get.

        Returns:
            Node: A node containing the requested item.

        Notes:
            We overload magic methods that return a value. This method returns a MessageNode.
        """
        import opto.trace.operators as ops

        return ops.getitem(self, node(key))

    def __contains__(self, item):
        """Check if the item is contained in the node.

        Args:
            item: The item to check for containment.

        Returns:
            Node: A node containing the boolean result.

        Notes:
            We overload magic methods that return a value. This method returns a MessageNode.
        """
        import opto.trace.operators as ops

        return ops.in_(node(item), self)

    # Unary operators and functions
    def __pos__(self):
        """Return the positive value of the node.

        Returns:
            Node: A node containing the positive value.

        Notes:
            We overload magic methods that return a value. This method returns a MessageNode.
        """
        import opto.trace.operators as ops

        return ops.pos(self)

    def __neg__(self):
        """Return the negative value of the node.

        Returns:
            Node: A node containing the negative value.

        Notes:
            We overload magic methods that return a value. This method returns a MessageNode.
        """
        import opto.trace.operators as ops

        return ops.neg(self)

    def __abs__(self):
        """Return the absolute value of the node.

        Returns:
            Node: A node containing the absolute value.

        Notes:
            We overload magic methods that return a value. This method returns a MessageNode.
        """
        import opto.trace.operators as ops

        return ops.abs(self)

    def __invert__(self):
        """Return the inverted value of the node.

        Returns:
            Node: A node containing the inverted value.

        Notes:
            We overload magic methods that return a value. This method returns a MessageNode.
        """
        import opto.trace.operators as ops

        return ops.invert(self)

    def __round__(self, n=None):
        """Return the rounded value of the node.

        Args:
            n: The number of decimal places to round to (optional).

        Returns:
            Node: A node containing the rounded value.

        Notes:
            We overload magic methods that return a value. This method returns a MessageNode.
        """
        import opto.trace.operators as ops

        return ops.round(self, node(n) if n is not None else None)

    def __floor__(self):
        """Return the floor value of the node.

        Returns:
            Node: A node containing the floor value.

        Notes:
            We overload magic methods that return a value. This method returns a MessageNode.
        """
        import opto.trace.operators as ops

        return ops.floor(self)

    def __ceil__(self):
        """Return the ceiling value of the node.

        Returns:
            Node: A node containing the ceiling value.

        Notes:
            We overload magic methods that return a value. This method returns a MessageNode.
        """
        import opto.trace.operators as ops

        return ops.ceil(self)

    def __trunc__(self):
        """Return the truncated value of the node.

        Returns:
            Node: A node containing the truncated value.

        Notes:
            We overload magic methods that return a value. This method returns a MessageNode.
        """
        import opto.trace.operators as ops

        return ops.trunc(self)

    # Normal arithmetic operators
    def __add__(self, other):
        """Return the sum of the node and another value.

        Args:
            other: The value to add to the node.

        Returns:
            Node: A node containing the sum.

        Notes:
            We overload magic methods that return a value. This method returns a MessageNode.
        """
        import opto.trace.operators as ops

        if type(self._data) is str:
            return ops.concat(self, node(other))
        else:
            return ops.add(self, node(other))

    def __radd__(self, other):
        """Return the sum of another value and the node.

        Args:
            other: The value to add to the node.

        Returns:
            Node: A node containing the sum.

        Notes:
            We overload magic methods that return a value. This method returns a MessageNode.
        """
        return node(other) + self

    def __sub__(self, other):
        """Return the difference between the node and another value.

        Args:
            other: The value to subtract from the node.

        Returns:
            Node: A node containing the difference.

        Notes:
            We overload magic methods that return a value. This method returns a MessageNode.
        """
        import opto.trace.operators as ops

        return ops.subtract(self, node(other))

    def __rsub__(self, other):
        """Return the difference between another value and the node.

        Args:
            other: The value to subtract the node from.

        Returns:
            Node: A node containing the difference.

        Notes:
            We overload magic methods that return a value. This method returns a MessageNode.
        """
        return node(other) - self

    def __mul__(self, other):
        """Return the product of the node and another value.

        Args:
            other: The value to multiply the node by.

        Returns:
            Node: A node containing the product.

        Notes:
            We overload magic methods that return a value. This method returns a MessageNode.
        """
        import opto.trace.operators as ops

        return ops.multiply(self, node(other))

    def __rmul__(self, other):
        """Return the product of another value and the node.

        Args:
            other: The value to multiply the node by.

        Returns:
            Node: A node containing the product.

        Notes:
            We overload magic methods that return a value. This method returns a MessageNode.
        """
        return self * node(other)

    def __floordiv__(self, other):
        """Return the floor division of the node by another value.

        Args:
            other: The value to divide the node by.

        Returns:
            Node: A node containing the floor division result.

        Notes:
            We overload magic methods that return a value. This method returns a MessageNode.
        """
        import opto.trace.operators as ops

        return ops.floor_divide(self, node(other))

    def __rfloordiv__(self, other):
        """Return the floor division of another value by the node.

        Args:
            other: The value to divide by the node.

        Returns:
            Node: A node containing the floor division result.

        Notes:
            We overload magic methods that return a value. This method returns a MessageNode.
        """
        return node(other) // self

    def __truediv__(self, other):
        """Return the true division of the node by another value.

        Args:
            other: The value to divide the node by.

        Returns:
            Node: A node containing the division result.

        Notes:
            We overload magic methods that return a value. This method returns a MessageNode.
        """
        import opto.trace.operators as ops

        return ops.divide(self, node(other))

    def __rtruediv__(self, other):
        """Return the true division of another value by the node.

        Args:
            other: The value to divide by the node.

        Returns:
            Node: A node containing the division result.

        Notes:
            We overload magic methods that return a value. This method returns a MessageNode.
        """
        return node(other) / self

    def __div__(self, other):
        """Return the division of the node by another value.

        Args:
            other: The value to divide the node by.

        Returns:
            Node: A node containing the division result.

        Notes:
            We overload magic methods that return a value. This method returns a MessageNode.
        """
        import opto.trace.operators as ops

        return ops.divide(self, node(other))

    def __rdiv__(self, other):
        """Return the division of another value by the node.

        Args:
            other: The value to divide by the node.

        Returns:
            Node: A node containing the division result.

        Notes:
            We overload magic methods that return a value. This method returns a MessageNode.
        """
        return node(other) / self

    def __mod__(self, other):
        """Return the modulo of the node by another value.

        Args:
            other: The value to divide the node by.

        Returns:
            Node: A node containing the modulo result.

        Notes:
            We overload magic methods that return a value. This method returns a MessageNode.
        """
        import opto.trace.operators as ops

        return ops.mod(self, node(other))

    def __rmod__(self, other):
        """Return the modulo of another value by the node.

        Args:
            other: The value to divide by the node.

        Returns:
            Node: A node containing the modulo result.

        Notes:
            We overload magic methods that return a value. This method returns a MessageNode.
        """
        return node(other) % self

    def __divmod__(self, other):
        """Return the division and modulo of the node by another value.

        Args:
            other: The value to divide the node by.

        Returns:
            Node: A node containing the division and modulo results.

        Notes:
            We overload magic methods that return a value. This method returns a MessageNode.
        """
        import opto.trace.operators as ops

        return ops.node_divmod(self, node(other))

    def __rdivmod__(self, other):
        """Return the division and modulo of another value by the node.

        Args:
            other: The value to divide by the node.

        Returns:
            Node: A node containing the division and modulo results.

        Notes:
            We overload magic methods that return a value. This method returns a MessageNode.
        """
        return divmod(node(other), self)

    def __pow__(self, other):
        """Return the power of the node raised to another value.

        Args:
            other: The exponent value.

        Returns:
            Node: A node containing the power result.

        Notes:
            We overload magic methods that return a value. This method returns a MessageNode.
        """
        import opto.trace.operators as ops

        return ops.power(self, node(other))

    def __rpow__(self, other):
        """Return the power of another value raised to the node.

        Args:
            other: The base value.

        Returns:
            Node: A node containing the power result.

        Notes:
            We overload magic methods that return a value. This method returns a MessageNode.
        """
        return node(other) ** self

    def __lshift__(self, other):
        """Return the left shift of the node by another value.

        Args:
            other: The number of positions to shift.

        Returns:
            Node: A node containing the left shift result.

        Notes:
            We overload magic methods that return a value. This method returns a MessageNode.
        """
        import opto.trace.operators as ops

        return ops.lshift(self, node(other))

    def __rlshift__(self, other):
        """Return the left shift of another value by the node.

        Args:
            other: The value to shift.

        Returns:
            Node: A node containing the left shift result.

        Notes:
            We overload magic methods that return a value. This method returns a MessageNode.
        """
        return node(other) << self

    def __rshift__(self, other):
        """Return the right shift of the node by another value.

        Args:
            other: The number of positions to shift.

        Returns:
            Node: A node containing the right shift result.

        Notes:
            We overload magic methods that return a value. This method returns a MessageNode.
        """
        import opto.trace.operators as ops

        return ops.rshift(self, node(other))

    def __rrshift__(self, other):
        """Return the right shift of another value by the node.

        Args:
            other: The value to shift.

        Returns:
            Node: A node containing the right shift result.

        Notes:
            We overload magic methods that return a value. This method returns a MessageNode.
        """
        return node(other) >> self

    def __and__(self, other):
        """Return the bitwise AND of the node and another value.

        Args:
            other: The value to AND with.

        Returns:
            Node: A node containing the AND result.

        Notes:
            We overload magic methods that return a value. This method returns a MessageNode.
        """
        import opto.trace.operators as ops

        return ops.and_(self, node(other))

    def __rand__(self, other):
        """Return the bitwise AND of another value and the node.

        Args:
            other: The value to AND with.

        Returns:
            Node: A node containing the AND result.

        Notes:
            We overload magic methods that return a value. This method returns a MessageNode.
        """
        return node(other) & self

    def __or__(self, other):
        """Return the bitwise OR of the node and another value.

        Args:
            other: The value to OR with.

        Returns:
            Node: A node containing the OR result.

        Notes:
            We overload magic methods that return a value. This method returns a MessageNode.
        """
        import opto.trace.operators as ops

        return ops.or_(self, node(other))

    def __ror__(self, other):
        """Return the bitwise OR of another value and the node.

        Args:
            other: The value to OR with.

        Returns:
            Node: A node containing the OR result.

        Notes:
            We overload magic methods that return a value. This method returns a MessageNode.
        """
        return node(other) | self

    def __xor__(self, other):
        """Return the bitwise XOR of the node and another value.

        Args:
            other: The value to XOR with.

        Returns:
            Node: A node containing the XOR result.

        Notes:
            We overload magic methods that return a value. This method returns a MessageNode.
        """
        import opto.trace.operators as ops

        return ops.xor(self, node(other))

    def __rxor__(self, other):
        """Return the bitwise XOR of another value and the node.

        Args:
            other: The value to XOR with.

        Returns:
            Node: A node containing the XOR result.

        Notes:
            We overload magic methods that return a value. This method returns a MessageNode.
        """
        return node(other) ^ self

    def __iter__(self):
        """Return an iterator for the node.

        Returns:
            iterator: An iterator over the node's data.

        Notes:
            The Node object must have a data attribute that is a list, tuple, set, or dictionary.
            The iterate function called by __iter__ handles the conversion of sets to lists and wraps items in lists or dictionaries with node objects.
        """
        import opto.trace.iterators as it

        return it.iterate(self)

    def __len__(self):
        """Return the length of the node.

        Returns:
            int: The length of the node's data.

        Notes:
            __len__ restricts return type to be integer.
            Therefore, this method only returns integer.
            If a Node/MessageNode is desired to be returned, call node.len() instead.
        """
        return len(self._data)

    # for logic operators
    # case 1: used in if-statement, then we should return a bool
    # case 2: used else-where, then we should return Node(bool)
    # we can't quite distinguish myopically, so...in here, we prioritize case 1
    def __lt__(self, other):
        """Check if the node is less than another value.

        Args:
            other: The value to compare the node to.

        Returns:
            Node: A node containing the comparison result.

        Notes:
            If a logic operator is used in an if-statement, it will return a boolean value.
            Otherwise, it will return a MessageNode.
        """
        import opto.trace.operators as ops

        return ops.lt(self, node(other))
        # if isinstance(other, Node):
        #     other = other.data
        # return self._data < other

    def __le__(self, other):
        """Check if the node is less than or equal to another value.

        Args:
            other: The value to compare the node to.

        Returns:
            Node: A node containing the comparison result.

        Notes:
            If a logic operator is used in an if-statement, it will return a boolean value.
            Otherwise, it will return a MessageNode.
        """
        import opto.trace.operators as ops

        return ops.le(self, node(other))
        # if isinstance(other, Node):
        #     other = other.data
        # return self._data <= other

    def __gt__(self, other):
        """Check if the node is greater than another value.

        Args:
            other: The value to compare the node to.

        Returns:
            Node: A node containing the comparison result.

        Notes:
            If a logic operator is used in an if-statement, it will return a boolean value.
            Otherwise, it will return a MessageNode.
        """
        import opto.trace.operators as ops

        return ops.gt(self, node(other))
        # if isinstance(other, Node):
        #     other = other.data
        # return self._data > other

    def __ge__(self, other):
        """Check if the node is greater than or equal to another value.

        Args:
            other: The value to compare the node to.

        Returns:
            Node: A node containing the comparison result.

        Notes:
            If a logic operator is used in an if-statement, it will return a boolean value.
            Otherwise, it will return a MessageNode.
        """
        import opto.trace.operators as ops

        return ops.ge(self, node(other))
        # if isinstance(other, Node):
        #     other = other.data
        # return self._data >= other

    # this creates a lot of issues if we return Node
    # instead of bool (for example "in" operator will not work)
    def __eq__(self, other):
        """Check if the node is equal to another value.

        Args:
            other: The value to compare the node to.

        Returns:
            bool: True if the values are equal, False otherwise.

        Notes:
            __eq__ restricts return type to be bool; otherwise, it will create issues (for example, the "in" operator will not work).
        """
        # import opto.trace.operators as ops
        # return ops.eq(self, node(other))
        if isinstance(other, Node):
            other = other.data
        return self._data == other

    def eq(self, other):
        """Check if the node is equal to another value.

        Args:
            other: The value to compare the node to.

        Returns:
            Node: A node containing the comparison result.

        Notes:
            If a logic operator is used in an if-statement, it will return a boolean value.
            Otherwise, it will return a MessageNode.
        """
        import opto.trace.operators as ops

        return ops.eq(self, node(other))

    def neq(self, other):
        """Check if the node is not equal to another value.

        Args:
            other: The value to compare the node to.

        Returns:
            Node: A node containing the comparison result.

        Notes:
            If a logic operator is used in an if-statement, it will return a boolean value.
            Otherwise, it will return a MessageNode.
        """
        import opto.trace.operators as ops

        return ops.neq(self, node(other))

    def __hash__(self):
        """Return the hash value of the node.

        Returns:
            int: The hash value of the node.
        """
        return super().__hash__()

    def __bool__(self):
        """Return the boolean value of the node.

        Returns:
            bool: The boolean value of the node's data.

        Notes:
            The access to the `_data` attribute happening in this method is not traced.
        """
        # not tracing this conversion
        return bool(self._data)

    # string operators
    def format(self, *args, **kwargs):
        if type(self._data) is not str:
            raise AttributeError(
                f"{type(self._data)} object has no attribute 'format'."
            )

        import opto.trace.operators as ops

        return ops.format(self, *args, **kwargs)

    def capitalize(self):
        if type(self._data) is not str:
            raise AttributeError(
                f"{type(self._data)} object has no attribute 'capitalize'."
            )
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
            raise AttributeError(
                f"{type(self._data)} object has no attribute 'swapcase'."
            )
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
            raise AttributeError(
                f"{type(self._data)} object has no attribute 'replace'."
            )
        import opto.trace.operators as ops

        return ops.replace(self, node(old), node(new), count)

    def join(self, seq):
        if type(self._data) is not str:
            raise AttributeError(f"{type(self._data)} object has no attribute 'join'.")
        # test if seq is a sequence
        try:
            iter(seq)
        except TypeError:
            raise TypeError("Can only join an iterable.")

        import opto.trace.operators as ops

        return ops.join(self, *seq)

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
            description = (
                "[ParameterNode] This is a ParameterNode in a computational graph."
            )

        matched = re.match(r"^\[([^\[\]]+)\]", description)
        if not matched:
            description = "[ParameterNode] " + description.strip()

        super().__init__(
            value,
            name=name,
            trainable=trainable,
            description=description,
            constraint=constraint,
            info=info,
        )
        self._dependencies["parameter"].add(self)

    def __str__(self) -> str:
        # str(node) allows us to look up in the feedback dictionary easily
        return (
            f"ParameterNode: ({self.name}, dtype={type(self._data)}, data={self._data})"
        )


class MessageNode(Node[T]):
    """A node representing the output of an operator.

    The description string should begin with [operator_name] followed by details about the operator.
    When referring to inputs in the description, use either:
    - The keys in args (if args is a dict)
    - The names of the nodes in args (if args is a list)

    Examples:
        >>> MessageNode(node_a, inputs=[node_a],
        >>>        description="[identity] This is an identity operator.")
        >>> MessageNode(copy_node_a, inputs=[node_a],
        >>>        description="[copy] This is a copy operator.")
        >>> MessageNode(1, inputs={'a':node_a, 'b':node_b},
        >>>        description="[Add] This is an add operator of a and b.")

    Attributes:
        value: The output value of the operator
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
        super().__init__(
            value, name=name, description=description, constraint=constraint, info=info
        )

        assert isinstance(inputs, list) or isinstance(
            inputs, dict
        ), "Inputs to MessageNode must be a list or a dict."
        # If inputs is not a dict, we create a dict with the names of the nodes as keys
        if isinstance(inputs, list):
            inputs = {v.name: v for v in inputs}
        self._inputs = inputs

        # If not tracing, MessageNode would just behave like a Node.
        if not GRAPH.TRACE:
            assert (
                len(self._inputs) == 0
            ), "MessageNode should have no inputs when not tracing."

        # Add parents if we are tracing
        for k, v in self._inputs.items():
            assert isinstance(v, Node), f"Input {k} is not a Node."
            self._add_parent(v)
            self._add_dependencies(
                v
            )  # Initializes the dependencies on parameter and expandable nodes

        if len(self.hidden_dependencies) > 0:
            self._dependencies["expandable"].add(self)

    @property
    def inputs(self):
        """(Union[List[Node], Dict[str, Node]]): Input nodes to the operator"""
        return copy.copy(self._inputs)

    def __str__(self) -> str:
        # str(node) allows us to look up in the feedback dictionary easily
        return (
            f"MessageNode: ({self.name}, dtype={type(self._data)}, data={self._data})"
        )

    def _add_feedback(self, child, feedback):
        """Add feedback from a child."""
        super()._add_feedback(child, feedback)
        assert (
            len(self._feedback[child]) == 1
        ), "MessageNode should have only one feedback from each child."

    @property
    def hidden_dependencies(self):  # this needs to be recursive
        """Returns the set of hidden dependencies that are not visible in the current graph level."""
        diff = set()

        inputs, output = [None], None
        if isinstance(self.info, dict):
            if "inputs" in self.info:
                inputs = list(self.info["inputs"]["args"]) + list(
                    self.info["inputs"]["kwargs"].values()
                )
            if "output" in self.info:
                output = self.info["output"]

        if (
            isinstance(self.info, dict)
            and isinstance(output, Node)
            and all(isinstance(i, Node) for i in inputs)
        ):  # traceable code
            # The inner function is traceable.
            diff = diff | (
                output.parameter_dependencies - self.parameter_dependencies
            )  # add extra parameters explicitly used in the inner function
            extra_expandable = (
                output.expandable_dependencies - self.expandable_dependencies
            )
            for n in extra_expandable:  # add extra hidden dependencies
                diff = diff | n.hidden_dependencies
        return diff

    def _add_dependencies(self, parent):
        assert parent is not self, "Cannot add self as a parent."
        assert isinstance(
            parent, Node
        ), f"{parent} is {type(parent)}, which is not a Node."
        self._dependencies["parameter"] = (
            self._dependencies["parameter"] | parent._dependencies["parameter"]
        )
        self._dependencies["expandable"] = (
            self._dependencies["expandable"] | parent._dependencies["expandable"]
        )


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

        value = f"({error_type}) {str(e)}"
        super().__init__(
            value,
            inputs=inputs,
            description=description,
            constraint=constraint,
            name=name,
            info=info,
        )

    def create_feedback(self, style="simple"):
        assert style in ("simple", "full")
        feedback = self._data
        if style == "full":
            if type(self.info) is dict and self.info.get("error_comment") is not None:
                feedback = self.info["error_comment"]
        return feedback


if __name__ == "__main__":
    x = node("Node X")
    y = node("Node Y")
    z = MessageNode(
        "Node Z",
        inputs={"x": x, "y": y},
        description="[Add] This is an add operator of x and y.",
    )
    print(x.name, y.name)
    print([p.name for p in z.parents])

    x: AbstractNode[str] = node("Node X")
    x: Node[str] = node("Node X")
    x: ParameterNode[str] = ParameterNode("Node X", trainable=True)
    x: MessageNode[str] = MessageNode(
        "Node X",
        inputs={"x": x, "y": y},
        description="[Add] This is an add operator of x and y.",
    )
