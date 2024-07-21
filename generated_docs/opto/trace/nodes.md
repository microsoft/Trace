## FunctionDef node(message, name, trainable, constraint)
**node**: The function of node is to create a Node object from a message. If the message is already a Node, it will be returned as is. This function is provided for the convenience of the user and should be used instead of directly invoking the Node class.

**parameters**:
- message: The message to create the Node from.
- name: (optional) The name of the Node.
- trainable: (optional) A boolean indicating whether the Node is trainable or not. Default is False.
- constraint: (optional) A constraint on the Node.

**Code Description**: The node function is a versatile function that allows users to create Node objects from messages. It takes in a message and optional parameters such as name, trainable, and constraint. 

The function first checks if the trainable parameter is True. If it is, it checks if the message is already a Node. If it is, it extracts the underlying data and updates the name if a new name is provided. It then creates a ParameterNode object with the extracted data, name, trainable set to True, and the provided constraint. If the message is not already a Node, it creates a new ParameterNode object with the message as the data, the provided name, trainable set to True, and the provided constraint.

If the trainable parameter is False, the function checks if the message is already a Node. If it is, it checks if a name is provided. If a name is provided, it issues a warning that the name is ignored because the message is already a Node. It then returns the message as is. If the message is not already a Node, it creates a new Node object with the message as the data, the provided name, and the provided constraint.

**Note**:
- The node function is a convenient way to create Node objects from messages.
- The trainable parameter determines whether the created Node is trainable or not.
- The constraint parameter allows users to specify a constraint on the created Node.

**Output Example**: A possible return value of the node function could be a ParameterNode object with the extracted data, name, trainable set to True, and the provided constraint.
## ClassDef Graph
**Graph**: The function of Graph is to serve as a registry of all the nodes, forming a Directed Acyclic Graph (DAG).

**attributes**: The attributes of this Class.
· TRACE: A class-level attribute that determines whether the graph is traced when creating MessageNode. It is set to True by default.
· _nodes: An instance-level attribute, which is a defaultdict of lists, used as a lookup table to find nodes by name.

**Code Description**: The Graph class is designed to manage and organize nodes in a Directed Acyclic Graph (DAG). It provides methods to register nodes, clear the graph, retrieve nodes by name, and identify root nodes.

- The `__init__` method initializes the Graph object, setting up the `_nodes` attribute as a defaultdict of lists to store nodes by their names.

- The `clear` method removes all nodes from the graph by deleting each node and reinitializing the `_nodes` attribute.

- The `register` method adds a node to the graph. It ensures the node is an instance of the Node class and that its name follows the expected format (containing a colon). The method also handles name scoping and assigns a unique name to the node based on its position in the list.

- The `get` method retrieves a node by its name, which includes an identifier. It splits the name to find the correct node in the `_nodes` dictionary.

- The `roots` property returns a list of all root nodes in the graph. A root node is identified by its `is_root` attribute.

- The `__str__` method provides a string representation of the `_nodes` attribute, useful for debugging and logging.

- The `__len__` method returns the total number of nodes in the graph by summing the lengths of all lists in the `_nodes` dictionary.

**Note**: 
- The `TRACE` attribute controls whether the graph is traced during the creation of MessageNode instances.
- The `register` method assumes that elements in `_nodes` are never removed, which is important for maintaining the integrity of node names.

**Output Example**: 
- When calling the `__str__` method, the output might look like:
  ```
  defaultdict(<class 'list'>, {'node1': [<Node object at 0x...>], 'node2': [<Node object at 0x...>]})
  ```
- When calling the `__len__` method, the output might be:
  ```
  5
  ```
### FunctionDef __init__(self)
**__init__**: The function of __init__ is to initialize an instance of the Graph class by setting up an internal data structure to store nodes.

**parameters**: The parameters of this Function.
· This function does not take any parameters.

**Code Description**: The __init__ function initializes an instance of the Graph class. It sets up an internal attribute `_nodes`, which is a defaultdict with lists as the default factory. This defaultdict will be used as a lookup table to store and retrieve nodes by their names. Each key in the `_nodes` dictionary represents a node name, and the corresponding value is a list of nodes associated with that name. This structure allows for efficient organization and retrieval of nodes within the graph.

**Note**: 
- The defaultdict from the collections module is used to automatically handle missing keys by initializing them with an empty list.
- This function does not require any arguments and is called automatically when a new instance of the Graph class is created.
***
### FunctionDef clear(self)
**clear**: The function of clear is to remove all nodes from the graph and reset the internal node storage.

**parameters**: The parameters of this Function.
· This function does not take any parameters other than the implicit self parameter.

**Code Description**: The clear function is designed to empty the graph of all its nodes. It iterates over the current nodes stored in the _nodes attribute, which is a dictionary, and deletes each node. After all nodes have been deleted, it reinitializes the _nodes attribute to an empty defaultdict of lists. This ensures that the graph is completely cleared and ready to be repopulated with new nodes if necessary.

The function is called in unit tests located in tests\unit_tests\test_backward.py and tests\unit_tests\test_optimizer.py. These tests likely use the clear function to reset the state of the graph between test cases, ensuring that each test runs with a clean slate and is not affected by the state left by previous tests.

**Note**: 
- This function should be used with caution as it irreversibly deletes all nodes in the graph.
- After calling clear, any references to the previously stored nodes will become invalid.
- Ensure that any necessary data is saved or processed before calling this function, as it will reset the graph's state completely.
***
### FunctionDef register(self, node)
**register**: The function of register is to add a node to the graph.

**parameters**:
- self: The instance of the class.
- node: The node object to be registered in the graph.

**Code Description**:
The `register` function is a method of the `Graph` class in the `nodes.py` file of the `trace` module. It is used to add a node to the graph. The function takes in the `self` parameter, which represents the instance of the class, and the `node` parameter, which is the node object to be registered.

The function first checks if the `node` parameter is an instance of the `Node` class using the `isinstance` function. If it is not, an `AssertionError` is raised.

Next, the function checks if the name of the node contains exactly one ":" character by splitting the name using the ":" delimiter and checking the length of the resulting list. If the length is not equal to 2, an `AssertionError` is raised. This check ensures that the name of the node follows the required format.

After that, the function splits the name of the node using the ":" delimiter and assigns the first part of the split to the `name` variable. This is done to separate the name from the version number.

The function then checks if there are any name scopes defined in the `NAME_SCOPES` list. If the length of the list is greater than 0, the name is prefixed with the last scope in the list followed by a "/". This allows for scoping of node names.

Finally, the function adds the node to the `_nodes` dictionary using the modified name as the key. The `_name` attribute of the node is set to the modified name followed by the index of the node in the list of nodes with the same name. This index is obtained by subtracting 1 from the length of the list of nodes with the same name.

**Note**:
- The `register` function should only be called after the node has been properly initialized and its name has been set.
- The function assumes that elements in the `_nodes` dictionary never get removed.

**Output Example**:
If the name of the node is "node:0", the `register` function will add the node to the `_nodes` dictionary with the key "node" and set the `_name` attribute of the node to "node:0".
***
### FunctionDef get(self, name)
**get**: The function of get is to retrieve a specific node from the graph based on a given name and identifier.

**parameters**: The parameters of this Function.
· name: A string in the format "name:id", where "name" is the name of the node and "id" is the identifier of the node.

**Code Description**: The get function is designed to extract and return a specific node from a graph structure. The input parameter 'name' is expected to be a string formatted as "name:id". The function first splits this string into two parts: 'name' and 'id', using the colon (":") as the delimiter. The 'name' part represents the name of the node, and the 'id' part represents the identifier of the node, which is then converted to an integer. The function then accesses the '_nodes' dictionary attribute of the graph object, using the 'name' as the key to retrieve the list of nodes associated with that name. Finally, it returns the node at the position specified by the integer 'id' within that list.

**Note**: 
- Ensure that the 'name' parameter is correctly formatted as "name:id" before calling this function.
- The function assumes that the '_nodes' attribute is a dictionary where each key is a node name and the corresponding value is a list of nodes.
- The 'id' should be a valid index within the list of nodes for the given 'name'.

**Output Example**: 
If the '_nodes' dictionary is structured as follows:
```python
_nodes = {
    "nodeA": ["nodeA_0", "nodeA_1"],
    "nodeB": ["nodeB_0"]
}
```
Calling `get("nodeA:1")` would return `"nodeA_1"`.
***
### FunctionDef roots(self)
**roots**: The function of roots is to return a list of root nodes from the graph.

**parameters**: This function does not take any parameters.

**Code Description**: The `roots` function iterates over the values in the `_nodes` dictionary of the `Graph` object. The `_nodes` dictionary contains lists of nodes. For each node in these lists, the function checks if the node is a root node by evaluating the `is_root` attribute of the node. If the `is_root` attribute is `True`, the node is included in the resulting list. The function ultimately returns a list of all nodes that are identified as root nodes.

**Note**: 
- Ensure that the nodes in the `_nodes` dictionary have the `is_root` attribute properly set to `True` for root nodes and `False` for non-root nodes.
- The function assumes that `_nodes` is a dictionary where the values are lists of node objects.

**Output Example**: 
If the `_nodes` dictionary contains the following structure:
```python
_nodes = {
    'group1': [Node1, Node2],
    'group2': [Node3, Node4]
}
```
and `Node1` and `Node3` have their `is_root` attribute set to `True`, while `Node2` and `Node4` have it set to `False`, the `roots` function will return:
```python
[Node1, Node3]
```
***
### FunctionDef __str__(self)
**__str__**: The function of __str__ is to return a string representation of the Graph object.

**parameters**: The parameters of this Function.
· None: This method does not take any parameters.

**Code Description**: The __str__ method is a special method in Python that is used to define the string representation of an object. In this implementation, the __str__ method returns the string representation of the `_nodes` attribute of the Graph object. The `_nodes` attribute is expected to be a collection (such as a list or dictionary) that holds the nodes of the graph. By converting `_nodes` to a string, the method provides a human-readable format of the graph's nodes, which can be useful for debugging and logging purposes.

**Note**: 
- Ensure that the `_nodes` attribute is properly initialized and contains the nodes of the graph before calling the __str__ method.
- The readability and usefulness of the output depend on the structure and content of the `_nodes` attribute.

**Output Example**: 
If the `_nodes` attribute is a list of node names, such as `['A', 'B', 'C']`, the __str__ method will return the string "['A', 'B', 'C']". If `_nodes` is a dictionary representing nodes and their connections, such as `{'A': ['B', 'C'], 'B': ['A'], 'C': ['A']}`, the method will return the string "{'A': ['B', 'C'], 'B': ['A'], 'C': ['A']}".
***
### FunctionDef __len__(self)
**__len__**: The function of __len__ is to return the number of nodes in the graph.

**parameters**: The parameters of this Function.
· self: Refers to the instance of the Graph class.

**Code Description**: The __len__ method calculates the total number of nodes in the graph. It does this by iterating over the values in the self._nodes dictionary, where each value is a list representing the connections or edges of a particular node. The method uses a list comprehension to get the length of each list (i.e., the number of connections for each node) and then sums these lengths to get the total number of nodes. Finally, it returns this sum as the result.

**Note**: This method assumes that the self._nodes attribute is a dictionary where each key is a node and each value is a list of connections for that node. The method will not work correctly if self._nodes is not structured in this way.

**Output Example**: If the graph has 3 nodes with the following connections:
- Node A connected to Node B and Node C
- Node B connected to Node A
- Node C connected to Node A

The return value of __len__ would be 3.
***
## ClassDef AbstractNode
**AbstractNode**: The function of AbstractNode is to represent an abstract data node in a directed graph.

**attributes**:
- `data`: The data stored in the node.
- `parents`: The list of parent nodes.
- `children`: The list of child nodes.
- `name`: The name of the node.
- `py_name`: The name of the node without the ":" character.
- `id`: The ID of the node.
- `level`: The level of the node in the graph.
- `is_root`: A boolean indicating whether the node is a root node.
- `is_leaf`: A boolean indicating whether the node is a leaf node.

**Code Description**: The `AbstractNode` class represents an abstract data node in a directed graph. It is a generic class that can store any type of data. The node can have multiple parents and children, forming a directed graph structure. The node has a name, which is used to identify it within the graph. The `py_name` attribute is the same as the name attribute, but with the ":" character removed. The `id` attribute is extracted from the name and represents a version number.

The node can be initialized with a value, an optional name, and an optional trainable flag. If the value is an instance of the `Node` class, the node will be initialized as a reference to that node, otherwise, the value will be stored directly in the node. The default name is generated based on the type of the value and a version number.

The `AbstractNode` class provides several properties to access its attributes. The `data` property allows access to the stored data. If the node is being traced within a context, the `data` property adds the node to the list of used nodes. The `parents` property returns a list of parent nodes, and the `children` property returns a list of child nodes. The `name` property returns the name of the node, and the `py_name` property returns the name without the ":" character. The `id` property returns the version number extracted from the name. The `level` property returns the level of the node in the graph. The `is_root` property returns True if the node has no parents, and the `is_leaf` property returns True if the node has no children.

The `AbstractNode` class also provides internal methods to add parents and children to the node. The `_add_child` method adds a child node to the node's list of children. The `_add_parent` method adds a parent node to the node's list of parents and updates the level of the node based on the parent's level.

The `AbstractNode` class overrides the `__str__` method to provide a string representation of the node. The representation includes the name, the type of the data, and the data itself.

The `AbstractNode` class implements the `__deepcopy__` method to create a deep copy of the node. This allows the node to be detached from the original graph.

The `AbstractNode` class provides comparison methods `lt` and `gt` to compare the levels of two nodes.

**Note**: The `AbstractNode` class is meant to be subclassed and extended to create specific types of nodes.

**Output Example**:
```
Node: (node_name, dtype=<class 'int'>, data=10)
```
### FunctionDef __init__(self, value)
**__init__**: The function of __init__ is to initialize an instance of the AbstractNode class.

**parameters**:
- self: The instance of the class.
- value: The value to be assigned to the node.
- name: The name of the node (optional).
- trainable: A boolean indicating whether the node is trainable or not (optional).

**Code Description**:
The `__init__` function is the constructor of the AbstractNode class. It takes in the `self` parameter, which represents the instance of the class, and the `value`, `name`, and `trainable` parameters, which are used to initialize the attributes of the node.

The function starts by initializing the `_parents`, `_children`, and `_level` attributes to empty lists and 0 respectively. These attributes are used to keep track of the parent and child nodes of the current node, as well as the level of the node in the graph.

Next, the function generates a default name for the node based on the type of the `value` parameter. If the `name` parameter is provided, it is appended to the default name. The format of the name is "type:version", where the version is set to 0 if no name is provided.

After that, the function checks if the `value` parameter is an instance of the Node class. If it is, the `_data` attribute of the current node is set to the `_data` attribute of the `value` parameter, and the `_name` attribute is set to the `_name` attribute of the `value` parameter if no name is provided. Otherwise, the `_data` attribute is set to the `value` parameter itself, and the `_name` attribute is set to the default name.

Finally, the function calls the `register` function of the GRAPH object to register the current node in the graph.

**Note**:
- The `__init__` function should be called to create a new instance of the AbstractNode class.
- The `value` parameter can be any type of value.
- The `name` parameter is optional and can be used to provide a custom name for the node.
- The `trainable` parameter is optional and can be used to indicate whether the node is trainable or not.
- The `register` function should only be called after the node has been properly initialized and its name has been set.
***
### FunctionDef data(self)
**data**: The function of data is to retrieve the internal data of a node, potentially adding the node to a list of used nodes if certain conditions are met.

**parameters**: The parameters of this Function.
· self: Refers to the instance of the class that contains this method.

**Code Description**: The data function is designed to return the internal data of a node object. It first checks if there are any nodes in the USED_NODES list and if the GRAPH.TRACE flag is set to True. If both conditions are met, it adds the current node (self) to the USED_NODES list. This indicates that the node is being used within a tracing context. Finally, the function returns the value of the node's internal data by accessing the "_data" attribute.

This function is utilized in various parts of the project to access the data stored within nodes. For instance:
- In the node_to_function_feedback function in opto\optimizers\function_optimizer.py, it retrieves node data to convert a TraceGraph to a FunctionFeedback.
- In the construct_update_dict method of the FunctionOptimizer class, it converts suggestions into the appropriate data types by accessing node data.
- In the __next__ method of the SeqIterable class in opto\trace\containers.py, it iterates over a wrapped list of nodes and accesses their data.
- In the ExecutionError class's __init__ and __str__ methods in opto\trace\errors.py, it retrieves the data of an exception node to initialize and represent the error.
- In the get_label method of the NodeVizStyleGuide class in opto\trace\nodes.py, it generates labels for nodes by accessing their data.
- In the _set method of the Node class in opto\trace\nodes.py, it sets the value of a node, unwrapping it if necessary.
- In the trace_fun method of the Foo class in tests\unit_tests\test_bundle.py, it prints the data of a node during a trace function.

**Note**: This function assumes that the "_data" attribute exists within the node object. If this attribute is not present, an AttributeError will be raised.

**Output Example**: A possible return value of the code could be any data type stored in the "_data" attribute of the node, such as an integer, string, list, or custom object. For example, if the "_data" attribute contains the integer 42, the function will return 42.
***
### FunctionDef parents(self)
**parents**: The function of parents is to return the parents of the current node.
**parameters**:
- self: The current node object.
**Code Description**:
The `parents` function is a method of the `AbstractNode` class in the `nodes.py` module. It returns the parents of the current node. The parents are stored in the `_parents` attribute of the node object.

The function takes only one parameter, `self`, which refers to the current node object. It is used to access the `_parents` attribute and return its value.

The `_parents` attribute is a list that contains the parent nodes of the current node. These parent nodes are the nodes that have an edge pointing to the current node in the graph.

The `parents` function is called by several objects in the project. For example, it is called by the `is_root` function in the `AbstractNode` class, which checks if the current node is a root node by checking if it has any parents. It is also called by the `backward` function in the `Node` class, which performs a backward pass in the graph by propagating feedback from the current node to its parents.

**Note**: The `parents` function is a basic method that provides access to the parents of a node. It is an essential part of the graph structure and is used in various operations such as graph traversal and feedback propagation.

**Output Example**: 
If the current node has two parents, the `parents` function will return a list containing the two parent nodes.
***
### FunctionDef children(self)
**children**: The function of children is to return the list of child nodes associated with the current node.

**parameters**: This function does not take any parameters.

**Code Description**: The `children` function is a method of the `AbstractNode` class. It returns the `_children` attribute of the instance, which is a list containing the child nodes of the current node. This method is essential for accessing the hierarchical structure of nodes, allowing traversal and manipulation of the node tree.

The `children` method is called by the `is_leaf` method within the same `AbstractNode` class. The `is_leaf` method uses `children` to determine if the current node is a leaf node (i.e., it has no children). Specifically, `is_leaf` checks if the length of the list returned by `children` is zero, indicating that the node has no children and is therefore a leaf.

Additionally, the `children` method is referenced in the `opto\trace\bundle.py` file and the `tests\unit_tests\test_nodes.py` file, although specific details of its usage in these files are not provided.

**Note**: Ensure that the `_children` attribute is properly initialized and maintained within the `AbstractNode` class to avoid unexpected behavior when calling the `children` method.

**Output Example**: A possible return value of the `children` method could be:
```python
[<AbstractNode object at 0x...>, <AbstractNode object at 0x...>]
```
This indicates that the current node has two child nodes, each represented by an instance of `AbstractNode`.
***
### FunctionDef name(self)
**name**: The function of name is name.
**parameters**:
- self: The instance of the class.
**Code Description**:
The `name` function is a method of the `AbstractNode` class. It returns the value of the private attribute `_name`. This function is used to retrieve the name of the node.

The `_name` attribute is set when the node is registered in the graph. It is a combination of the node's name and its index in the list of nodes with the same name. The index is incremented each time a new node with the same name is registered.

This function is called by various objects in the project. For example, it is called by the `get_fun_name` function in the `function_optimizer.py` file of the `optimizers` module. It is also called by the `register` function in the `nodes.py` file of the `trace` module.

In the `get_fun_name` function, the `name` function is used to retrieve the name of a `MessageNode` object. If the `info` attribute of the node is a dictionary and it contains the key "fun_name", the value associated with that key is returned. Otherwise, the name of the node is split using the ":" delimiter, and the first part of the split is returned.

In the `register` function, the `name` function is used to set the `_name` attribute of a node. The name is split using the ":" delimiter, and the first part of the split is assigned to the `name` variable. If there are any name scopes defined in the `NAME_SCOPES` list, the name is prefixed with the last scope in the list followed by a "/". The node is then added to the `_nodes` dictionary using the modified name as the key. The `_name` attribute of the node is set to the modified name followed by the index of the node in the list of nodes with the same name.

**Note**: 
- The `name` function should only be called after the node has been registered in the graph.
- The `name` function assumes that elements in the `_nodes` dictionary never get removed.

**Output Example**: 
If the `_name` attribute of a node is "node:0", the `name` function will return "node:0".
***
### FunctionDef py_name(self)
**py_name**: The function of py_name is py_name.

**parameters**:
- self: The instance of the class.

**Code Description**:
The `py_name` function is a method of the current class. It returns the value of the `name` attribute after removing the ":" character. This function is used to modify the name attribute by replacing the ":" character with an empty string.

This function is called by various objects in the project. For example, it is called by the `repr_function_call` function in the `function_optimizer.py` file of the `optimizers` module. It is also called by the `node_to_function_feedback` function in the same file.

In the `repr_function_call` function, the `py_name` function is used to retrieve the name of a `MessageNode` object. The name is then used to construct a function call string.

In the `node_to_function_feedback` function, the `py_name` function is used to retrieve the name of a node. The name is then used as a key in the `documentation` dictionary.

In the `summarize` method of the `FunctionOptimizer` class, the `py_name` function is used to retrieve the name of a parameter node. The name is then used to classify the node into variables and others.

In the `construct_update_dict` method of the `FunctionOptimizer` class, the `py_name` function is used to retrieve the name of a parameter node. The name is then used to construct an update dictionary.

In the `fun` method of the `FunModule` class, the `py_name` function is used to retrieve the name of a parameter node. The name is then used to define a function.

In the `get_label` method of the `NodeVizStyleGuide` class, the `py_name` function is used to retrieve the name of a node. The name is then used to construct a label for the node.

In the `backward` method of the `Node` class, the `py_name` function is used to retrieve the name of a node. The name is then used for visualization purposes.

**Note**:
- The `py_name` function should only be called after the name attribute has been set.
- The `py_name` function assumes that the name attribute does not contain any other special characters that need to be replaced.

**Output Example**:
If the name attribute of a node is "node:0", the `py_name` function will return "node0".
***
### FunctionDef id(self)
**id**: The function of id is to extract and return the identifier part of the node's name.

**parameters**: The parameters of this Function.
- self: The instance of the class.

**Code Description**: The `id` function is a method of the `AbstractNode` class. It operates on the `name` attribute of the instance, which is a string formatted as "name:identifier". The function splits this string using the colon (":") delimiter and returns the second part, which corresponds to the identifier. This identifier is typically a unique part of the node's name, distinguishing it from other nodes with the same base name.

The `name` attribute is accessed through the `name` method of the `AbstractNode` class, which retrieves the value of the private attribute `_name`. The `id` function relies on the assumption that the `name` attribute follows the "name:identifier" format.

**Note**: 
- The `id` function should only be called after the node's `name` attribute has been properly set and follows the expected format.
- Ensure that the `name` attribute contains a colon (":") to avoid index errors during the split operation.

**Output Example**: 
If the `name` attribute of a node is "node:0", the `id` function will return "0".
***
### FunctionDef level(self)
**level**: The function of level is to return the internal level attribute of the object.

**parameters**: The parameters of this Function.
· This function does not take any parameters.

**Code Description**: The level function is a method that returns the value of the private attribute _level of the object. This method is used to access the internal state of the object, specifically the _level attribute, which is presumably set elsewhere in the class. The function does not modify any state or take any arguments; it simply provides a way to retrieve the current value of _level.

In the context of its usage within the project, the level function is called by the init_feedback method in the GraphPropagator class, located in the opto\trace\propagators\graph_propagator.py file. The init_feedback method uses the level function to obtain the level of a node and includes this information in the TraceGraph it constructs. This indicates that the level of a node is an important piece of information for initializing feedback in the graph propagation process.

**Note**: This function is a simple accessor and does not perform any validation or modification of the _level attribute. It is important to ensure that the _level attribute is properly initialized before calling this function to avoid potential issues.

**Output Example**: If the _level attribute of the object is set to 3, calling the level function will return 3.
***
### FunctionDef is_root(self)
**is_root**: The function of is_root is to determine if the current node is a root node.

**parameters**: The parameters of this function.
· self: The current node object.

**Code Description**: The `is_root` function is a method of the `AbstractNode` class in the `nodes.py` module. It checks whether the current node is a root node by evaluating the length of its parents list. Specifically, it returns `True` if the length of the parents list is zero, indicating that the node has no parents and is therefore a root node. Conversely, it returns `False` if the node has one or more parents.

The function relies on the `parents` method of the `AbstractNode` class to retrieve the list of parent nodes. The `parents` method accesses the `_parents` attribute of the node object, which is a list containing the parent nodes. By checking the length of this list, the `is_root` function determines the root status of the node.

**Note**: This function is essential for identifying root nodes in a graph structure, which can be useful for various graph operations such as traversal, initialization, and feedback propagation.

**Output Example**: 
- If the current node has no parents, the `is_root` function will return `True`.
- If the current node has one or more parents, the `is_root` function will return `False`.
***
### FunctionDef is_leaf(self)
**is_leaf**: The function of is_leaf is to determine if the current node is a leaf node, meaning it has no children.

**parameters**: This function does not take any parameters.

**Code Description**: The `is_leaf` method is a part of the `AbstractNode` class. It checks whether the current node has any child nodes by utilizing the `children` method of the same class. Specifically, it returns `True` if the length of the list returned by the `children` method is zero, indicating that the node has no children and is therefore a leaf node. Otherwise, it returns `False`.

The `children` method, which is called within `is_leaf`, returns the `_children` attribute of the instance. This attribute is a list containing the child nodes of the current node. By checking the length of this list, `is_leaf` can accurately determine the leaf status of the node.

**Note**: Ensure that the `_children` attribute is properly initialized and maintained within the `AbstractNode` class to avoid unexpected behavior when calling the `is_leaf` method.

**Output Example**: A possible return value of the `is_leaf` method could be:
```python
True
```
This indicates that the current node has no children and is therefore a leaf node.
***
### FunctionDef _add_child(self, child)
**_add_child**: The function of _add_child is to add a child node to the current node.
**parameters**:
- child: The child node to be added.

**Code Description**:
The `_add_child` function is used to add a child node to the current node. It performs the following steps:
1. It first checks if the child node is not the same as the current node itself. If it is, it raises an assertion error with the message "Cannot add self as a child."
2. It then checks if the child node is an instance of the `Node` class. If it is not, it raises an assertion error with a message indicating that the child is not a Node.
3. Finally, it calls the `_add_parent` function of the child node, passing the current node as the parent.

**Note**:
- The `_add_child` function ensures that the child node is not the same as the current node and that it is an instance of the `Node` class before adding it as a child.
- This function assumes that the child node has an `_add_parent` function to add the current node as its parent.
***
### FunctionDef _add_parent(self, parent)
**_add_parent**: The function of _add_parent is to add a parent node to the current node in the hierarchical structure of the graph.

**parameters**:
- parent: The parent node to be added.

**Code Description**:
The _add_parent function is a method designed to add a parent node to the current node in the hierarchical structure of the graph. It performs several checks and operations to ensure the validity of the parent node and the consistency of the graph structure.

First, the function asserts that the parent node is not the same as the current node, as it is not allowed to add itself as a parent. This check prevents circular dependencies and ensures the integrity of the graph.

Next, the function asserts that the parent node is an instance of the Node class. This check ensures that only valid nodes can be added as parents.

If both checks pass, the function proceeds to add the current node as a child to the parent node by appending it to the parent's _children attribute. Similarly, it adds the parent node to the current node's _parents attribute.

Finally, the function calls the _update_level method to update the level attribute of the current node. It passes the maximum value between the current node's _level attribute and the parent node's _level attribute plus one as the new level value. This ensures that the hierarchical structure of the nodes is maintained correctly, with child nodes always having a level greater than or equal to their parent nodes.

It is worth noting that the _add_parent function assumes that the parent parameter is a valid instance of the Node class. If the parent parameter is not a Node instance, an assertion error will be raised.

**Note**:
- The function does not return any value.
- The function assumes that the parent parameter is a valid instance of the Node class.
- The function raises an assertion error if the parent parameter is the same as the current node or if it is not an instance of the Node class.
***
### FunctionDef _update_level(self, new_level)
**_update_level**: The function of _update_level is to update the level attribute of the current node to a new specified level.

**parameters**: The parameters of this Function.
· new_level: The new level to which the node's level attribute should be updated.

**Code Description**: The _update_level function is a method designed to update the internal _level attribute of an instance of the AbstractNode class. This method takes a single parameter, new_level, which represents the new level value that the node should be assigned. The function directly assigns this new value to the node's _level attribute.

In the context of its usage within the project, the _update_level function is called by the _add_parent method of the AbstractNode class. When a new parent node is added to the current node, the _add_parent method ensures that the current node's level is updated appropriately. Specifically, it sets the current node's level to the maximum of its current level and the new parent's level plus one. This ensures that the hierarchical structure of the nodes is maintained correctly, with child nodes always having a level greater than or equal to their parent nodes.

**Note**: 
- The function assumes that the new_level parameter is a valid integer representing the level.
- The function does not perform any validation or checks on the new_level parameter; it directly assigns it to the _level attribute.
- The commented-out line in the function suggests that there was an intention to update a global or shared structure (GRAPH._levels) that tracks nodes by their levels, but this functionality is not implemented in the current version of the function.
***
### FunctionDef __str__(self)
**__str__**: The function of __str__ is to provide a string representation of the AbstractNode object.

**parameters**: The parameters of this function.
· self: The instance of the AbstractNode class.

**Code Description**: The __str__ method in the AbstractNode class returns a string that represents the node in a human-readable format. This method is particularly useful for debugging and logging purposes, as it provides a quick way to inspect the node's key attributes. The string includes the node's name, the data type of the node's data, and the actual data stored in the node.

The method constructs the string by accessing the `name` property of the node, which retrieves the node's name. It also accesses the `_data` attribute to include the data type and the data itself in the string. The `name` property is a method that returns the value of the private attribute `_name`, which is set when the node is registered in the graph.

**Note**: 
- The __str__ method should be used when a readable string representation of the node is needed, such as in logging or debugging scenarios.
- Ensure that the node has been properly initialized and registered before calling this method to avoid any unexpected behavior.

**Output Example**: 
If a node has the name "node:0", its data type is `<class 'int'>`, and its data is `42`, the __str__ method will return:
```
Node: (node:0, dtype=<class 'int'>, data=42)
```
***
### FunctionDef __deepcopy__(self, memo)
**__deepcopy__**: The function of __deepcopy__ is to create a deep copy of the node, which is detached from the original graph.

**parameters**: The parameters of this Function.
· memo: A dictionary used to keep track of objects that have already been copied to avoid infinite recursion during the deep copy process.

**Code Description**: The __deepcopy__ function is designed to create a deep copy of an instance of the AbstractNode class. This means that the new instance will be a completely independent copy of the original, with no shared references to mutable objects.

1. The function starts by obtaining the class of the current instance (`cls = self.__class__`).
2. It then creates a new, uninitialized instance of this class (`result = cls.__new__(cls)`).
3. The `memo` dictionary is updated to associate the original instance's ID with the new instance (`memo[id(self)] = result`). This helps in tracking already copied objects to prevent infinite loops.
4. The function iterates over all the attributes of the original instance (`for k, v in self.__dict__.items():`).
5. For attributes named `_parents` or `_children`, it sets these attributes in the new instance to empty lists (`setattr(result, k, [])`). This ensures that the new instance starts with no parent or child nodes.
6. For all other attributes, it performs a deep copy of the attribute's value and assigns it to the new instance (`setattr(result, k, copy.deepcopy(v, memo))`).
7. Finally, the new instance is returned (`return result`).

**Note**: 
- This function ensures that the new node is completely independent of the original node, with no shared references to mutable objects.
- Special handling is provided for `_parents` and `_children` attributes to ensure they are initialized as empty lists in the new instance.

**Output Example**: 
If the original node has attributes like `name`, `_parents`, and `_children`, the deep copy will result in a new node with the same `name` but with `_parents` and `_children` set to empty lists. For example:

Original Node:
```python
original_node = AbstractNode()
original_node.name = "Node1"
original_node._parents = [parent_node]
original_node._children = [child_node]
```

Deep Copied Node:
```python
copied_node = copy.deepcopy(original_node)
print(copied_node.name)  # Output: Node1
print(copied_node._parents)  # Output: []
print(copied_node._children)  # Output: []
```
***
### FunctionDef lt(self, other)
**lt**: The function of lt is to compare the levels of two nodes and determine if the level of the current node is less than the level of another node.

**parameters**: The parameters of this Function.
· self: The current instance of the node.
· other: Another instance of a node to compare with the current node.

**Code Description**: The lt function is a method used to compare the levels of two nodes. It takes two parameters: `self`, which refers to the current node instance, and `other`, which refers to another node instance. The function compares the `_level` attribute of both nodes. Specifically, it checks if the negated level of the current node (`-self._level`) is less than the negated level of the other node (`-other._level`). This effectively means that the function is comparing the levels in reverse order, where a higher numerical level is considered "less than" a lower numerical level.

**Note**: 
- Ensure that both `self` and `other` have the `_level` attribute defined before using this function.
- This function is intended to be used where node levels are compared in a reversed manner.

**Output Example**: 
If `self._level` is 3 and `other._level` is 5, the function will return `True` because `-3` is less than `-5`.
***
### FunctionDef gt(self, other)
**gt**: The function of gt is to compare the levels of two AbstractNode objects and determine if the level of the current object is greater than the level of another object.

**parameters**: The parameters of this Function.
· self: The instance of the current AbstractNode object.
· other: Another instance of an AbstractNode object to compare against.

**Code Description**: The gt function is a method used to compare the levels of two AbstractNode objects. It takes two parameters: `self` and `other`, which are both instances of AbstractNode. The function compares the `_level` attribute of the two objects. Specifically, it negates the `_level` attributes of both objects and then checks if the negated level of the current object (`self`) is greater than the negated level of the other object (`other`). This effectively determines if the level of the current object is greater than the level of the other object.

**Note**: 
- The `_level` attribute must be defined for both AbstractNode objects being compared.
- This function relies on the assumption that `_level` is a numeric value that can be meaningfully compared.

**Output Example**: 
If `self._level` is 3 and `other._level` is 2, the function will return `True` because -3 is greater than -2.
***
## FunctionDef get_op_name(description)
**get_op_name**: The function of get_op_name is to extract the operator type from the given description.

**Parameters**:
- description: A string representing the description from which the operator type needs to be extracted.

**Code Description**:
The `get_op_name` function takes a description as input and uses regular expression to search for the operator type enclosed in square brackets at the beginning of the description. If a match is found, the operator type is extracted and returned. Otherwise, a `ValueError` is raised with a specific error message.

This function is called by multiple objects in the project. In the `FunModule` class of the `bundle.py` file, the `get_op_name` function is used to generate the description for the function module. The extracted operator type is combined with the function name and docstring to create a meaningful description. The `name` method of the `FunModule` class also calls the `get_op_name` function to retrieve the operator type from the description.

The `get_op_name` function is also used in the `backward` method of the `Node` class in the `nodes.py` file. This method performs a backward pass in a graph and propagates feedback from child nodes to parent nodes. The `get_op_name` function is used to extract the operator type from the description of each node.

**Note**:
- The description parameter must contain the operator type enclosed in square brackets at the beginning.
- If the description does not contain the operator type, a `ValueError` will be raised.

**Output Example**:
If the description is "[Add] Add two numbers", the function will return "Add".
## ClassDef NodeVizStyleGuide
**NodeVizStyleGuide**: The function of NodeVizStyleGuide is to provide a standardized way to visualize nodes in a graph, particularly for use with graph visualization tools like Graphviz.

**attributes**: The attributes of this Class.
· style: A string that defines the style of the visualization. Default is 'default'.
· print_limit: An integer that sets the maximum number of characters to print for node descriptions and content. Default is 100.

**Code Description**: The NodeVizStyleGuide class is designed to facilitate the visualization of nodes in a graph by providing a consistent style guide. It includes methods to generate attributes for nodes, such as labels, shapes, colors, and styles, which are essential for rendering nodes in a visually coherent manner.

- The `__init__` method initializes the class with a specified style and a print limit for node descriptions and content.
- The `get_attrs` method returns a dictionary of attributes for a given node, including label, shape, fill color, and style.
- The `get_label` method constructs a label for a node by combining its name, description, and data. It truncates the description and data if they exceed the print limit.
- The `get_node_shape` method determines the shape of a node based on its type. For instance, ParameterNode types are represented as 'box', while other types are represented as 'ellipse'.
- The `get_color` method assigns a color to a node based on its type. ExceptionNode types are colored 'firebrick1', and ParameterNode types are colored 'lightgray'.
- The `get_style` method sets the style of a node to 'filled,solid' if the node is trainable; otherwise, it returns an empty string.

In the context of its usage within the project, the NodeVizStyleGuide class is utilized in the `backward` method of the Node class. When the `visualize` parameter is set to True, an instance of NodeVizStyleGuide is created to generate the necessary attributes for each node in the graph. These attributes are then used to render the nodes and edges in the graph using Graphviz. The `get_attrs` method is called to obtain the visualization attributes for each node, ensuring that the graph is displayed with a consistent and informative style.

**Note**: 
- Ensure that the `print_limit` is set appropriately to avoid truncating important information in node descriptions and content.
- The class assumes the existence of specific node types like ParameterNode and ExceptionNode, so it should be used in environments where these types are defined.

**Output Example**: 
A possible appearance of the code's return value from the `get_attrs` method might look like this:
```
{
    'label': 'node_name\nnode_description...\nnode_content...',
    'shape': 'ellipse',
    'fillcolor': '',
    'style': 'filled,solid'
}
```
### FunctionDef __init__(self, style, print_limit)
**__init__**: The function of __init__ is to initialize an instance of the NodeVizStyleGuide class with specific visualization style settings and a print limit.

**parameters**: The parameters of this Function.
· style: A string parameter that sets the visualization style. The default value is 'default'.
· print_limit: An integer parameter that sets the limit for print operations. The default value is 100.

**Code Description**: The __init__ function is a constructor method for the NodeVizStyleGuide class. It initializes the instance with two attributes: `style` and `print_limit`. The `style` attribute is set to the value provided by the `style` parameter, which defaults to 'default' if not specified. The `print_limit` attribute is set to the value provided by the `print_limit` parameter, which defaults to 100 if not specified. These attributes are used to configure the visualization style and the print limit for the node visualization guide.

**Note**: Ensure that the `style` parameter is a valid string representing a visualization style and that the `print_limit` parameter is a positive integer to avoid potential issues during the usage of the NodeVizStyleGuide class.
***
### FunctionDef get_attrs(self, x)
**get_attrs**: The function of get_attrs is to generate a dictionary of attributes for a node object.

**parameters**:
- self: Refers to the instance of the class that contains this method.
- x: The node object for which the attributes are generated.

**Code Description**:
The `get_attrs` function is a method of the `NodeVizStyleGuide` class. It takes a node object `x` as input and generates a dictionary of attributes for the node. The attributes include the label, shape, fill color, and style of the node.

The function first calls the `get_label` method of the `NodeVizStyleGuide` class to generate the label attribute. It then calls the `get_node_shape` method to determine the shape attribute based on the type of the node. The `get_color` method is called to determine the fill color attribute based on the type of the node. Finally, the `get_style` method is called to determine the style attribute based on the trainable status of the node.

The function constructs a dictionary `attrs` with the label, shape, fill color, and style attributes, and returns it.

This function is called by the `backward` method of the `Node` class in the same module. The `backward` method performs a backward pass in a computational graph and utilizes the `get_attrs` function to generate the attributes for each node in the graph.

**Note**:
- The `get_attrs` function assumes that the `get_label`, `get_node_shape`, `get_color`, and `get_style` methods are implemented correctly and return valid values.
- The function does not handle cases where the node object does not have the required attributes or methods.

**Output Example**:
If the label of the node is "Node1", the shape is "ellipse", the fill color is "lightgray", and the style is an empty string, the function will return the following dictionary:
```
{
    'label': 'Node1',
    'shape': 'ellipse',
    'fillcolor': 'lightgray',
    'style': ''
}
```
***
### FunctionDef get_label(self, x)
**get_label**: The function of get_label is to generate a label for a node object.

**parameters**:
- self: Refers to the instance of the class that contains this method.
- x: The node object for which the label is generated.

**Code Description**:
The `get_label` function is a method of the `NodeVizStyleGuide` class. It takes a node object `x` as input and generates a label for the node. The label consists of the node's name and description, as well as additional content if available.

The function first retrieves the description of the node by calling the `description` method of the node object. It then checks if the length of the description exceeds the `print_limit` attribute of the `NodeVizStyleGuide` instance. If it does, the description is truncated and an ellipsis is appended.

Next, the function constructs the text part of the label by concatenating the node's name and the truncated description. The content of the node is retrieved by accessing the `data` attribute of the node object. If the content is a dictionary and it contains a key named "content", the value associated with that key is used as the content. Otherwise, the content is converted to a string representation.

Similar to the description, the content is checked against the `print_limit` attribute and truncated if necessary.

Finally, the function returns the concatenated text and content as the label for the node.

This function is called by the `get_attrs` method of the `NodeVizStyleGuide` class. The `get_attrs` method generates a dictionary of attributes for a node, including the label, shape, fill color, and style. The `get_label` function is responsible for generating the label attribute of the dictionary.

**Note**:
- The `get_label` function assumes that the `description` and `data` attributes of the node object are already set and contain valid values.
- The `print_limit` attribute of the `NodeVizStyleGuide` instance determines the maximum length of the description and content before truncation.
- The function does not handle cases where the `data` attribute is not present or is of an unsupported type.

**Output Example**:
If the name of the node is "Node1" and the description is "This is a sample node description.", the content is a dictionary with the key "content" and value "Sample content", and the `print_limit` is set to 20, the function will return the following label:
```
Node1
This is a sample no...
Sample content
```
***
### FunctionDef get_node_shape(self, x)
**get_node_shape**: The function of get_node_shape is to determine the shape of a node based on its type.

**parameters**: The parameters of this Function.
· x: The node whose shape is to be determined.

**Code Description**: The get_node_shape function is a method designed to return the shape of a node in a computational graph visualization. It takes a single parameter, x, which represents the node whose shape needs to be determined. The function checks the type of the node x. If x is an instance of the ParameterNode class, the function returns the string 'box', indicating that the node should be visualized as a box. For all other types of nodes, the function returns the string 'ellipse', indicating that the node should be visualized as an ellipse.

This function is utilized within the get_attrs method of the NodeVizStyleGuide class. The get_attrs method calls get_node_shape to include the shape attribute in the dictionary of attributes for a node. This dictionary is used to define various visual properties of the node, such as its label, shape, fill color, and style.

**Note**: 
- The function relies on the type of the node to determine its shape. It specifically checks if the node is an instance of ParameterNode.
- The ParameterNode class represents a trainable node in a computational graph and has various attributes such as value, name, trainable, description, constraint, and info.

**Output Example**: 
- If x is an instance of ParameterNode, the function returns 'box'.
- If x is not an instance of ParameterNode, the function returns 'ellipse'.
***
### FunctionDef get_color(self, x)
**get_color**: The function of get_color is to determine the color representation of a node based on its type.

**parameters**: The parameters of this Function.
· x: The node whose color representation is to be determined.

**Code Description**: The get_color function is a method designed to return a specific color string based on the type of the node passed as an argument. It takes a single parameter, x, which represents the node. The function checks the type of the node and returns a corresponding color string:

- If the node is of type ExceptionNode, the function returns the color 'firebrick1'.
- If the node is of type ParameterNode, the function returns the color 'lightgray'.
- For any other type of node, the function returns an empty string.

This function is utilized within the get_attrs method of the NodeVizStyleGuide class. The get_attrs method calls get_color to determine the fill color attribute of a node, which is part of a set of attributes used for visualizing the node. The get_attrs method constructs a dictionary of attributes including label, shape, fill color, and style, where the fill color is obtained by invoking get_color.

**Note**: 
- The function relies on the specific types of nodes (ExceptionNode and ParameterNode) to determine the color. If additional node types need to be supported, the function should be extended accordingly.
- The function returns an empty string for node types that are not explicitly handled, which may need to be addressed depending on the visualization requirements.

**Output Example**: 
- For an ExceptionNode, the function would return 'firebrick1'.
- For a ParameterNode, the function would return 'lightgray'.
- For any other node type, the function would return an empty string.
***
### FunctionDef get_style(self, x)
**get_style**: The function of get_style is to determine the style attributes of a node based on its trainable status.

**parameters**: The parameters of this Function.
· x: An object that contains the attribute 'trainable'.

**Code Description**: The get_style function evaluates the 'trainable' attribute of the input object 'x'. If 'x.trainable' is True, the function returns the string 'filled,solid', indicating that the node should be styled with a filled and solid appearance. If 'x.trainable' is False, the function returns an empty string, indicating that no specific style should be applied.

This function is called by the get_attrs function within the same module. The get_attrs function constructs a dictionary of attributes for a node, including its label, shape, fill color, and style. The get_style function specifically provides the 'style' attribute for this dictionary, ensuring that nodes which are trainable are visually distinguished by a filled and solid style.

**Note**: Ensure that the input object 'x' has a 'trainable' attribute; otherwise, the function may raise an AttributeError.

**Output Example**: 
- If x.trainable is True, the return value will be 'filled,solid'.
- If x.trainable is False, the return value will be an empty string "".
***
## ClassDef Node
An unknown error occurred while generating this documentation after many tries.
### FunctionDef __init__(self, value)
**__init__**: The function of __init__ is to initialize a Node object in a computational graph.

**parameters**: The parameters of this Function.
· value: The initial value of the node.
· name: An optional string representing the name of the node.
· trainable: A boolean indicating whether the node is trainable.
· description: A string providing a description of the node.
· constraint: An optional string representing any constraints on the node.
· info: An optional dictionary containing additional information about the node.

**Code Description**: The __init__ function initializes a Node object with several attributes. It first calls the superclass initializer with the value and name parameters. The trainable attribute is set based on the provided argument, indicating whether the node can be trained. The _feedback attribute is initialized as a defaultdict of lists, which will store feedback from child nodes. This feedback mechanism is analogous to gradients in machine learning and is used to propagate information back through the graph. The _description attribute stores a textual description of the node, while the _constraint attribute holds any constraints that apply to the node. The _backwarded attribute is a boolean flag indicating whether the backward pass has been called on this node. The _info attribute is a dictionary for storing additional information about the node. Finally, the _dependencies attribute is a dictionary that tracks dependencies on parameters and expandable nodes, which are nodes that depend on parameters not visible at the current graph level.

**Note**: Points to note about the use of the code
- Ensure that the value parameter is provided when initializing the Node.
- The name parameter is optional but can be useful for identifying nodes in the graph.
- The trainable parameter should be set to True if the node is intended to be updated during training.
- The description, constraint, and info parameters provide additional context and constraints for the node, which can be useful for debugging and documentation purposes.
- The feedback mechanism is designed to support non-commutative aggregation, so feedback should be handled carefully to maintain the correct order of operations.
***
### FunctionDef zero_feedback(self)
**zero_feedback**: The function of zero_feedback is to reset the feedback attribute of the Node object to an empty state.

**parameters**: This function does not take any parameters.

**Code Description**: The zero_feedback function is designed to reset the feedback mechanism of a Node object. It achieves this by setting the _feedback attribute to a new defaultdict with lists as the default factory. This ensures that any previous feedback data stored in the _feedback attribute is cleared, effectively resetting it to an empty state.

In the context of its usage within the project, the zero_feedback function is called by the backward method of the Node class. During the backward pass, feedback is propagated from the current node to its parent nodes. After this propagation, zero_feedback is invoked to clear the feedback of the current node. This is crucial to prevent the feedback from being double-counted if the retain_graph parameter is set to True. By resetting the feedback, the function ensures that each node's feedback is only considered once during the backward pass, maintaining the integrity of the feedback propagation process.

**Note**: It is important to note that zero_feedback should be used judiciously within the feedback propagation process to avoid unintended loss of feedback data. It is specifically designed to be used after feedback has been successfully propagated to parent nodes.
***
### FunctionDef feedback(self)
**feedback**: The function of feedback is to return the internal feedback attribute of the Node object.

**parameters**: The parameters of this Function.
· None

**Code Description**: The feedback function is a method of the Node class that simply returns the value of the private attribute _feedback. This method does not take any parameters and provides a way to access the internal feedback data stored within the Node object.

The feedback method is utilized in various parts of the project to retrieve feedback information from Node objects. For instance, in the summarize method of the FunctionOptimizer class, the feedback method is called on each trainable node to aggregate feedback from all parameters. This aggregated feedback is then used to construct a summary of the feedback for further processing.

Similarly, in the _propagate method of the GraphPropagator class, the feedback method is called on a child node to obtain its feedback, which is then aggregated and propagated to its parent nodes. This ensures that feedback information flows correctly through the graph structure.

In the AbstractPropagator class, the __call__ method also makes use of the feedback method to propagate feedback from a child node to its parents. This method ensures that the feedback is in the correct format and that all parent nodes receive the appropriate feedback.

The SumPropagator class's _propagate method uses the feedback method to retrieve user feedback or sum the feedback from various sources, ensuring that the feedback is correctly propagated to parent nodes.

**Note**: The feedback method is a straightforward accessor method and does not perform any modifications to the internal state of the Node object. It is essential to ensure that the _feedback attribute is correctly initialized and maintained within the Node class to provide accurate feedback information.

**Output Example**: A possible appearance of the code's return value could be:
```
{
    "loss": 0.25,
    "accuracy": 0.95
}
```
This example assumes that the _feedback attribute contains a dictionary with keys representing different metrics and their corresponding values. The actual structure and content of the feedback will depend on the specific implementation and use case within the project.
***
### FunctionDef description(self)
**description**: The function of description is to return a textual description of the node.

**parameters**: The parameters of this Function.
· None

**Code Description**: The description function is a method that returns the value of the private attribute `_description` of the Node object. This function is straightforward and does not take any parameters. It simply accesses and returns the `_description` attribute, which is expected to hold a textual description of the node.

This function is utilized in various parts of the project to retrieve the description of a node. For instance, in the `get_label` method of the `NodeVizStyleGuide` class, the `description` function is called to obtain the node's description, which is then used to generate a label for visualization purposes. The method ensures that the description does not exceed a certain length by truncating it if necessary.

Similarly, in the `propagate` method of the `Propagator` class, the `description` function is used to get the node's description, which is then processed to determine the appropriate propagation behavior based on the operator name derived from the description.

**Note**: This function assumes that the `_description` attribute is already set and contains a valid string. It does not perform any validation or modification of the description.

**Output Example**: 
If the `_description` attribute of a Node object is set to "This is a sample node description.", calling the `description` function will return:
"This is a sample node description."
***
### FunctionDef info(self)
**info**: The function of info is to return the value of the `_info` attribute of the object.

**parameters**:
- self: The object itself.

**Code Description**:
The `info` function is a method of the `Node` class. It returns the value of the `_info` attribute of the object. The `_info` attribute is a private attribute that stores additional information about the node.

The purpose of the `info` function is to provide access to the `_info` attribute, allowing users to retrieve any additional information associated with the node.

This function does not take any arguments other than `self`, which refers to the object itself. By calling `info()` on a `Node` object, the function will return the value of the `_info` attribute.

The `_info` attribute can be set by the user or by other functions within the code. It is typically used to store metadata or any other relevant information about the node.

**Note**: 
- The `info` function is a simple getter method that provides access to the `_info` attribute of the object.
- The `_info` attribute can be accessed directly, but it is recommended to use the `info` function for consistency and encapsulation.

**Output Example**: 
If the `_info` attribute of the object is set to `"This is a node"`, calling `info()` will return `"This is a node"`.
***
### FunctionDef parameter_dependencies(self)
**parameter_dependencies**: The function of parameter_dependencies is to return the dependencies related to parameters within the Node object.

**parameters**: This function does not take any parameters.

**Code Description**: The parameter_dependencies function is a method within the Node class that retrieves and returns the parameter dependencies stored in the Node object. Specifically, it accesses the '_dependencies' attribute of the Node instance, which is a dictionary, and returns the value associated with the 'parameter' key. This value represents the set of dependencies that are related to the parameters of the Node.

The function is utilized by the external_dependencies method in the MessageNode class. In this context, the external_dependencies method checks if the 'info' attribute of the MessageNode instance is a dictionary and if it contains an 'output' key that is an instance of Node. It then compares the length of the parameter dependencies of the 'output' Node with the parameter dependencies of the current MessageNode. If the 'output' Node has more parameter dependencies, it returns the difference between the two sets of dependencies. This indicates that the external_dependencies method relies on the parameter_dependencies function to determine the parameter dependencies of the Node instances it interacts with.

**Note**: Ensure that the '_dependencies' attribute is properly initialized and contains a 'parameter' key with a corresponding value before calling the parameter_dependencies function to avoid potential KeyError exceptions.

**Output Example**: A possible return value of the parameter_dependencies function could be a set of dependencies, such as:
```
{'dependency1', 'dependency2', 'dependency3'}
```
***
### FunctionDef expandable_dependencies(self)
**expandable_dependencies**: The function of expandable_dependencies is to retrieve the 'expandable' dependencies from the Node object's internal dependencies dictionary.

**parameters**: This function does not take any parameters.

**Code Description**: The expandable_dependencies function is a method of the Node class. It accesses the Node object's internal dictionary, `_dependencies`, and returns the value associated with the key 'expandable'. This dictionary is assumed to store various types of dependencies, and the 'expandable' key specifically holds the dependencies that can be expanded. The function provides a straightforward way to access these expandable dependencies without directly interacting with the internal dictionary.

**Note**: 
- Ensure that the '_dependencies' dictionary is properly initialized and contains the 'expandable' key before calling this function to avoid potential KeyError exceptions.
- This function assumes that the 'expandable' key in the '_dependencies' dictionary holds a valid value that can be returned.

**Output Example**: 
If the '_dependencies' dictionary is structured as follows:
```python
self._dependencies = {
    'expandable': ['dependency1', 'dependency2'],
    'non_expandable': ['dependency3']
}
```
Calling `expandable_dependencies()` would return:
```python
['dependency1', 'dependency2']
```
***
### FunctionDef _add_feedback(self, child, feedback)
**_add_feedback**: The function of _add_feedback is to add feedback from a child node to the current node.

**parameters**: The parameters of this Function.
· child: The child node from which the feedback is received.
· feedback: The feedback data to be added.

**Code Description**: The _add_feedback function is designed to manage feedback propagation in a node-based structure. It takes two parameters: 'child', which represents the child node providing the feedback, and 'feedback', which is the actual feedback data to be appended. The function appends the feedback to a list associated with the child node in the _feedback dictionary of the current node.

In the context of its usage within the backward function, _add_feedback plays a crucial role in the feedback propagation mechanism. During the backward pass, feedback is propagated from child nodes to parent nodes. The backward function initializes the feedback for the current node and then propagates it to its parents. The _add_feedback function is called to append the propagated feedback from a child node to the current node's feedback list. This ensures that each node accumulates feedback from its children, which can then be used for further processing or analysis.

**Note**: Points to note about the use of the code
- Ensure that the _feedback dictionary is properly initialized and that each child node has an associated list to append feedback to.
- The function assumes that the child node is already present in the _feedback dictionary.
- Proper handling of feedback data is essential to avoid issues during the feedback propagation process.
***
### FunctionDef _set(self, value)
**_set**: The function of _set is to set the value of the node. If the value is a Node, it will be unwrapped.

**parameters**: The parameters of this Function.
· value: The value to be set for the node. It can be of any type, including another Node.

**Code Description**: The _set function is designed to assign a value to the node's internal data attribute. It first checks if the provided value is an instance of the Node class. If it is, the function retrieves the internal data of the Node by accessing its data attribute, effectively unwrapping the Node. This ensures that the node's internal data is set to the actual data contained within the provided Node, rather than the Node object itself. If the value is not a Node, it is directly assigned to the node's internal data attribute. This function is crucial for maintaining the integrity of the node's data, especially when dealing with nested Node objects.

**Note**: This function assumes that the "_data" attribute exists within the node object. If this attribute is not present, an AttributeError will be raised.
***
### FunctionDef backward(self, feedback, propagator, retain_graph, visualize, simple_visualization, reverse_plot, print_limit)
**backward**: The `backward` function is responsible for performing a backward pass in a computational graph. It propagates feedback from the current node to its parents, updates the graph visualization if required, and returns the resulting graph.

**parameters**:
- `feedback`: An optional parameter that represents the feedback given to the current node. It can be of any type.
- `propagator`: An optional parameter that represents a function used to propagate feedback from a node to its parents. If not provided, a default `GraphPropagator` object is used.
- `retain_graph`: A boolean parameter that determines whether to retain the graph after the backward pass. If set to `True`, the graph will be retained; otherwise, it will be cleared. The default value is `False`.
- `visualize`: A boolean parameter that determines whether to plot the graph using graphviz. If set to `True`, the graph will be visualized; otherwise, it will not be plotted. The default value is `False`.
- `simple_visualization`: A boolean parameter that determines whether to simplify the visualization by bypassing chains of identity operators. If set to `True`, identity operators will be skipped in the visualization; otherwise, they will be included. The default value is `True`.
- `reverse_plot`: A boolean parameter that determines the order of the graph visualization. If set to `True`, the graph will be plotted in reverse order (from child to parent); otherwise, it will be plotted in the default order (from parent to child). The default value is `False`.
- `print_limit`: An integer parameter that sets the maximum number of characters to print in the graph visualization. If the description or content of a node exceeds this limit, it will be truncated. The default value is `100`.

**Code Description**:
The `backward` function is a method of the current object. It performs a backward pass in a computational graph by propagating feedback from the current node to its parents. The function takes several parameters to control the behavior of the backward pass.

The `feedback` parameter represents the feedback given to the current node. It can be of any type and is used to initialize the feedback mechanism of the node. The `propagator` parameter is an optional function that is used to propagate feedback from a node to its parents. If not provided, a default `GraphPropagator` object is used, which implements specific methods for feedback propagation. The `retain_graph` parameter determines whether to retain the graph after the backward pass. If set to `True`, the graph will be retained; otherwise, it will be cleared. The `visualize` parameter determines whether to plot the graph using graphviz. If set to `True`, the graph will be visualized; otherwise, it will not be plotted. The `simple_visualization` parameter determines whether to simplify the visualization by bypassing chains of identity operators. If set to `True`, identity operators will be skipped in the visualization; otherwise, they will be included. The `reverse_plot` parameter determines the order of the graph visualization. If set to `True`, the graph will be plotted in reverse order (from child to parent); otherwise, it will be plotted in the default order (from parent to child). The `print_limit` parameter sets the maximum number of characters to print in the graph visualization. If the description or content of a node exceeds this limit, it will be truncated.

The function first checks if a `propagator` object is provided. If not, it imports the `GraphPropagator` class from the `opto.trace.propagators.graph_propagator` module. It then initializes the `propagator` object if it is not provided.

Next, the function sets up the visualization by creating a `digraph` object and a `NodeVizStyleGuide` object. These objects are used to plot the graph using graphviz and define the style of the nodes in the graph.

The function checks if the current node has already been backwarded. If it has, an `AttributeError` is raised. Otherwise, the function adds the feedback to the current node by calling the `_add_feedback` method of the node object. The feedback is initialized with a special "FEEDBACK_ORACLE" node and the propagated feedback from the `propagator` object.

If the current node has no parents, indicating that it is a root node, the function checks if visualization is enabled. If it is, the current node is added to the `digraph` object with the appropriate style attributes. Finally, the function returns the `digraph` object.

If the current node has parents, indicating that it is not a root node, the function initializes a priority queue called `queue` using the `MinHeap` class. The priority queue is used to process the nodes in the correct order during the backward pass.

The function enters a loop that continues until the `queue` is empty. In each iteration, a node is popped from the `queue` and processed. The node is checked to ensure it has parents and is an instance of the `MessageNode` class. If not, an `AttributeError` is raised.

The function propagates information from the current node to its parents by calling the `propagator` object with the current node as the argument. The `propagator` object computes the propagated feedback based on the child node's description, data, and feedback. The propagated feedback is then added to the parents of the current node by calling the `_add_feedback` method of each parent node.

The function checks if visualization is enabled. If it is, the function plots the edge from each parent to the current node in the `digraph` object. It also handles the visualization of identity operators by bypassing chains of identity operators if the `simple_visualization` parameter is set to `True`.

After processing the parents of the current node, the `_backwarded` attribute of the current node is updated to indicate that it has been backwarded. This attribute is set to `True` unless the `retain_graph` parameter is set to `True`.

The loop continues until the `queue` is empty, indicating that all the nodes have been processed. Finally, the function returns the `digraph` object.

**Note**:
- The `backward` function is a crucial part of the backward pass in a computational graph. It propagates feedback from child nodes to parent nodes, updates the graph visualization if required, and returns the resulting graph.
- The `feedback` parameter is used to initialize the feedback mechanism of the current node. It can be of any type and is specific to the application.
- The `propagator` parameter allows for customization of the feedback propagation process. If not provided, a default `GraphPropagator` object is used.
- The `retain_graph` parameter determines whether to retain the graph after the backward pass. This can be useful for further analysis or visualization.
- The `visualize` parameter allows for visualization of the graph using graphviz. This can be helpful for understanding the structure of the graph.
- The `simple_visualization` parameter simplifies the visualization by bypassing chains of identity operators. This can improve the clarity of the graph.
- The `reverse_plot` parameter determines the order of the graph visualization. This can be useful for visualizing the graph from child to parent, which may be more intuitive in some cases.
- The `print_limit` parameter sets a limit on the number of characters to print in the graph visualization. This can prevent the visualization from becoming too cluttered or overwhelming.

**Output Example**: 
If the current node has two parents and visualization is enabled, the `backward` function will return a `digraph` object representing the graph with the appropriate edges and node styles.
***
### FunctionDef clone(self)
**clone**: The function of clone is to create and return a duplicate of the current Node object.

**parameters**: The parameters of this Function.
· This function does not take any parameters other than the implicit self parameter, which refers to the instance of the Node class.

**Code Description**: The clone function is a method of the Node class that imports the clone function from the opto.trace.operators module and applies it to the current instance (self) of the Node class. The imported clone function from the operators module is responsible for creating a duplicate of the Node instance. This method ensures that the Node object can be cloned using a standardized operation defined in the operators module.

The clone function is also indirectly referenced by the identity function in the opto.trace.operators module. The identity function calls the clone method on its input parameter, effectively creating a duplicate of the input object. This demonstrates that the clone method is integral to operations that require object duplication within the project.

**Note**: 
- Ensure that the opto.trace.operators module is correctly imported and accessible when using the clone method.
- The clone method does not modify the original Node object; it only creates and returns a duplicate.

**Output Example**: The return value of the clone function will be a new instance of the Node class that is a duplicate of the original instance. For example, if the original Node instance has specific attributes and states, the cloned instance will have the same attributes and states.
***
### FunctionDef detach(self)
**detach**: The function of detach is to create and return a deep copy of the current instance of the Node class.

**parameters**: The parameters of this Function.
· This function does not take any parameters.

**Code Description**: The detach function is designed to create a deep copy of the current instance of the Node class. When this function is called, it utilizes the deepcopy method from the copy module to generate a new instance of the Node class that is a complete copy of the original, including all nested objects. This ensures that any changes made to the new instance do not affect the original instance, and vice versa. The function then returns this new deep-copied instance.

**Note**: 
- Ensure that the copy module is imported before using this function.
- This function does not modify the original instance; it only creates and returns a new deep-copied instance.

**Output Example**: 
If the original instance of the Node class has certain attributes and nested objects, calling the detach function will return a new instance with identical attributes and nested objects, but completely independent of the original instance. For example:

```python
original_node = Node()
detached_node = original_node.detach()
# detached_node is a deep copy of original_node
```
***
### FunctionDef getattr(self, key)
**getattr**: The function of getattr is to get the value of the specified attribute from the given object.

**parameters**:
- self: The object from which the attribute value is to be retrieved.
- key: A string representing the name of the attribute to be retrieved.

**Code Description**:
The `getattr` function is a method of the `Node` class in the `opto.trace.nodes.py` module. It takes in the `self` object, which is an instance of the `Node` class, and a string `key` as parameters. 

The function first imports the `node_getattr` function from the `opto.trace.operators` module. It then calls the `node_getattr` function passing itself (`self`) and the specified attribute (`key`) as arguments. The `node_getattr` function is responsible for retrieving the value of the specified attribute from the `Node` object.

The `getattr` method is used to access the attributes of the `Node` object. It is called when the `getattr` function is invoked on a `Node` object. The `getattr` method retrieves the value of the specified attribute from the `Node` object by calling the `node_getattr` function.

**Note**:
- The `getattr` method assumes that the `self` parameter is a valid `Node` object.
- If the `self` object does not have the specified attribute, a `AttributeError` will be raised.

**Output Example**:
A possible return value of the `getattr` method could be the value of the specified attribute from the `Node` object.
***
### FunctionDef call(self, fun)
**call**: The function of call is to invoke a specified function with the given arguments and keyword arguments.

**parameters**:
- self: The object on which the function is called.
- fun: A string representing the name of the function to be invoked.
- *args: Variable-length positional arguments to be passed to the function.
- **kwargs: Variable-length keyword arguments to be passed to the function.

**Code Description**:
The `call` function is a method of the `Node` class in the `opto.trace.nodes.py` module. It takes in the `self` object, which is an instance of the `Node` class, a string `fun`, and variable-length positional and keyword arguments (`args` and `kwargs`) as parameters.

The function first iterates over the `args` and converts each argument to a `Node` object using the `node` function. This is done to ensure that all arguments passed to the function are `Node` objects. The converted arguments are then stored in a generator expression.

Next, the function iterates over the `kwargs` and converts each value to a `Node` object using the `node` function. The converted values are then stored in a dictionary comprehension, with the keys being the original keys from `kwargs`.

Finally, the function calls the `getattr` method of the `self` object, passing the `fun` string as the attribute name. The `getattr` method retrieves the value of the specified attribute from the `self` object. The retrieved attribute is then invoked as a function, passing the converted `args` and `kwargs` as arguments.

The `call` method is used to dynamically invoke functions on the `Node` object. It allows for flexible and dynamic function calls based on the provided arguments and keyword arguments.

**Note**:
- The `fun` parameter should be a string representing the name of a valid function that can be invoked on the `self` object.
- The `args` and `kwargs` parameters can be any valid arguments that can be passed to the specified function.
- The `call` method assumes that the `self` parameter is a valid `Node` object with the specified function as an attribute.

**Output Example**: A possible return value of the `call` method could be the result of invoking the specified function with the provided arguments and keyword arguments.
***
### FunctionDef __call__(self)
**__call__**: The function of __call__ is to invoke the `call` function from the `opto.trace.operators` module with the provided arguments and keyword arguments.

**parameters**: The parameters of this function.
· `*args`: Variable-length argument list.
· `**kwargs`: Keyword arguments.

**Code Description**: The `__call__` method is designed to facilitate the invocation of a function encapsulated within a Node object. When this method is called, it imports the `call` function from the `opto.trace.operators` module. The `call` function is then executed with the current instance (`self`) and any additional arguments (`*args`) and keyword arguments (`**kwargs`) provided to the `__call__` method.

The `call` function, as defined in the `opto.trace.operators` module, takes a Node object representing the function to be called, along with any positional and keyword arguments. It ensures that the function encapsulated within the Node object is callable and then invokes it with the provided arguments. The result of this invocation is returned as the output.

By using the `__call__` method, the Node object can be used as if it were a regular callable function, providing a seamless interface for function invocation.

**Note**:
- The Node object must encapsulate a callable function.
- The `*args` parameter can accept any number of positional arguments.
- The `**kwargs` parameter can accept any number of keyword arguments.

**Output Example**:
If the Node object encapsulates a function defined as follows:
```python
def add(a, b):
    return a + b
```
and the `__call__` method is invoked with `args=(2, 3)`, the output will be `5`.
***
### FunctionDef len(self)
**len**: The function of len is to return the length of the Node instance.

**parameters**: The parameters of this Function.
· self: The Node instance whose length is to be calculated.

**Code Description**: The len method is a member of the Node class in the opto.trace.nodes module. This method is designed to compute and return the length of the Node instance. When invoked, the len method imports the len_ function from the opto.trace.operators module and applies it to the Node instance (self). The len_ function is a utility that leverages Python's built-in len() function to determine the length of the input object. By using the len_ function, the len method ensures a consistent and modular approach to length calculation within the project. This design promotes reusability and maintainability, as the len_ function can be utilized across different parts of the project.

**Note**: Ensure that the Node instance supports the len() operation. Passing an unsupported type will result in a TypeError.

**Output Example**: 
- If the Node instance represents a list [1, 2, 3], len(self) will return 3.
- If the Node instance represents a string "hello", len(self) will return 5.
***
### FunctionDef __getitem__(self, key)
**__getitem__**: The function of __getitem__ is to retrieve an element from a Node instance using a specified key.

**parameters**: The parameters of this function.
· key: The key used to access the element within the Node instance.

**Code Description**: The __getitem__ method is designed to facilitate element retrieval from a Node instance using a specified key. When this method is called, it first imports the getitem function from the opto.trace.operators module. It then uses the node function to create a Node object from the provided key. Finally, it calls the getitem function with the current Node instance (self) and the newly created Node object (from the key) as arguments. This modular approach allows for flexible and reusable element retrieval within the Node class.

The node function is responsible for creating a Node object from a given message. If the message is already a Node, it returns the message as is. This function simplifies the creation of Node objects and ensures consistency in how Nodes are instantiated.

The getitem function is a straightforward implementation of the indexing operation. It takes an object and an index as parameters and returns the element located at the specified index within the object. In this context, the getitem function is used to retrieve an element from the Node instance using the key provided to the __getitem__ method.

**Note**:
- Ensure that the key provided is compatible with the indexing mechanism of the Node instance.
- The node function should be used to create Node objects instead of directly invoking the Node class.

**Output Example**: If a Node instance contains a list [10, 20, 30] and the key provided is 1, the return value of the __getitem__ method will be 20.
***
### FunctionDef __contains__(self, item)
**__contains__**: The function of __contains__ is to determine if a given item is part of the Node instance.

**parameters**: The parameters of this Function.
· item: The element to be checked for presence within the Node instance.

**Code Description**: The __contains__ method is a special method in Python that allows the use of the `in` operator to check for membership within an object. In this context, the __contains__ method is part of the Node class in the opto\trace\nodes.py module. 

When the __contains__ method is called, it first imports the `in_` function from the opto.trace.operators module. The `in_` function is designed to determine whether an element `x` is present within a collection `y`. 

Next, the __contains__ method converts the `item` into a Node object using the `node` function. The `node` function is responsible for creating a Node object from a given message. If the message is already a Node, it returns the message as is. This ensures that the `item` is always in the form of a Node object before performing the membership test.

Finally, the __contains__ method calls the `in_` function with the Node-converted `item` and the Node instance (`self`) as arguments. The `in_` function then checks if the `item` is present within the Node instance and returns a boolean value indicating the result.

**Note**:
- The `item` parameter must be convertible to a Node object using the `node` function.
- The Node instance (`self`) must support the membership test operation.

**Output Example**: 
- If `item` is a Node object that is part of the Node instance, the method will return True.
- If `item` is not part of the Node instance, the method will return False.
***
### FunctionDef __pos__(self)
**__pos__**: The function of __pos__ is to return the unary positive of the Node instance.

**parameters**: The parameters of this Function.
· self: Refers to the instance of the Node class on which the unary positive operator is applied.

**Code Description**: The __pos__ method is a special method in Python that is invoked when the unary positive operator (+) is used on an instance of the Node class. When this operator is applied, the __pos__ method is called, which in turn imports the pos function from the opto.trace.operators module. The pos function is then called with the Node instance (self) as its argument. The pos function applies the unary positive operator to the input value and returns it. In this context, the unary positive operator does not alter the value of the Node instance; it simply returns the instance itself. This ensures that the unary positive operation is consistently applied to instances of the Node class.

**Note**: 
- The __pos__ method does not modify the Node instance; it simply returns it.
- Ensure that the Node class instances are of a type that supports the unary positive operator.

**Output Example**: 
If the Node instance is node_instance, the return value will be node_instance when +node_instance is used.
***
### FunctionDef __neg__(self)
**__neg__**: The function of __neg__ is to return the negation of the Node instance.

**parameters**: The parameters of this Function.
· self: The instance of the Node class to be negated.

**Code Description**: The __neg__ method is a special method in Python that is invoked when the unary negation operator (-) is applied to an instance of the Node class. This method imports the neg function from the opto.trace.operators module and applies it to the Node instance (self). The neg function, in turn, returns the negation of its input value using the unary negation operator (-). Therefore, when the __neg__ method is called, it effectively negates the Node object by leveraging the neg function.

**Note**: Ensure that the Node instance supports the unary negation operator to avoid runtime errors.

**Output Example**: If the Node instance represents a value of 5, applying the unary negation operator will result in -5. If the Node instance represents a value of -3.2, applying the unary negation operator will result in 3.2.
***
### FunctionDef __abs__(self)
**__abs__**: The function of __abs__ is to return the absolute value of the Node instance.

**parameters**: The parameters of this Function.
· self: The instance of the Node class on which the __abs__ method is called.

**Code Description**: The __abs__ method is a special method in Python that is called when the built-in abs() function is used on an instance of the Node class. When invoked, this method imports the abs function from the opto.trace.operators module and applies it to the Node instance (self). The imported abs function is designed to compute the absolute value of its input, leveraging Python's built-in abs() function. This allows the Node class to utilize the abs function to compute and return the absolute value of its instances.

**Note**: 
- Ensure that the Node instance supports the absolute value operation, either directly or through a custom implementation of the __abs__ method.
- The behavior and limitations of this method are consistent with Python's built-in abs() function.

**Output Example**: 
- If the Node instance represents a value of -5, the __abs__ method will return 5.
- If the Node instance represents a value of 3.14, the __abs__ method will return 3.14.
- If the Node instance is a custom object that implements the __abs__ method, the __abs__ method will return the result of that custom implementation.
***
### FunctionDef __invert__(self)
**__invert__**: The function of __invert__ is to perform a bitwise NOT operation on the instance of the Node class.

**parameters**: The parameters of this Function.
· self: The instance of the Node class on which the bitwise NOT operation will be performed.

**Code Description**: The __invert__ method is a special method in Python that allows the use of the bitwise NOT operator (~) on an instance of the Node class. When the ~ operator is applied to a Node instance, the __invert__ method is invoked. This method imports the invert function from the opto.trace.operators module and applies it to the instance (self).

The invert function, defined in the opto.trace.operators module, takes a single parameter x and returns the result of applying the bitwise NOT operation to x. The bitwise NOT operation inverts each bit of the input value. For example, if x is an integer, each bit in its binary representation will be flipped (0s become 1s and 1s become 0s).

In this context, the __invert__ method enables the Node class to support the bitwise NOT operation by leveraging the invert function. This allows developers to use the ~ operator directly on Node instances, making the code more intuitive and concise.

**Note**: Ensure that the Node instance supports the bitwise NOT operation. Using types that do not support this operation will result in a TypeError.

**Output Example**: 
- If the Node instance represents an integer with a value of 5, the return value will be -6.
- If the Node instance represents an integer with a value of 0, the return value will be -1.
***
### FunctionDef __round__(self, n)
**__round__**: The function of __round__ is to round the value of the Node object to a specified number of decimal places.

**parameters**: The parameters of this function.
· n: The number of decimal places to round to. This parameter is optional and can be None.

**Code Description**: The __round__ method is a special method in the Node class that allows rounding the value of the Node object to a specified number of decimal places. It imports the round function from the opto.trace.operators module and applies it to the Node instance (self). If the parameter n is provided, it is converted into a Node object using the node function from the same module. If n is not provided (i.e., it is None), the round function is called with None as the second argument.

The method works as follows:
1. It imports the round function from the opto.trace.operators module.
2. It checks if the parameter n is provided.
3. If n is provided, it converts n into a Node object using the node function.
4. It calls the round function with the Node instance (self) and the converted n (or None if n is not provided).
5. It returns the result of the round function.

The relationship with its callees is as follows:
- The node function is used to convert the parameter n into a Node object if n is provided.
- The round function is used to perform the actual rounding operation on the Node instance.

**Note**: 
- Ensure that the parameter n, if provided, can be interpreted as an integer to avoid runtime errors.
- The method relies on the round function from the opto.trace.operators module, which is a wrapper around Python's built-in round function.

**Output Example**: 
If the Node instance represents the value 3.14159 and n is 2, the method will return a Node object representing the value 3.14.
If the Node instance represents the value 3.14159 and n is 0, the method will return a Node object representing the value 3.
***
### FunctionDef __floor__(self)
**__floor__**: The function of __floor__ is to compute the largest integer less than or equal to the value of the current Node instance.

**parameters**: The parameters of this Function.
· self: An instance of the Node class.

**Code Description**: The __floor__ method is a special method in the Node class that allows instances of Node to be floored directly. When this method is called, it imports the floor function from the opto.trace.operators module and applies it to the current instance (self). The floor function, in turn, computes the largest integer less than or equal to the given number using Python's math.floor method. This operation is useful for rounding down the value of the Node instance to the nearest whole number.

**Note**: Ensure that the Node instance holds a numeric value that can be floored. If the value is not numeric, the floor function will raise a TypeError. Additionally, the math module must be available in the environment for the floor function to work correctly.

**Output Example**: 
- If the Node instance has a value of 3.7, calling __floor__() will return 3.
- If the Node instance has a value of -2.3, calling __floor__() will return -3.
***
### FunctionDef __ceil__(self)
**__ceil__**: The function of __ceil__ is to return the smallest integer greater than or equal to the value represented by the Node instance.

**parameters**: The parameters of this Function.
· self: An instance of the Node class.

**Code Description**: The __ceil__ method is a special method in the Node class that provides a ceiling operation on the Node instance. When invoked, it imports the ceil function from the opto.trace.operators module and applies it to the Node instance (self). The ceil function, in turn, rounds up the numeric value represented by the Node instance to the nearest integer. This method leverages the functionality of the ceil function to ensure that the Node instance's value is rounded up correctly.

The ceil function, which is called within __ceil__, is designed to handle any numeric type and uses the math.ceil() method from the math module to perform the rounding operation. By importing and utilizing this function, the __ceil__ method ensures that the Node instance's value is processed accurately and efficiently.

**Note**: Ensure that the Node instance represents a numeric value; otherwise, the ceil function will raise a TypeError. The math module must be available in the environment where the code is executed.

**Output Example**: 
- If the Node instance represents the value 4.2, __ceil__() will return 5.
- If the Node instance represents the value -3.7, __ceil__() will return -3.
- If the Node instance represents the value 7, __ceil__() will return 7.
***
### FunctionDef __trunc__(self)
**__trunc__**: The function of __trunc__ is to truncate the decimal part of a Node object, returning its integer part.

**parameters**: The parameters of this Function.
· self: The instance of the Node class that is to be truncated.

**Code Description**: The __trunc__ method is a special method in the Node class that allows instances of Node to be truncated to their integer representation. When __trunc__ is called on a Node instance, it imports the trunc function from the opto.trace.operators module and applies it to the instance (self). The trunc function, in turn, utilizes Python's math.trunc function to truncate the decimal part of the number, returning only the integer part. This ensures that any Node object can be converted to its integer form when necessary.

**Note**: 
- The Node instance should be compatible with the math.trunc function, typically meaning it should represent a numerical value.
- If the Node instance does not represent a number, the trunc function will raise a TypeError.

**Output Example**: 
If a Node instance represents the value 3.14, calling __trunc__ on this instance will return 3.
If a Node instance represents the value -2.99, calling __trunc__ on this instance will return -2.
***
### FunctionDef __add__(self, other)
**__add__**: The function of __add__ is to define the addition operation for Node objects, allowing them to be combined with other values.

**parameters**: The parameters of this function.
· self: The current instance of the Node class.
· other: The value to be added to the current Node instance. This can be of any type.

**Code Description**: The __add__ method in the Node class is designed to handle the addition of a Node object with another value. It first imports the necessary operators from the opto.trace.operators module. The method then checks the type of the _data attribute of the Node instance. If _data is a string, it uses the concat function from the operators module to concatenate the current Node instance with another Node instance created from the other parameter. If _data is not a string, it uses the add function from the operators module to add the current Node instance to another Node instance created from the other parameter.

The node function is used to ensure that the other parameter is converted into a Node object if it is not already one. This function provides a convenient way to create Node objects from various types of messages, ensuring consistency and ease of use.

The __add__ method is also called by the __radd__ method in the Node class, which allows for the reverse addition operation. This means that if the other parameter is on the left side of the addition operation, the __radd__ method will be invoked, which in turn calls the __add__ method to perform the addition.

**Note**: 
- Ensure that the types of the _data attribute and the other parameter are compatible with the + operator to avoid runtime errors.
- The behavior of the + operator varies depending on the types of the operands. For example, it concatenates strings and lists but adds numbers.

**Output Example**: 
- If self._data is "Hello" and other is "World", the return value will be a Node object with _data "HelloWorld".
- If self._data is 3 and other is 5, the return value will be a Node object with _data 8.
***
### FunctionDef __radd__(self, other)
**__radd__**: The function of __radd__ is to handle the reverse addition operation for Node objects, allowing them to be combined with other values when the Node instance is on the right side of the addition.

**parameters**: The parameters of this function.
· self: The current instance of the Node class.
· other: The value to be added to the current Node instance. This can be of any type.

**Code Description**: The __radd__ method in the Node class is designed to facilitate the addition operation when the Node instance appears on the right side of the addition operator. This method is invoked when the left operand does not support the addition operation with the right operand, which is an instance of the Node class. The __radd__ method simply calls the __add__ method of the Node class, passing the other parameter to it. This ensures that the addition logic defined in the __add__ method is reused, maintaining consistency in how Node objects are combined with other values.

The __add__ method, which is called by __radd__, handles the addition by checking the type of the _data attribute of the Node instance. If _data is a string, it concatenates the current Node instance with another Node instance created from the other parameter using the concat function from the opto.trace.operators module. If _data is not a string, it adds the current Node instance to another Node instance created from the other parameter using the add function from the same module. The node function ensures that the other parameter is converted into a Node object if it is not already one.

**Note**: 
- Ensure that the types of the _data attribute and the other parameter are compatible with the + operator to avoid runtime errors.
- The behavior of the + operator varies depending on the types of the operands. For example, it concatenates strings and lists but adds numbers.

**Output Example**: 
- If self._data is "Hello" and other is "World", the return value will be a Node object with _data "HelloWorld".
- If self._data is 3 and other is 5, the return value will be a Node object with _data 8.
***
### FunctionDef __sub__(self, other)
**__sub__**: The function of __sub__ is to perform a subtraction operation between the current Node object and another operand.

**parameters**: The parameters of this function.
· self: The current instance of the Node object.
· other: The operand to be subtracted from the current Node object. This operand can be any type that can be converted into a Node object.

**Code Description**: The __sub__ method is designed to enable the use of the subtraction operator (-) between Node objects or between a Node object and another operand. When the subtraction operator is used, this method is invoked. The method first imports the subtract function from the opto.trace.operators module. It then calls the node function from the opto.trace.nodes module to ensure that the operand 'other' is converted into a Node object if it is not already one. Finally, it calls the subtract function with the current Node object (self) and the newly created Node object from the operand 'other'. The subtract function performs the actual subtraction operation and returns the result.

**Note**: 
- Ensure that the operand 'other' is of a type that can be converted into a Node object to avoid runtime errors.
- The node function is used to handle the conversion of the operand into a Node object, providing flexibility in the types of operands that can be used with the subtraction operator.

**Output Example**: 
- If self is a Node object representing the value 10 and other is a Node object representing the value 5, the __sub__ method will return a Node object representing the value 5.
- If self is a Node object representing a list [1, 2, 3] and other is a Node object representing a list [1, 1, 1], the __sub__ method will return a Node object representing the list [0, 1, 2] (assuming the subtraction operation is defined for lists in this context).
***
### FunctionDef __mul__(self, other)
**__mul__**: The function of __mul__ is to enable the multiplication operation for Node objects using the * operator.

**parameters**: The parameters of this function.
· self: The current instance of the Node object.
· other: The operand to be multiplied with the current Node instance. This can be any type that is compatible with the multiplication operation.

**Code Description**: The __mul__ method allows for the multiplication of a Node object with another operand. When the * operator is used with a Node instance, this method is invoked. It imports the multiply function from the opto.trace.operators module and the node function from the opto.trace.nodes module.

The method first converts the other operand into a Node object using the node function. This ensures that the operand is in a compatible format for the multiplication operation. The node function checks if the operand is already a Node and returns it as is if true. Otherwise, it creates a new Node object from the operand.

After converting the operand, the method calls the multiply function with the current Node instance (self) and the newly created Node object as arguments. The multiply function performs the multiplication operation and returns the result.

This design allows for seamless multiplication of Node objects or Node-compatible objects using the * operator, enhancing the flexibility and usability of the Node class.

**Note**: Ensure that the operand passed to the * operator is compatible with the multiplication operation to avoid runtime errors. If the operand does not support multiplication, a TypeError will be raised.

**Output Example**: If self is a Node object representing the value 3 and other is 4, the result of self * other will be a Node object representing the value 12.
***
### FunctionDef __floordiv__(self, other)
**__floordiv__**: The function of __floordiv__ is to perform floor division between a Node object and another operand.

**parameters**: The parameters of this function.
· self: The Node object on which the floor division operation is invoked.
· other: The operand with which the floor division is to be performed. This can be any type that supports the floor division operation.

**Code Description**: The __floordiv__ method is a special method in the Node class that enables the use of the floor division operator (//) between a Node object and another operand. When this method is called, it imports the floor_divide function from the opto.trace.operators module and the node function from the opto.trace.nodes module.

The method first converts the other operand into a Node object using the node function. This ensures that the operand is compatible with the Node class's operations. It then applies the floor_divide function to the Node object (self) and the newly created Node object (other). The floor_divide function performs the floor division operation, which divides the two operands and rounds down the result to the nearest integer.

This method ensures that the floor division operation is performed correctly and consistently within the project's framework by leveraging the floor_divide function. The use of the node function guarantees that the other operand is appropriately handled as a Node object, maintaining the integrity of the Node class's operations.

**Note**: Ensure that the other operand is of a type that supports the floor division operation to avoid runtime errors. The method relies on the floor_divide function, which does not perform type checking or validation, so improper types may lead to unexpected behavior or exceptions.

**Output Example**: If self is a Node object representing the value 7 and other is an operand representing the value 3, the method call self // other will return a Node object representing the value 2, as 7 // 3 equals 2.
***
### FunctionDef __truediv__(self, other)
**__truediv__**: The function of __truediv__ is to perform division between the current Node instance and another operand.

**parameters**: The parameters of this function.
· self: The current instance of the Node class.
· other: The operand to divide the current Node instance by. This can be any type that supports division.

**Code Description**: The __truediv__ method is designed to handle the division operation for Node objects. When the division operator (/) is used between a Node instance and another operand, this method is invoked. The method first imports the divide function from the opto.trace.operators module. It then converts the other operand into a Node object using the node function from the opto.trace.nodes module. This ensures that both operands are Node objects, maintaining consistency within the framework. Finally, the method returns the result of the divide function, which performs the actual division operation between the two Node objects.

**Note**: 
- Ensure that the divisor (other) is not zero to avoid a ZeroDivisionError.
- The other operand should be of a type that supports the division operation.
- The node function is used to convert the other operand into a Node object if it is not already one, ensuring compatibility within the Node framework.

**Output Example**: If the current Node instance represents the value 10 and the other operand represents the value 2, the method will return a Node object representing the value 5.0.
***
### FunctionDef __mod__(self, other)
**__mod__**: The function of __mod__ is to perform the modulo operation between the current Node object and another value.

**parameters**: The parameters of this function.
· other: The value to be used as the divisor in the modulo operation. It can be of any type that supports the modulo operation.

**Code Description**: The __mod__ method is designed to enable the modulo operation between a Node object and another value. When this method is called, it first imports the mod function from the opto.trace.operators module. It then calls the node function to ensure that the other value is converted into a Node object if it is not already one. Finally, it applies the mod function to the current Node object (self) and the converted Node object (node(other)), and returns the result.

The node function is responsible for creating a Node object from a given message. If the message is already a Node, it returns it as is. This ensures that the other value is always in the form of a Node object before the modulo operation is performed.

The mod function takes two parameters, x and y, and returns the result of the modulo operation (x % y). This operation finds the remainder when x is divided by y. By integrating the mod function with the __mod__ method, Node objects can seamlessly perform the modulo operation with other values, enhancing their arithmetic capabilities.

**Note**: Ensure that the other value provided is of a type that supports the modulo operation to avoid runtime errors.

**Output Example**: If the current Node object represents the value 10 and the other value is 3, the return value will be a Node object representing the value 1. If the current Node object represents the value 20 and the other value is 7, the return value will be a Node object representing the value 6.
***
### FunctionDef __divmod__(self, other)
**__divmod__**: The function of __divmod__ is to perform the divmod operation on a Node object and another operand, returning the result.

**parameters**: The parameters of this function.
· self: The Node instance on which the __divmod__ method is called.
· other: The operand to be used in the divmod operation with the Node instance.

**Code Description**: The __divmod__ method is designed to enable the use of the divmod operation on Node objects within the project. When this method is called, it first imports the divmod function from the opto.trace.operators module and the node function from the opto.trace.nodes module. The method then converts the other operand into a Node object using the node function. This ensures that the divmod operation is performed between two Node objects, maintaining consistency within the project's framework.

The core functionality of the __divmod__ method is to delegate the actual divmod operation to the divmod function imported from opto.trace.operators. This function takes two parameters, x and y, and applies Python's built-in divmod function to them, returning a tuple containing the quotient and the remainder. By using this approach, the __divmod__ method ensures that the divmod operation can be seamlessly integrated with Node objects, providing a consistent interface for performing division and modulus operations within the project's tracing framework.

**Note**: Ensure that the other operand is of a type that can be converted into a Node object to avoid runtime errors. The method relies on the node function to handle this conversion, so any constraints or behaviors of the node function will apply here as well.

**Output Example**: If the Node instance represents the value 10 and the other operand is 3, the return value will be a tuple (3, 1), where 3 is the quotient and 1 is the remainder.
***
### FunctionDef __pow__(self, other)
**__pow__**: The function of __pow__ is to enable the power operation (exponentiation) on Node objects.

**parameters**: The parameters of this function.
· self: The Node object on which the power operation is being performed.
· other: The exponent value, which can be of any type that supports the power operation.

**Code Description**: The __pow__ method allows for the use of the power operator (**) directly on Node objects. When this method is called, it imports the power function from the opto.trace.operators module and applies it to the Node object (self) and the other value (other). 

The method first imports the necessary operators from the opto.trace.operators module. It then calls the power function, passing in the current Node object (self) and the result of the node function applied to the other value. The node function ensures that the other value is converted into a Node object if it is not already one, providing a consistent interface for the power operation.

This integration allows for intuitive mathematical operations within the project's framework, enabling users to perform exponentiation on Node objects seamlessly.

**Note**: 
- Ensure that the types of self and other are compatible with the power operation to avoid runtime errors.
- The node function is used to convert the other value into a Node object if it is not already one, ensuring consistency in the operation.

**Output Example**: 
If self is a Node object representing the value 2 and other is 3, the function will return a Node object representing the value 8, as 2**3 equals 8.
***
### FunctionDef __lshift__(self, other)
**__lshift__**: The function of __lshift__ is to perform a left bitwise shift operation on a Node object using another operand.

**parameters**: The parameters of this function.
· self: The current instance of the Node class.
· other: The operand to be used for the left bitwise shift operation.

**Code Description**: The __lshift__ method in the Node class is designed to facilitate the left bitwise shift operation using the << operator. When this method is invoked, it imports the lshift function from the opto.trace.operators module and the node function from the same module where the Node class is defined. The method then calls the lshift function, passing the current Node instance (self) and the result of the node function applied to the other operand.

The node function ensures that the other operand is converted into a Node object if it is not already one. This conversion is crucial for maintaining consistency within the Node class operations. The lshift function then performs the left bitwise shift operation on the two Node objects, self and the converted other operand, and returns the result.

This method allows instances of the Node class to use the << operator for left bitwise shift operations, leveraging the underlying lshift function to handle the actual bitwise manipulation.

**Note**: 
- Ensure that the other operand is of a type that can be converted into a Node object using the node function.
- The left bitwise shift operation is typically used with integer values, so the operands should support this operation to avoid runtime errors.

**Output Example**: 
If the current Node instance represents the value 4 (binary 100) and the other operand is 2, the method will return a Node object representing the value 16 (binary 10000), as the bits of 4 are shifted left by 2 positions.
***
### FunctionDef __rshift__(self, other)
**__rshift__**: The function of __rshift__ is to perform a bitwise right shift operation on the current Node instance and another operand.

**parameters**: The parameters of this function.
· self: The current instance of the Node class.
· other: The operand to be right-shifted with the current Node instance.

**Code Description**: The __rshift__ method is a special method in the Node class that facilitates the bitwise right shift operation between the current Node instance (self) and another operand (other). This method first imports the rshift function from the opto.trace.operators module. It then calls this rshift function, passing the current Node instance (self) and the result of the node function applied to the other operand.

The node function is used to ensure that the other operand is converted into a Node object if it is not already one. This conversion is necessary to maintain consistency and compatibility within the Node class operations. The rshift function, once called, performs the bitwise right shift operation (x >> y) on the two operands.

**Note**:
- Ensure that the other operand is of a type that supports the right shift operation to avoid runtime errors.
- The node function is used to convert the other operand into a Node object if it is not already one, ensuring compatibility within the Node class operations.

**Output Example**: If the current Node instance represents the value 8 (binary 1000) and the other operand is 2, the __rshift__ method will return a Node object representing the value 2 (binary 10).
***
### FunctionDef __and__(self, other)
**__and__**: The function of __and__ is to perform a bitwise AND operation between the current Node object and another operand.

**parameters**: The parameters of this function.
· self: The current instance of the Node object.
· other: The operand to perform the bitwise AND operation with. This can be any type that supports the bitwise AND operation.

**Code Description**: The __and__ method is designed to facilitate the bitwise AND operation between a Node object and another operand. When this method is called, it first imports the necessary operators from the `opto.trace.operators` module. Specifically, it imports the `and_` function, which is responsible for executing the bitwise AND operation.

The method then calls the `node` function from the `opto.trace.nodes` module to ensure that the `other` operand is converted into a Node object if it is not already one. The `node` function is a utility that either returns the operand as a Node object or creates a new Node object from the operand.

Finally, the `__and__` method applies the `and_` function to the current Node object (`self`) and the converted Node object (`node(other)`). The `and_` function performs the bitwise AND operation and returns the result.

**Note**: 
- Ensure that the `other` operand is of a type that supports the bitwise AND operation to avoid runtime errors.
- The `node` function is used to standardize the operand into a Node object, which simplifies the operation and ensures consistency.

**Output Example**: If the current Node object represents the value 6 (binary 110) and the `other` operand represents the value 3 (binary 011), the method call `self.__and__(other)` will return a Node object representing the value 2 (binary 010).
***
### FunctionDef __or__(self, other)
**__or__**: The function of __or__ is to perform a bitwise OR operation between the current Node instance and another Node instance.

**parameters**: The parameters of this function.
· self: The current Node instance.
· other: Another Node instance or a message that can be converted into a Node.

**Code Description**: The __or__ method is designed to enable the use of the "|" operator to combine two Node instances using a bitwise OR operation. When the "|" operator is used between two Node instances, this method is invoked.

1. The method first imports the `or_` function from the `opto.trace.operators` module.
2. It then calls the `node` function to ensure that the `other` parameter is converted into a Node instance if it is not already one.
3. Finally, it applies the `or_` function to the current Node instance (`self`) and the converted Node instance (`other`), returning the result.

The `node` function is responsible for creating a Node object from a message, ensuring that the `other` parameter is in the correct format for the bitwise OR operation. The `or_` function performs the actual bitwise OR operation between the two Node instances.

**Note**: Ensure that the `other` parameter can be converted into a Node instance to avoid errors. The `or_` function expects both operands to support the bitwise OR operation.

**Output Example**: If `self` is a Node instance representing the binary value 0101 and `other` is a Node instance representing the binary value 0011, the return value of `self | other` would be a Node instance representing the binary value 0111.
***
### FunctionDef __xor__(self, other)
**__xor__**: The function of __xor__ is to perform a bitwise XOR operation between the current Node instance and another Node instance or value.

**parameters**: The parameters of this function.
· self: The current Node instance.
· other: Another Node instance or value to perform the XOR operation with.

**Code Description**: The __xor__ method is designed to enable the use of the ^ operator to perform a bitwise XOR operation between Node objects. This method imports the xor function from the opto.trace.operators module and applies it to the current Node instance (self) and another Node instance or value (other). 

The method first imports the necessary operators from the opto.trace.operators module. It then calls the xor function, passing in the current Node instance (self) and the result of the node function applied to the other parameter. The node function ensures that the other parameter is converted into a Node object if it is not already one. This allows for seamless integration and operation between Node objects and other values.

The xor function itself performs the bitwise XOR operation, which compares each bit of its operands and returns 1 if the bits are different, and 0 if they are the same. This operation is useful in various scenarios, such as cryptography, error detection, and correction algorithms.

**Note**: Ensure that the other parameter is of a type that supports the bitwise XOR operation, such as integers or objects that implement the __xor__ method. The node function will handle the conversion of the other parameter to a Node object if necessary.

**Output Example**: If the current Node instance represents the value 5 (binary 0101) and the other parameter represents the value 3 (binary 0011), the result of the __xor__ method would be a Node object representing the value 6 (binary 0110).
***
### FunctionDef __iter__(self)
**__iter__**: The function of __iter__ is to provide an iterable interface for the Node object, allowing it to be iterated over in a consistent manner.

**parameters**: This function does not take any parameters.

**Code Description**: The __iter__ method is designed to make the Node object iterable. When called, it imports the iterate function from the opto.trace.containers module. The iterate function is then invoked with the Node object (self) as its argument. The iterate function determines the appropriate iterable class to use based on the type of the Node object's data attribute. It handles various types of collections such as lists, tuples, sets, and dictionaries, and returns an iterable object accordingly. This ensures that the Node object can be iterated over seamlessly, regardless of the type of its data attribute.

**Note**: 
- The Node object must have a data attribute that is a list, tuple, set, or dictionary.
- The iterate function handles the conversion of sets to lists and wraps items in lists or dictionaries with node objects.

**Output Example**: 
If the Node object's data attribute is a list [1, 2, 3], iterating over the Node object would yield:
```
node(1)
node(2)
node(3)
```
If the Node object's data attribute is a dictionary {'a': 1, 'b': 2}, iterating over the Node object would yield:
```
(node('a'), 1)
(node('b'), 2)
```
***
### FunctionDef __len__(self)
**__len__**: The function of __len__ is to return the number of elements contained in the Node object.

**parameters**: The parameters of this Function.
· self: Refers to the instance of the Node class.

**Code Description**: The __len__ method is a special method in Python that is used to define the behavior of the len() function for instances of a class. In this implementation, the __len__ method returns the length of the internal data structure, self._data, which is assumed to be a collection such as a list, dictionary, or any other iterable. The method ensures that the return type is an integer, which is a requirement for the __len__ method in Python. This method provides a straightforward way to get the size of the Node's data without directly accessing the internal data structure.

**Note**: 
- The __len__ method strictly returns an integer value representing the number of elements in the Node's internal data structure.
- If users need a Node object representing the length, they should use a different method, such as node.len(), instead of __len__.

**Output Example**: 
If the Node's internal data structure, self._data, contains 5 elements, calling len(node_instance) will return:
5
***
### FunctionDef __lt__(self, other)
**__lt__**: The function of __lt__ is to define the behavior of the less-than operator (<) for Node objects.

**parameters**: The parameters of this function.
· self: The instance of the Node object on the left-hand side of the < operator.
· other: The object on the right-hand side of the < operator, which can be another Node or a value that can be converted into a Node.

**Code Description**: The __lt__ method is a special method in Python that allows objects to implement behavior for the less-than operator (<). In this implementation, the method first imports the necessary operators from the opto.trace.operators module. It then calls the lt function from the operators module, passing in the current Node instance (self) and the result of converting the other object into a Node using the node function.

The node function is responsible for creating a Node object from the other parameter. If the other parameter is already a Node, it is returned as is. Otherwise, a new Node object is created from the other parameter. This ensures that the lt function always receives Node objects as its arguments.

The lt function from the operators module performs the actual comparison between the two Node objects and returns the result.

**Note**: 
- The __lt__ method relies on the node function to ensure that the other parameter is converted into a Node object if it is not already one.
- The comparison logic is delegated to the lt function from the opto.trace.operators module.

**Output Example**: A possible return value of the __lt__ method could be a boolean value, such as True or False, indicating whether the current Node instance is less than the other Node instance or value.
***
### FunctionDef __le__(self, other)
**__le__**: The function of __le__ is to define the behavior of the "less than or equal to" (<=) comparison operator for Node objects.

**parameters**: The parameters of this function.
· self: The instance of the Node object on the left-hand side of the <= operator.
· other: The object on the right-hand side of the <= operator, which can be another Node or a value that can be converted into a Node.

**Code Description**: The __le__ function is a special method in Python that allows the use of the <= operator with Node objects. When the <= operator is used, this method is called with the Node instance (self) and the other object (other) being compared.

1. The function imports the operators module from the opto.trace package as ops.
2. It then calls the le function from the ops module, passing in the current Node instance (self) and the result of the node function applied to the other object.

The node function is used to ensure that the other object is converted into a Node if it is not already one. This conversion is necessary because the le function in the ops module expects both arguments to be Node objects.

The le function in the ops module performs the actual comparison between the two Node objects and returns the result.

**Note**:
- The __le__ method ensures that comparisons using the <= operator are consistent and meaningful for Node objects.
- The node function is used to handle the conversion of the other object to a Node, ensuring compatibility with the le function in the ops module.

**Output Example**: A possible return value of the __le__ function could be a boolean value, such as True or False, indicating whether the left-hand side Node is less than or equal to the right-hand side Node.
***
### FunctionDef __gt__(self, other)
**__gt__**: The function of __gt__ is to compare if the current Node object is greater than another object.

**parameters**: The parameters of this function.
· self: The current instance of the Node object.
· other: The object to compare with the current Node instance.

**Code Description**: The __gt__ method is a special method in Python used to define the behavior of the greater-than operator (>) for instances of a class. In this implementation, the method first imports the operators module from the opto.trace package. It then calls the gt function from the operators module, passing the current Node instance (self) and another Node instance created from the other parameter using the node function.

The node function is responsible for converting the other parameter into a Node object if it is not already one. This ensures that the comparison is always between two Node objects. The gt function from the operators module performs the actual comparison and returns the result.

**Note**:
- The other parameter can be any object that can be converted into a Node using the node function.
- The comparison relies on the gt function from the operators module, which should be defined to handle Node comparisons appropriately.

**Output Example**: A possible return value of the __gt__ method could be a boolean value, such as True or False, indicating whether the current Node instance is greater than the other object.
***
### FunctionDef __ge__(self, other)
**__ge__**: The function of __ge__ is to compare the current Node object with another object to determine if the current Node is greater than or equal to the other object.

**parameters**: The parameters of this function.
· self: The current instance of the Node object.
· other: The object to compare with the current Node.

**Code Description**: The __ge__ method is a special method in Python used to define the behavior of the greater than or equal to (>=) operator for instances of a class. In this implementation, the method imports the `opto.trace.operators` module as `ops` and uses the `ge` function from this module to perform the comparison.

The method first converts the `other` object into a Node object using the `node` function. This ensures that the comparison is always between two Node objects, regardless of the initial type of `other`. The `node` function is designed to create a Node object from a given message, handling various scenarios such as whether the message is already a Node, whether it should be trainable, and whether it has any constraints.

Once the `other` object is converted into a Node, the `ge` function from the `ops` module is called with `self` and the newly created Node as arguments. The `ge` function is responsible for performing the actual comparison and returning the result.

**Note**:
- The `__ge__` method ensures that comparisons are always made between Node objects by converting the `other` object using the `node` function.
- The `node` function handles various scenarios to create a Node object, making the comparison process robust and flexible.

**Output Example**: A possible return value of the `__ge__` method could be a boolean value, such as `True` or `False`, indicating whether the current Node is greater than or equal to the `other` object.
***
### FunctionDef __eq__(self, other)
**__eq__**: The function of __eq__ is to compare the current Node object with another object to determine if they are equal.

**parameters**: The parameters of this Function.
· self: The instance of the Node class.
· other: The object to compare with the current Node instance.

**Code Description**: The __eq__ method is designed to enable comparison between a Node object and another object to check for equality. The method first checks if the 'other' object is an instance of the Node class. If it is, the method extracts the 'data' attribute from the 'other' Node object. Then, it compares the '_data' attribute of the current Node instance with the 'other' object (or its 'data' attribute if 'other' is a Node). The method returns True if the '_data' attributes are equal, and False otherwise.

**Note**: 
- This method overrides the default equality comparison behavior in Python.
- It ensures that two Node objects are considered equal if their '_data' attributes are equal.
- If 'other' is not a Node instance, the method directly compares 'self._data' with 'other'.

**Output Example**: 
- If `self._data` is 5 and `other` is a Node instance with `data` attribute 5, the method returns True.
- If `self._data` is 5 and `other` is 10, the method returns False.
***
### FunctionDef __hash__(self)
**__hash__**: The function of __hash__ is to return the hash value of the Node object.

**parameters**: The parameters of this Function.
· self: Refers to the instance of the Node class.

**Code Description**: The __hash__ method in the Node class is an override of the built-in __hash__ method. It calls the __hash__ method of its superclass using the super() function. This ensures that the hash value of the Node object is consistent with the hash value defined in its superclass. By doing so, it maintains the integrity and uniqueness of the hash value for instances of the Node class, which is crucial for operations that rely on hashing, such as using Node instances as keys in dictionaries or storing them in sets.

**Note**: 
- The __hash__ method should be consistent with the __eq__ method. If two objects are considered equal (using the __eq__ method), they must return the same hash value.
- Overriding the __hash__ method is essential when you need custom behavior for hashing, but in this case, it simply defers to the superclass implementation.

**Output Example**: The return value of the __hash__ method will be an integer representing the hash value of the Node object, as determined by the superclass's __hash__ method. For example, if the superclass's __hash__ method returns 123456 for a particular Node instance, then calling hash(node_instance) will also return 123456.
***
### FunctionDef __bool__(self)
**__bool__**: The function of __bool__ is to provide a boolean representation of the Node object.

**parameters**: The parameters of this Function.
· self: Refers to the instance of the Node class.

**Code Description**: The __bool__ method is a special method in Python that is used to define the boolean value of an object. In this implementation, the method returns the boolean value of the instance variable `_data`. The expression `bool(self._data)` converts `_data` to its boolean equivalent. If `_data` is a non-empty value (such as a non-empty list, string, or a non-zero number), the method will return `True`. If `_data` is an empty value (such as an empty list, string, or zero), the method will return `False`. This allows the Node object to be used in boolean contexts, such as in conditional statements.

**Note**: 
- Ensure that the `_data` attribute is properly initialized in the Node class, as its value directly affects the boolean representation of the Node object.
- This method does not trace the conversion process, meaning it directly returns the boolean value without additional logging or processing.

**Output Example**: 
- If `_data` is a non-empty list, e.g., `[1, 2, 3]`, the return value will be `True`.
- If `_data` is an empty list, e.g., `[]`, the return value will be `False`.
***
### FunctionDef format(self)
**format**: The function of format is to format the data contained within the Node object if the data is a string.

**parameters**: The parameters of this Function.
· *args: Variable length argument list.
· **kwargs: Arbitrary keyword arguments.

**Code Description**: The `format` function first checks if the `_data` attribute of the Node object is of type `str`. If `_data` is not a string, it raises an `AttributeError` indicating that the object does not have a `format` attribute. This ensures that only string data can be formatted using this function. 

Next, the function imports the `opto.trace.operators` module as `ops`. It then calls the `format` function from the `ops` module, passing the current Node object (`self`) along with any additional arguments (`*args`) and keyword arguments (`**kwargs`). This delegation allows the `format` function in the `ops` module to handle the actual formatting logic.

**Note**: 
- Ensure that the `_data` attribute of the Node object is a string before calling the `format` function to avoid an `AttributeError`.
- The `opto.trace.operators` module must be available and contain a `format` function that can handle the passed arguments and keyword arguments.

**Output Example**: 
If the `_data` attribute of the Node object is a string, the `format` function will return the formatted string as processed by the `opto.trace.operators.format` function. For example, if `_data` is `"Hello, {}"` and the arguments passed are `"World"`, the return value might be `"Hello, World"`.
***
### FunctionDef capitalize(self)
**capitalize**: The function of capitalize is to convert the first character of the string stored in the `_data` attribute of the Node object to uppercase.

**parameters**: This function does not take any parameters.

**Code Description**: The `capitalize` function first checks if the `_data` attribute of the Node object is of type `str`. If `_data` is not a string, it raises an `AttributeError` indicating that the object does not have a `capitalize` attribute. This ensures that the function is only applied to string data. If `_data` is a string, the function imports the `capitalize` function from the `opto.trace.operators` module and returns the result of calling this `capitalize` function with the current Node object (`self`) as its argument. This modular approach allows for the actual capitalization logic to be handled by the `opto.trace.operators` module, promoting code reusability and separation of concerns.

**Note**: 
- Ensure that the `_data` attribute of the Node object is a string before calling the `capitalize` function to avoid raising an `AttributeError`.
- The function relies on the `opto.trace.operators` module, so make sure this module is correctly implemented and accessible.

**Output Example**: If the `_data` attribute of the Node object is `"hello world"`, the `capitalize` function will return `"Hello world"`.
***
### FunctionDef lower(self)
**lower**: The function of lower is to convert the string data contained within the object to lowercase.

**parameters**: This function does not take any parameters.

**Code Description**: The lower function is designed to operate on an instance's internal data, specifically converting it to lowercase if it is a string. The function first checks if the type of the instance's _data attribute is a string. If _data is not a string, it raises an AttributeError, indicating that the object does not have a 'lower' attribute. This ensures that the function only attempts to convert string data to lowercase, preventing type errors. If the _data attribute is a string, the function imports the lower function from the opto.trace.operators module and applies it to the instance, returning the result.

**Note**: 
- This function will raise an AttributeError if the _data attribute is not of type str.
- Ensure that the opto.trace.operators module is available and contains a lower function that can handle the conversion.

**Output Example**: 
If the _data attribute of the instance is "Hello World", the function will return "hello world".
***
### FunctionDef upper(self)
**upper**: The function of upper is to convert the internal data of the Node object to uppercase if it is a string.

**parameters**: The parameters of this Function.
· This function does not take any parameters.

**Code Description**: The upper function first checks if the internal data attribute (_data) of the Node object is of type string. If _data is not a string, it raises an AttributeError indicating that the object does not have an 'upper' attribute. If _data is a string, the function imports the upper function from the opto.trace.operators module and returns the result of calling this imported upper function with the current Node object as its argument.

**Note**: 
- This function will only work if the _data attribute of the Node object is a string. If _data is of any other type, an AttributeError will be raised.
- Ensure that the opto.trace.operators module is correctly implemented and accessible, as this function relies on it.

**Output Example**: 
If the _data attribute of the Node object is "hello", calling the upper function will return "HELLO".
***
### FunctionDef swapcase(self)
**swapcase**: The function of swapcase is to convert all uppercase characters in the string to lowercase and vice versa.

**parameters**: The parameters of this Function.
· None

**Code Description**: The swapcase function is a method designed to operate on an instance's _data attribute. It first checks if the _data attribute is of type str. If _data is not a string, the function raises an AttributeError, indicating that the object does not have a swapcase attribute. This ensures that the function only processes string data. If the _data attribute is a string, the function imports the swapcase function from the opto.trace.operators module and applies it to the instance, returning the result. This modular approach allows for the swapcase operation to be defined and maintained separately in the operators module.

**Note**: 
- The _data attribute must be a string; otherwise, an AttributeError will be raised.
- Ensure that the opto.trace.operators module is correctly implemented and accessible.

**Output Example**: 
If the _data attribute of the instance is "Hello World", the swapcase function will return "hELLO wORLD".
***
### FunctionDef title(self)
**title**: The function of title is to retrieve the title attribute of the Node object if it exists.

**parameters**: The parameters of this Function.
· self: Refers to the instance of the Node class.

**Code Description**: The title function checks if the _data attribute of the Node instance is a string. If _data is not a string, it raises an AttributeError indicating that the object does not have a title attribute. If _data is a string, it imports the title function from the opto.trace.operators module and returns the result of calling this imported title function with the current Node instance as its argument.

**Note**: 
- Ensure that the _data attribute of the Node instance is a string before calling the title function to avoid an AttributeError.
- The function relies on the title function from the opto.trace.operators module, so ensure that this module is correctly imported and available.

**Output Example**: 
If the _data attribute of the Node instance is a string, the function will return the result of the title function from the opto.trace.operators module. For example, if the title function in the operators module processes the string and returns a formatted title, the output will be that formatted title.
***
### FunctionDef split(self, sep, maxsplit)
**split**: The function of split is to divide a string into a list of substrings based on a specified separator.

**parameters**: The parameters of this Function.
· sep: The delimiter according to which the string is split. If not specified or None, any whitespace string is a separator.
· maxsplit: The maximum number of splits to do. -1 (the default value) means no limit on the number of splits.

**Code Description**: The split function is designed to operate on an object that contains a string. It first checks if the object's _data attribute is of type str. If _data is not a string, it raises an AttributeError indicating that the split operation is not applicable to the object's data type. If _data is a string, the function imports the split function from the opto.trace.operators module and delegates the actual splitting operation to this imported function, passing along the separator and maxsplit parameters.

**Note**: 
- This function will raise an AttributeError if the _data attribute of the object is not a string.
- Ensure that the opto.trace.operators module is available and contains a split function that can handle the parameters passed to it.

**Output Example**: 
If the _data attribute of the object is "hello world" and the split function is called with the default parameters, the return value would be:
```python
['hello', 'world']
```
***
### FunctionDef strip(self, chars)
**strip**: The function of strip is to remove leading and trailing characters from a string stored in the object's `_data` attribute.

**parameters**: The parameters of this Function.
· chars: A string specifying the set of characters to be removed. If not provided, whitespace characters are removed by default.

**Code Description**: The `strip` function first checks if the `_data` attribute of the object is of type `str`. If `_data` is not a string, it raises an `AttributeError` indicating that the object does not have a `strip` attribute. This ensures that the function is only applied to string data. The function then imports the `strip` function from the `opto.trace.operators` module and calls this imported `strip` function, passing the current object and the `chars` parameter to it. This design allows for the actual stripping operation to be handled by the `strip` function in the `opto.trace.operators` module, potentially allowing for more complex or customized stripping behavior.

**Note**: 
- Ensure that the `_data` attribute is a string before calling the `strip` function to avoid the `AttributeError`.
- The `chars` parameter is optional. If not provided, the function will default to removing whitespace characters.

**Output Example**: 
If `_data` is `"  example  "` and `chars` is not provided, the return value might be `"example"`. If `_data` is `"--example--"` and `chars` is `"-"`, the return value might be `"example"`.
***
### FunctionDef replace(self, old, new, count)
**replace**: The function of replace is to substitute occurrences of a specified substring within the Node's data with a new substring.

**parameters**: The parameters of this Function.
· self: The instance of the Node class.
· old: The substring that needs to be replaced.
· new: The substring that will replace the old substring.
· count: (optional) The maximum number of occurrences to replace. Default is -1, which means replace all occurrences.

**Code Description**: The replace function is designed to perform a substring replacement operation on the data contained within a Node object. The function first checks if the data type of the Node's internal data (_data) is a string. If it is not a string, it raises an AttributeError, indicating that the replace operation is not applicable to the data type.

The function then imports the replace function from the opto.trace.operators module. It proceeds to call this imported replace function, passing the current Node instance (self), and the old and new substrings wrapped in Node objects using the node function. The count parameter is also passed along to control the number of replacements.

The node function is used to ensure that the old and new substrings are appropriately converted into Node objects if they are not already. This ensures consistency and proper handling within the replace operation.

**Note**: 
- The replace function only works if the Node's internal data is a string. Attempting to use it with non-string data will result in an AttributeError.
- The count parameter allows for partial replacements, where only a specified number of occurrences are replaced. If count is set to -1, all occurrences will be replaced.

**Output Example**: A possible return value of the replace function could be a new Node object with the specified substring replacements applied to its internal string data. For instance, if the original Node's data is "hello world" and the replace function is called with old="world", new="there", the resulting Node's data would be "hello there".
***
### FunctionDef items(self)
**items**: The function of items is to retrieve and return the items associated with the current instance of the Node class.

**parameters**: The parameters of this Function.
· This function does not take any parameters other than the implicit 'self' which refers to the instance of the Node class.

**Code Description**: The items function is designed to import the items function from the opto.trace.containers module and then call this imported function, passing the current instance (self) as an argument. This allows the function to retrieve the items related to the current Node instance by leveraging the functionality provided in the opto.trace.containers module.

**Note**: 
- Ensure that the opto.trace.containers module is correctly installed and accessible in your environment, as the items function relies on it.
- This function assumes that the imported items function from the opto.trace.containers module is designed to handle the Node instance appropriately.

**Output Example**: 
The return value of this function will depend on the implementation of the items function in the opto.trace.containers module. Typically, it might return a list, dictionary, or another collection of items associated with the Node instance. For example:
```python
[
    {'id': 1, 'name': 'Item1'},
    {'id': 2, 'name': 'Item2'}
]
```
***
### FunctionDef pop(self, __index)
**pop**: The function of pop is to remove and return an element from a Node object at a specified index.

**parameters**: The parameters of this function.
· __index: An optional integer parameter that specifies the index of the element to be removed. The default value is -1, which means the last element will be removed.

**Code Description**: The pop function is designed to remove and return an element from a Node object at a specified index. It imports the pop function from the opto.trace.operators module and utilizes the node function to handle the index parameter. The node function ensures that the index is properly converted into a Node object if it is not already one. This allows for consistent handling of the index parameter within the pop function.

The pop function works as follows:
1. It imports the necessary operators from the opto.trace.operators module.
2. It calls the ops.pop function, passing the current Node object (self) and the index parameter converted to a Node object using the node function.

The relationship with its callees is as follows:
- The node function is used to ensure that the index parameter is properly converted into a Node object.
- The ops.pop function from the opto.trace.operators module is used to perform the actual removal and return of the element from the Node object.

**Note**: 
- The default value of the __index parameter is -1, which means the last element will be removed if no index is specified.
- The node function is used to handle the index parameter, ensuring it is properly converted into a Node object.

**Output Example**: A possible return value of the pop function could be the element that was removed from the Node object at the specified index. For example, if the Node object contained the elements [1, 2, 3] and the index parameter was 1, the return value would be 2, and the Node object would be updated to [1, 3].
***
### FunctionDef append(self)
**append**: The function of append is to add elements to a collection or list within the Node object.

**parameters**: The parameters of this function.
· self: The instance of the Node class on which the method is called.
· *args: Variable-length positional arguments to be appended.
· **kwargs: Variable-length keyword arguments to be appended.

**Code Description**: The `append` method is a member of the `Node` class in the `opto.trace.nodes.py` module. This method is designed to add elements to a collection or list within the Node object. It achieves this by internally calling the `call` method with the string "append" as the function name, along with any positional (`*args`) and keyword arguments (`**kwargs`) provided.

The `call` method, which is invoked by `append`, dynamically calls the specified function (in this case, "append") on the `Node` object. It first converts all positional and keyword arguments to `Node` objects using the `node` function, ensuring that the arguments are compatible with the Node's internal structure. After conversion, it retrieves the "append" function from the `Node` object using `getattr` and invokes it with the converted arguments.

This design allows the `append` method to flexibly handle various types of input while ensuring that all elements being appended are properly formatted as `Node` objects.

**Note**:
- The `append` method relies on the `call` method to dynamically invoke the "append" function on the `Node` object.
- All arguments passed to `append` are converted to `Node` objects before being appended.
- The `self` parameter must be a valid instance of the `Node` class.

**Output Example**: A possible return value of the `append` method could be the result of the "append" function invoked on the `Node` object with the provided arguments. For instance, if the "append" function adds elements to a list, the return value might be the updated list.
***
## ClassDef ParameterNode
**ParameterNode**: The function of ParameterNode is to represent a trainable node in a computational graph.

**attributes**:
- value: The initial value of the node.
- name: The name of the node.
- trainable: A boolean indicating whether the node is trainable or not.
- description: A string describing the node.
- constraint: A constraint on the node.
- info: Additional information about the node.

**Code Description**: The ParameterNode class is a subclass of the Node class and represents a trainable node in a computational graph. It is used to store and manipulate data in the graph. The class has an initializer method that takes in various parameters such as value, name, trainable, description, constraint, and info. These parameters are used to initialize the attributes of the ParameterNode object.

The initializer method also calls the initializer method of the superclass (Node) to set the value and name attributes. It then sets the trainable, description, constraint, and info attributes based on the provided parameters. Additionally, it adds the ParameterNode object to the 'parameter' dependency set.

The ParameterNode class also defines a __str__ method that returns a string representation of the node. This method allows users to easily look up the node in the feedback dictionary.

**Note**:
- The ParameterNode class inherits from the Node class, which is a data node in a directed graph.
- The value attribute represents the initial value of the node.
- The name attribute represents the name of the node.
- The trainable attribute indicates whether the node is trainable or not.
- The description attribute provides information about the node.
- The constraint attribute represents a constraint on the node.
- The info attribute stores additional information about the node.

**Output Example**:
A possible return value of the __str__ method could be "ParameterNode: (name, dtype=<class 'type'>, data=value)".
### FunctionDef __init__(self, value)
**__init__**: The function of __init__ is to initialize an instance of the ParameterNode class with specified attributes.

**parameters**: The parameters of this Function.
· value: The initial value assigned to the ParameterNode.
· name: An optional name for the ParameterNode. Default is None.
· trainable: A boolean indicating whether the parameter is trainable. Default is True.
· description: A string describing the ParameterNode. Default is "[ParameterNode] This is a ParameterNode in a computational graph."
· constraint: An optional constraint applied to the parameter. Default is None.
· info: Additional optional information about the parameter. Default is None.

**Code Description**: The __init__ function initializes a ParameterNode object by calling the constructor of its superclass with the provided parameters. It sets the initial value, name, trainable status, description, constraint, and additional information for the ParameterNode. After initializing the superclass, it adds the current instance to the '_dependencies' dictionary under the 'parameter' key. This ensures that the ParameterNode is properly registered within the computational graph's dependency management system.

**Note**: Points to note about the use of the code
- Ensure that the 'value' parameter is provided when creating an instance of ParameterNode.
- The 'name', 'constraint', and 'info' parameters are optional and can be omitted if not needed.
- The 'trainable' parameter defaults to True, indicating that the parameter will be included in training processes unless explicitly set to False.
- The 'description' parameter provides a default description but can be customized as needed.
***
### FunctionDef __str__(self)
**__str__**: The function of __str__ is to provide a string representation of the ParameterNode object.

**parameters**: The parameters of this Function.
· self: The instance of the ParameterNode class.

**Code Description**: The `__str__` method is designed to return a human-readable string that represents the current state of a `ParameterNode` object. This method is particularly useful for debugging and logging purposes, as it provides a concise summary of the node's key attributes.

When called, the `__str__` method constructs a string that includes:
- The name of the node, accessed via `self.name`. This name is managed by the `name` method of the `AbstractNode` class, which returns the value of the private attribute `_name`.
- The data type of the node's data, obtained using `type(self._data)`.
- The actual data stored in the node, accessed via `self._data`.

The string is formatted as follows:
```
ParameterNode: ({self.name}, dtype={type(self._data)}, data={self._data})
```
This format ensures that the string includes the node's name, the type of its data, and the data itself, all in a clear and structured manner.

**Note**: 
- The `__str__` method should be used when a string representation of the `ParameterNode` is needed, such as in logging or debugging scenarios.
- Ensure that the node's data (`self._data`) is in a state that can be meaningfully represented as a string.

**Output Example**: 
If a `ParameterNode` object has a name "node:0", data type `<class 'int'>`, and data `42`, the `__str__` method will return:
```
ParameterNode: (node:0, dtype=<class 'int'>, data=42)
```
***
## ClassDef MessageNode
**MessageNode**: The MessageNode class represents the output of an operator in a computational graph.

**attributes**:
- value: The value of the node.
- inputs: The input nodes of the MessageNode. It can be a list or a dictionary.
- description: A string that describes the operator associated with the MessageNode.
- constraint: A constraint on the node.
- name: The name of the node.
- info: Additional information about the node.

**Code Description**:
The MessageNode class is a subclass of the Node class and inherits its attributes and methods. It overrides the __init__ method to include the inputs, description, constraint, name, and info parameters. The inputs parameter can be a list or a dictionary, and it represents the input nodes of the MessageNode. The description parameter is a string that describes the operator associated with the MessageNode. The constraint parameter specifies a constraint on the node. The name parameter is the name of the node. The info parameter is additional information about the node.

The __init__ method initializes the MessageNode by calling the __init__ method of the Node class and passing the value, name, description, constraint, and info parameters. It checks if the inputs parameter is a list or a dictionary and creates a dictionary with the names of the nodes as keys if it is a list. It then assigns the inputs to the _inputs attribute of the MessageNode. If the GRAPH.TRACE flag is False, it checks if the MessageNode has any inputs and raises an assertion error if it does. It adds the parents and dependencies if the GRAPH.TRACE flag is True.

The inputs property returns a copy of the _inputs attribute.

The __str__ method returns a string representation of the MessageNode, including its name, data type, and data.

The _add_feedback method is called to add feedback from a child node. It adds the feedback to the _feedback attribute of the MessageNode.

The external_dependencies property returns a set of external dependencies based on the info attribute of the MessageNode.

The _add_dependencies method is called to add dependencies from a parent node. It adds the parameter and expandable dependencies to the _dependencies attribute of the MessageNode.

**Note**:
- The MessageNode class is used to represent the output of an operator in a computational graph.
- The inputs parameter can be a list or a dictionary, and it represents the input nodes of the MessageNode.
- The description parameter is a string that describes the operator associated with the MessageNode.
- The constraint parameter specifies a constraint on the node.
- The name parameter is the name of the node.
- The info parameter is additional information about the node.

**Output Example**:
A possible appearance of the MessageNode object when converted to a string could be:
"MessageNode: (node_name, dtype=<class 'int'>, data=10)"
### FunctionDef __init__(self, value)
**__init__**: The function of __init__ is to initialize a MessageNode object with the given parameters.

**parameters**:
- self: The instance of the class.
- value: The value of the MessageNode object.
- inputs: The inputs to the MessageNode object, which can be either a list or a dictionary of Node objects.
- description: The description of the MessageNode object.
- constraint: An optional constraint on the MessageNode object.
- name: An optional name for the MessageNode object.
- info: Additional information about the MessageNode object.

**Code Description**:
The `__init__` function is the constructor of the MessageNode class. It initializes a MessageNode object with the provided parameters. The function first calls the constructor of the parent class, AbstractNode, passing the value, name, description, constraint, and info parameters.

Next, the function checks if the inputs parameter is either a list or a dictionary. If it is not, an assertion error is raised with the message "Inputs to MessageNode must be a list or a dict." This ensures that the inputs are of the correct type.

If the inputs parameter is a list, the function creates a dictionary with the names of the nodes as keys and the nodes themselves as values. This is done to ensure that the inputs can be accessed by their names.

The function then assigns the inputs to the _inputs attribute of the MessageNode object.

If the GRAPH.TRACE flag is not set, indicating that tracing is not enabled, the function asserts that the _inputs attribute is empty. This is because when not tracing, a MessageNode should have no inputs.

Next, the function iterates over the items in the _inputs dictionary. For each item, it checks if the value is an instance of the Node class. If it is not, an assertion error is raised with the message "Input {k} is not a Node." This ensures that all inputs are valid Node objects.

For each valid input, the function calls the _add_parent method of the MessageNode object to add the input as a parent. This method adds the parent node to the hierarchical structure of the graph.

The function also calls the _add_dependencies method of the MessageNode object to add the dependencies on parameters and expandable nodes. This method updates the _dependencies attribute of the MessageNode object.

Finally, if the external_dependencies attribute of the MessageNode object is not empty, indicating that there are external dependencies, the function adds the MessageNode object to the 'expandable' set of the _dependencies attribute.

**Note**:
- The inputs parameter should be either a list or a dictionary of Node objects.
- When not tracing, a MessageNode should have no inputs.
- The inputs should be valid Node objects.
- The _add_parent method adds the parent node to the hierarchical structure of the graph.
- The _add_dependencies method adds the dependencies on parameters and expandable nodes to the MessageNode object.
- The external_dependencies attribute indicates the external dependencies of the MessageNode object.
***
### FunctionDef inputs(self)
**inputs**: The function of inputs is to return a copy of the `_inputs` attribute of the object.

**parameters**:
- self: The current object.

**Code Description**:
The `inputs` function is a method of the `MessageNode` class. It returns a copy of the `_inputs` attribute of the object. The `_inputs` attribute is a dictionary that stores the input nodes of the `MessageNode` object.

The purpose of this function is to provide access to the input nodes of the `MessageNode` object. By returning a copy of the `_inputs` attribute, it ensures that the original dictionary is not modified when accessing the input nodes.

This function can be useful when you need to retrieve the input nodes of a `MessageNode` object for further processing or analysis.

**Note**:
- The returned copy of the `_inputs` attribute is a shallow copy, which means that the keys and values of the dictionary are copied, but the objects themselves are not. If the values of the dictionary are mutable objects, modifying them will affect the original objects.
- The `_inputs` attribute is a private attribute and should not be modified directly. Use the `inputs` function to access the input nodes instead.

**Output Example**:
```
{
    'input1': <Node object at 0x12345678>,
    'input2': <Node object at 0x23456789>,
    ...
}
```
***
### FunctionDef __str__(self)
**__str__**: The function of __str__ is to provide a string representation of the MessageNode object.

**parameters**: The parameters of this Function.
· self: The instance of the MessageNode class.

**Code Description**: The __str__ method in the MessageNode class returns a formatted string that includes the name of the node, the data type of the node's data, and the data itself. This method is useful for debugging and logging purposes, as it provides a clear and concise representation of the node's state.

The method calls the `name` method from the AbstractNode class to retrieve the name of the node. The `name` method returns the value of the private attribute `_name`, which is set when the node is registered in the graph. The `type(self._data)` function is used to get the data type of the node's data, and `self._data` is used to access the actual data stored in the node.

The returned string follows the format: "MessageNode: (name, dtype=data_type, data=data)", where `name` is the node's name, `data_type` is the type of the data, and `data` is the actual data.

**Note**: 
- The __str__ method should be used when a string representation of the MessageNode object is needed, such as in logging or debugging scenarios.
- Ensure that the node has been properly initialized and registered before calling this method to avoid any unexpected behavior.

**Output Example**: 
If the name of the node is "node:0", the data type is `<class 'int'>`, and the data is `42`, the __str__ method will return:
```
MessageNode: (node:0, dtype=<class 'int'>, data=42)
```
***
### FunctionDef _add_feedback(self, child, feedback)
**_add_feedback**: The function of _add_feedback is to add feedback from a child node.

**parameters**: The parameters of this Function.
· child: The child node from which the feedback is received.
· feedback: The feedback data provided by the child node.

**Code Description**: The _add_feedback function is designed to handle feedback from child nodes within a MessageNode. It first calls the parent class's _add_feedback method to ensure any inherited behavior is executed. After that, it asserts that the length of the feedback list for the given child node is exactly one. This assertion ensures that each child node provides only one piece of feedback, maintaining the integrity and expected behavior of the MessageNode.

**Note**: 
- This function relies on the parent class's _add_feedback method, so it is crucial that the parent class is correctly implemented.
- The assertion will raise an AssertionError if a child node provides more than one piece of feedback, which helps in debugging and maintaining the correct structure of feedback within the MessageNode.
***
### FunctionDef external_dependencies(self)
**external_dependencies**: The function of external_dependencies is to determine the external dependencies of a MessageNode object.

**parameters**:
- self: The MessageNode object itself.

**Code Description**:
The `external_dependencies` function is a method within the `MessageNode` class that calculates and returns the external dependencies of the node. It checks if the `info` attribute of the `MessageNode` instance is a dictionary and if it contains an 'output' key that is an instance of the `Node` class. If these conditions are met, it compares the length of the parameter dependencies of the 'output' node with the parameter dependencies of the current `MessageNode`. If the 'output' node has more parameter dependencies, it returns the difference between the two sets of dependencies. This indicates that the `external_dependencies` function relies on the `parameter_dependencies` function of the `Node` class to determine the parameter dependencies of the nodes it interacts with.

The purpose of the `external_dependencies` function is to identify any external dependencies that the `MessageNode` relies on, which are not already accounted for in its own parameter dependencies. By returning the set of external dependencies, users can gain insights into the dependencies of the `MessageNode` and ensure that all necessary dependencies are properly handled.

It is important to note that the `external_dependencies` function assumes that the `info` attribute is a dictionary and that the 'output' key contains a valid `Node` object. If these assumptions are not met, the function will return an empty set.

**Note**: 
- The `external_dependencies` function relies on the `parameter_dependencies` function of the `Node` class to determine the parameter dependencies of the nodes it interacts with.
- The `info` attribute of the `MessageNode` instance must be a dictionary and contain an 'output' key that is an instance of the `Node` class for the function to work correctly.

**Output Example**: A possible return value of the `external_dependencies` function could be a set of external dependencies, such as:
```
{'dependency1', 'dependency2', 'dependency3'}
```
***
### FunctionDef _add_dependencies(self, parent)
**_add_dependencies**: The function of _add_dependencies is to add dependencies on parameters and expandable nodes to the current MessageNode object.

**Parameters**:
- parent: The parent node to add as a dependency.

**Code Description**:
The `_add_dependencies` function is used to add dependencies on parameters and expandable nodes to the current MessageNode object. It takes a `parent` parameter, which is the parent node to be added as a dependency.

The function first checks if the `parent` is not the same as the current object itself. If it is, an assertion error is raised with the message "Cannot add self as a parent."

Next, it checks if the `parent` is an instance of the `Node` class. If it is not, an assertion error is raised with a message indicating that the `parent` is not a Node.

If both assertions pass, the function proceeds to add the dependencies. It updates the `_dependencies` dictionary of the current object by taking the union of the `parameter` and `expandable` dependencies of the `parent` node. This is done using the bitwise OR operator (`|`).

Finally, the function returns without any explicit return value.

**Note**:
- The `parent` parameter should be a valid Node object.
- The function assumes that the current object is a MessageNode.
- The function updates the `_dependencies` dictionary of the current object to include the dependencies from the `parent` node.
***
## ClassDef ExceptionNode
**ExceptionNode**: The ExceptionNode class represents a node containing an exception message.

**attributes**:
- value: The exception value.
- inputs: The input nodes of the ExceptionNode. It can be a list or a dictionary.
- description: A string that describes the ExceptionNode.
- constraint: A constraint on the node.
- name: The name of the node.
- info: Additional information about the node.

**Code Description**:
The ExceptionNode class is a subclass of the MessageNode class and inherits its attributes and methods. It overrides the __init__ method to include the value, inputs, description, constraint, name, and info parameters. The value parameter represents the exception value. The inputs parameter can be a list or a dictionary, and it represents the input nodes of the ExceptionNode. The description parameter is a string that describes the ExceptionNode. The constraint parameter specifies a constraint on the node. The name parameter is the name of the node. The info parameter is additional information about the node.

The __init__ method initializes the ExceptionNode by calling the __init__ method of the MessageNode class and passing the value, inputs, description, constraint, name, and info parameters. It checks if the value is an instance of trace.ExecutionError and formats the value accordingly. It then calls the __init__ method of the MessageNode class and passes the formatted value, inputs, description, constraint, name, and info parameters.

**Note**:
- The ExceptionNode class represents a node containing an exception message.
- The value parameter represents the exception value.
- The inputs parameter can be a list or a dictionary, and it represents the input nodes of the ExceptionNode.
- The description parameter is a string that describes the ExceptionNode.
- The constraint parameter specifies a constraint on the node.
- The name parameter is the name of the node.
- The info parameter is additional information about the node.

**Output Example**:
A possible appearance of the ExceptionNode object when converted to a string could be:
"ExceptionNode: (node_name, dtype=<class 'int'>, data=10)"
### FunctionDef __init__(self, value)
**__init__**: The function of __init__ is to initialize an instance of the ExceptionNode class.

**parameters**:
- value: The exception value to be stored in the ExceptionNode.
- inputs: The inputs to the ExceptionNode, which can be either a list of nodes or a dictionary of nodes.
- description: A string that describes the ExceptionNode. The default value is "[ExceptionNode] This is node containing the error of execution."
- constraint: An optional constraint on the ExceptionNode.
- name: An optional name for the ExceptionNode.
- info: Additional information about the ExceptionNode.

**Code Description**:
The __init__ method of the ExceptionNode class initializes an instance of the ExceptionNode with the given parameters. It first assigns the value parameter to the variable e. Then, it uses regular expression to extract the error type from the string representation of the exception value. The re.search function searches for the pattern "<class '(.*)'>" in the string and retrieves the matched group, which represents the error type. 

Next, it imports the trace module from the opto package. This import is necessary because the isinstance function is used later in the code. 

The code then checks if the value is an instance of the ExecutionError class from the trace module. If it is not, it formats the exception message by concatenating the error type and the string representation of the exception value. This ensures that the exception message is informative and includes the error type.

Finally, the super().__init__ method is called to initialize the ExceptionNode instance with the value, inputs, description, constraint, name, and info parameters. The super() function is used to call the __init__ method of the base class (Node) and pass the parameters to it.

**Note**:
- The ExceptionNode class is used to represent a node in a computational graph that contains an exception value. It is typically used to handle errors that occur during the execution of code within a tracing context.
- The value parameter should be an instance of the Exception class or a subclass of it.
- The inputs parameter should be a list of nodes or a dictionary of nodes that serve as inputs to the ExceptionNode.
- The description parameter is optional and can be used to provide additional information about the ExceptionNode.
- The constraint parameter is optional and can be used to specify a constraint on the ExceptionNode.
- The name parameter is optional and can be used to assign a name to the ExceptionNode.
- The info parameter is optional and can be used to provide additional information about the ExceptionNode.
- When creating an instance of the ExceptionNode class, make sure to provide the necessary inputs and ensure that the value parameter is an instance of the Exception class or a subclass of it.
***
