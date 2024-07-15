## FunctionDef bundle(description, n_outputs, node_dict, traceable_code, wrap_output, unpack_input, trainable, catch_execution_error, allow_external_dependencies, overwrite_python_recursion)
**bundle**: The function of bundle is to wrap a function as a FunModule, which returns node objects.

**parameters**:
- description: A string that describes the function.
- n_outputs: An integer that specifies the number of outputs the wrapped function should have.
- node_dict: Either "auto" or a dictionary that maps input names to node objects.
- traceable_code: A boolean value indicating whether the code should be traced using nodes.
- wrap_output: A boolean value indicating whether the output should be wrapped as a node object.
- unpack_input: A boolean value indicating whether the input should be unpacked.
- trainable: A boolean value indicating whether the wrapped function is trainable.
- catch_execution_error: A boolean value indicating whether execution errors should be caught.
- allow_external_dependencies: A boolean value indicating whether external dependencies are allowed.
- overwrite_python_recursion: A boolean value indicating whether Python recursion should be overwritten.

**Code Description**: The bundle function is a decorator that wraps a function as a FunModule. It takes in various parameters to customize the behavior of the wrapped function. Inside the decorator, it creates a FunModule object with the specified parameters and returns it.

The decorator function also captures the locals of the calling function using the inspect module. This allows the wrapped function to access the locals of the calling function.

The wrapped function can be called with the same input signature as the original function. The output of the wrapped function is a node object, which represents the result of the function computation. The node object can be used in further computations or as inputs to other functions.

The bundle function provides flexibility in customizing the behavior of the wrapped function. It allows specifying the number of outputs, mapping input names to node objects, tracing the code using nodes, wrapping the output as a node object, unpacking the input, making the wrapped function trainable, catching execution errors, allowing external dependencies, and overwriting Python recursion.

**Note**: 
- The wrapped function should have a consistent input signature.
- The wrapped function can access the locals of the calling function.
- The output of the wrapped function is a node object.
- The behavior of the wrapped function can be customized using the parameters of the bundle function.

**Output Example**: 
```python
@bundle(description="This is a bundled function", n_outputs=2)
def add(a, b):
    return a + b, a - b

output = add(3, 2)
print(output)
# Output: (5, 1)
```
### FunctionDef decorator(fun)
Doc is waiting to be generated...
***
## ClassDef trace_nodes
**trace_nodes**: The function of trace_nodes is to act as a context manager for tracking which nodes are read or used in an operator.

**attributes**: The attributes of this Class.
· No explicit attributes are defined within this class.

**Code Description**: The trace_nodes class is designed to manage the tracking of nodes that are accessed during the execution of an operator. It achieves this by leveraging Python's context management protocol, which includes the `__enter__` and `__exit__` methods.

- The `__enter__` method initializes a new set to store the nodes that will be used and appends this set to the global `USED_NODES` list. It then returns this set, allowing it to be used within the context.
- The `__exit__` method is called when the context is exited. It removes the set of used nodes from the global `USED_NODES` list, ensuring that the tracking is properly cleaned up.

In the context of its usage within the `forward` method of the `FunModule` class, the trace_nodes context manager is used to keep track of all nodes that are accessed during the execution of the operator function (`self.fun`). When the `forward` method is called, it enters the trace_nodes context, which starts tracking the nodes. After the function execution, the context is exited, and the set of used nodes is then available for further processing.

The `forward` method uses this set of nodes to construct the inputs of a `MessageNode` from the function inputs or the set of used nodes. It also identifies any external dependencies, which are nodes used to create the outputs but not included in the inputs. If external dependencies are not allowed and are detected, an exception is raised.

**Note**: 
- Ensure that the global `USED_NODES` list is properly managed to avoid any unintended side effects.
- The trace_nodes context manager should be used within a controlled environment where the global state can be safely modified and restored.

**Output Example**: 
When used within the `forward` method of the `FunModule` class, the trace_nodes context manager might return a set of nodes that were accessed during the function execution. For example:
```
with trace_nodes() as used_nodes:
    # Function execution that accesses nodes
    pass
# used_nodes might contain: {Node1, Node2, Node3}
```
### FunctionDef __enter__(self)
**__enter__**: The function of __enter__ is to initialize and return a new set of nodes, and to append this set to the global list USED_NODES.

**parameters**: The parameters of this Function.
· self: Refers to the instance of the class in which this method is defined.

**Code Description**: The __enter__ method is a special method used in the context management protocol. When an instance of the class containing this method is used in a with statement, the __enter__ method is automatically invoked at the beginning of the block. In this implementation, the method performs the following actions:
1. Initializes an empty set named `nodes`.
2. Appends this set to the global list `USED_NODES`.
3. Returns the set `nodes`.

This allows the set of nodes to be used within the with block and ensures that it is tracked in the global `USED_NODES` list.

**Note**: 
- Ensure that the global list `USED_NODES` is defined before using this method.
- This method is typically paired with an `__exit__` method to handle cleanup actions when the with block is exited.

**Output Example**: 
When the __enter__ method is called, it returns an empty set. For example:
```
with some_instance as nodes:
    # nodes is an empty set
    print(nodes)  # Output: set()
```
***
### FunctionDef __exit__(self, type, value, traceback)
**__exit__**: The function of __exit__ is to handle the cleanup process when exiting a context managed by a with statement.

**parameters**: The parameters of this Function.
· type: The exception type, if an exception was raised.
· value: The exception instance, if an exception was raised.
· traceback: The traceback object, if an exception was raised.

**Code Description**: The __exit__ method is a special method used in context management to define cleanup actions when exiting a context. In this specific implementation, the __exit__ method removes the last element from the USED_NODES list by calling the pop() method. This indicates that the context manager is maintaining a stack of nodes, and upon exiting the context, it ensures that the most recently added node is removed from the stack. This is a common pattern in resource management where resources are pushed onto a stack when entering a context and popped off when exiting to ensure proper cleanup and resource deallocation.

**Note**: 
- Ensure that the USED_NODES list is properly initialized and managed elsewhere in the code to avoid potential errors.
- This method does not handle exceptions; it simply performs the cleanup action. If exception handling is required, it should be implemented separately.
***
## ClassDef FunModule
Doc is waiting to be generated...
### FunctionDef __init__(self, fun, description, n_outputs, node_dict, traceable_code, wrap_output, unpack_input, trainable, catch_execution_error, allow_external_dependencies, overwrite_python_recursion, ldict)
**__init__**: The function of __init__ is to initialize an instance of the FunModule class.

**Parameters**:
- self: The instance of the FunModule class.
- fun: A callable object representing the function to be wrapped.
- description: An optional string describing the function module.
- n_outputs: An integer indicating the number of outputs of the function.
- node_dict: A dictionary, None, or "auto" representing the node dictionary.
- traceable_code: A boolean indicating whether the code is traceable or not.
- wrap_output: A boolean indicating whether to wrap the output or not.
- unpack_input: A boolean indicating whether to unpack the input or not.
- trainable: A boolean indicating whether the function is trainable or not.
- catch_execution_error: A boolean indicating whether to catch execution errors or not.
- allow_external_dependencies: A boolean indicating whether to allow external dependencies or not.
- overwrite_python_recursion: A boolean indicating whether to overwrite Python recursion or not.
- ldict: A dictionary or None representing the local dictionary.

**Code Description**: The __init__ function initializes an instance of the FunModule class. It takes in various parameters such as fun, description, n_outputs, node_dict, traceable_code, wrap_output, unpack_input, trainable, catch_execution_error, allow_external_dependencies, overwrite_python_recursion, and ldict.

The function starts by asserting that the ldict parameter is either None or a dictionary. If ldict is None, an empty dictionary is assigned to self.ldict. Otherwise, a copy of ldict is assigned to self.ldict.

If traceable_code is True, the unpack_input parameter is set to False and the allow_external_dependencies parameter is set to True. This is because when the code is traceable, there is no need to unpack the input and there may be new nodes created in the code block.

The function then asserts that the fun parameter is callable and that the node_dict parameter is either a dictionary, None, or "auto".

Next, the source code of the function is obtained using the inspect.getsource() function. If the source code starts with a decorator line, the decorator line is removed and only the function definition is kept. Otherwise, the source code is trimmed.

The function constructs an info dictionary containing information about the function module. This includes the function name, docstring, signature, source code, output, external dependencies, and node dictionary.

If the description parameter is None, a description is generated using the function name and docstring. The get_op_name() function is called to extract the operator type from the description. The extracted operator type is combined with the function name and docstring to create a meaningful description.

The function assigns the provided parameters to the corresponding attributes of the FunModule instance. It also sets the parameter attribute to None.

If the n_outputs parameter is greater than 1, a warning message is displayed indicating that setting n_outputs>1 will be deprecated.

Finally, if the trainable parameter is True, the function asserts that overwrite_python_recursion is also True. It then searches for the function signature in the source code and creates a ParameterNode object with the source code as the value and "__code" as the name. This ParameterNode represents the code constraint for the trainable function.

**Note**: 
- The ldict parameter must be a dictionary or None.
- The fun parameter must be a callable object.
- The node_dict parameter must be a dictionary, None, or "auto".
- The description parameter will be generated if it is None.
- The n_outputs parameter should be used with caution as setting n_outputs>1 will be deprecated.
- The trainable parameter requires overwrite_python_recursion to be True.
- The source code of the function is obtained using the inspect.getsource() function.
- The get_op_name() function is used to extract the operator type from the description.
- The info dictionary contains information about the function module.
- The parameter attribute is set to None unless the trainable parameter is True.
***
### FunctionDef filter_global_namespaces(self, keys)
**filter_global_namespaces**: The function of filter_global_namespaces is to filter out keys that already exist in the current global namespace.

**parameters**: The parameters of this Function.
· keys: A list of keys to be filtered.

**Code Description**: The filter_global_namespaces function takes a list of keys as input and returns a new list containing only those keys that do not already exist in the current global namespace. The function initializes an empty list called filtered_keys to store the keys that pass the filtering criteria. It then iterates over each key in the input list. For each key, it checks if the key exists in the global namespace using the globals() function. If the key is found in the global namespace, it is skipped. Otherwise, the key is appended to the filtered_keys list. Finally, the function returns the filtered_keys list.

**Note**: 
- This function relies on the current global namespace, which means its behavior can vary depending on the existing global variables and functions at the time of execution.
- Ensure that the input list keys does not contain any unintended or sensitive keys that might be skipped due to their presence in the global namespace.

**Output Example**: 
If the global namespace contains the keys 'a' and 'b', and the input list is ['a', 'b', 'c', 'd'], the function will return ['c', 'd'].
***
### FunctionDef fun(self)
**fun**: The function of fun is to execute dynamically generated code and return the resulting function.

**parameters**:
- self: The instance of the class.
- *args: Variable length argument list.
- **kwargs: Arbitrary keyword arguments.

**Code Description**:
The `fun` function is a method of the current class. It is responsible for executing dynamically generated code and returning the resulting function. The function takes in variable length arguments (`*args`) and arbitrary keyword arguments (`**kwargs`).

The function first checks if the `parameter` attribute of the instance is `None`. If it is `None`, it returns the `_fun` attribute of the instance, which is the original function.

If the `parameter` attribute is not `None`, the function retrieves the code from the `parameter` attribute and stores it in the `code` variable. It then tries to import all the global namespaces from the original function by creating a local dictionary (`ldict`) and copying the global dictionary (`gdict`) from the `_fun` attribute. The local dictionary is updated with the `ldict` attribute of the instance. The `exec` function is then called to define the function using the code, the global dictionary, and the local dictionary. The name of the function is extracted from the code using regular expression. The resulting function is stored in the `fun` variable.

If there is an exception during the execution of the code (SyntaxError, NameError, KeyError, or OSError), an `ExecutionError` instance is created with details about the exception. The `ExecutionError` instance is then raised to indicate the error.

Finally, the function returns the resulting function (`fun`).

**Note**:
- The `fun` function is used within the `trace_nodes` context manager.
- The `fun` function relies on the `parameter` attribute to retrieve the dynamically generated code.
- The resulting function may be different from the original function if the code modifies the global namespaces.

**Output Example**:
The output of the `fun` function is the resulting function that is executed from the dynamically generated code.
***
### FunctionDef name(self)
**name**: The function of `name` is to retrieve the operator type from the description attribute of the FunModule instance.

**parameters**: This method does not take any parameters other than `self`.

**Code Description**: The `name` method is a member of the `FunModule` class in the `bundle.py` file. It is designed to extract and return the operator type from the `description` attribute of the `FunModule` instance. This is achieved by calling the `get_op_name` function, which processes the `description` string to find and return the operator type enclosed in square brackets at the beginning of the description.

The `get_op_name` function uses a regular expression to search for the operator type. If the operator type is found, it is returned; otherwise, a `ValueError` is raised. This ensures that the `description` attribute of the `FunModule` instance is correctly formatted and contains the necessary operator type information.

The `name` method is utilized within the `wrap` method of the same class. In the `wrap` method, the `name` method is used to set the `name` attribute of the `MessageNode` or `ExceptionNode` that is created based on the output of the function. This ensures that the nodes have a meaningful and accurate name that reflects the operator type.

**Note**: 
- The `description` attribute of the `FunModule` instance must contain the operator type enclosed in square brackets at the beginning.
- If the `description` does not contain the operator type, a `ValueError` will be raised by the `get_op_name` function.

**Output Example**: 
If the `description` attribute of the `FunModule` instance is "[Add] Add two numbers", the `name` method will return "Add".
***
### FunctionDef forward(self)
**forward**: The `forward` function is responsible for executing the operator function (`self.fun`) and returning the resulting nodes. It takes in variable length arguments (`*args`) and arbitrary keyword arguments (`**kwargs`).

**parameters**:
- `self`: The instance of the class.
- `*args`: Variable length argument list.
- `**kwargs`: Arbitrary keyword arguments.

**Code Description**:
The `forward` function is a method of the `FunModule` class in the `bundle.py` file. It is the main function that executes the operator function and handles the processing of inputs and outputs. 

The function starts by initializing the `_args` and `_kwargs` variables with the provided arguments (`args` and `kwargs`). If the `unpack_input` attribute of the instance is `True`, the function extracts the data from the container of nodes by calling the `to_data` function on the arguments.

Next, the function checks if the `overwrite_python_recursion` attribute is `True` and the `parameter` attribute is `None`. If both conditions are met, it sets the Python tracer to the `tracer` function defined within the `forward` function. This tracer modifies the local/global dictionary of the frame to ensure that recursive calls of the wrapped function call the unwrapped function.

The function then enters a `trace_nodes` context manager using the `with` statement. This context manager tracks the nodes that are read or used in the operator function. The `used_nodes` set is created and appended to the global `USED_NODES` list. This set will contain the nodes that are accessed during the execution of the operator function.

Within the context manager, the operator function (`self.fun`) is executed with the provided arguments (`_args` and `_kwargs`). If the `catch_execution_error` attribute is `True`, the function wraps the execution of the operator function in a try-except block. If an exception occurs during the execution, it is stored in the `outputs` variable. Otherwise, the `outputs` variable contains the result of the operator function.

After the execution of the operator function, the context manager is exited, and the set of used nodes is available for further processing.

The function then constructs the inputs of the `MessageNode` from the function inputs or the set of used nodes. If the `node_dict` attribute of the instance is `None`, the function generates a warning and creates a dictionary of inputs using the names of the nodes in the `used_nodes` set. If the `node_dict` attribute is not `None`, the function updates the input signature (`spec`) with the `node_dict` dictionary. It then iterates over the input signature and creates nodes for each input value using the `create_node` function. The resulting inputs dictionary is stored in the `inputs` variable.

Next, the function identifies any external dependencies, which are nodes used to create the outputs but not included in the inputs. It creates a list of external dependencies by iterating over the `used_nodes` set and checking if each node is present in the `inputs` dictionary using the `contain` function.

If the number of external dependencies is greater than 0 and the `allow_external_dependencies` attribute is `False`, the function raises a `TraceMissingInputsError` exception. This exception indicates that not all nodes used in the operator function are specified as inputs of the returned node.

If the `GRAPH.TRACE` attribute is `False`, the `inputs` dictionary is cleared, as there is no need to keep track of the inputs if tracing is not enabled.

Finally, the function wraps the output as a `MessageNode` or an `ExceptionNode` depending on the type of the output. If the `n_outputs` attribute of the instance is 1 or the output is an instance of `Exception`, the function calls the `wrap` function with the output, inputs, and external dependencies. Otherwise, it creates a tuple of wrapped nodes by calling the `wrap` function for each output element.

The function returns the resulting nodes.

**Note**:
- The `forward` function is the main function that executes the operator function and handles the processing of inputs and outputs.
- The `trace_nodes` context manager is used to track the nodes that are accessed during the execution of the operator function.
- The `tracer` function modifies the local/global dictionary of the frame to ensure that recursive calls of the wrapped function call the unwrapped function.
- The `to_data` function is used to extract the data from a node or a container of nodes.
- The `wrap` function is used to wrap the output of the operator function as a `MessageNode` or an `ExceptionNode`.
- The `TraceMissingInputsError` exception is raised when not all nodes used in the operator function are specified as inputs of the returned node.
- The `contain` function is used to check if a given node is present in a container of nodes.

**Output Example**:
The `forward` function returns the resulting nodes of the operator function. The output can be a single `MessageNode` or `ExceptionNode` if the `n_outputs` attribute is 1 or the output is an exception. If the `n_outputs` attribute is greater than 1, the output is a tuple of `MessageNode` or `ExceptionNode` objects.
#### FunctionDef tracer(frame, event, arg)
**tracer**: The function of tracer is to modify the local and global dictionaries of a frame to ensure that recursive calls of a wrapped function invoke the unwrapped function.

**parameters**: The parameters of this Function.
· frame: The frame object representing the current execution context.
· event: A string representing the type of event that occurred (e.g., 'call', 'return').
· arg: An optional argument that may be passed to the tracer function (default is None).

**Code Description**: The tracer function is designed to handle recursive calls within a wrapped function by modifying the local and global dictionaries of the frame. When the function is called, it first checks if the current frame's code object matches the code object of the wrapped function (`self._fun.__code__`). If it does, the function proceeds to handle different types of events:

- **Call Event**: When the event is 'call', the function checks if the function name exists in the frame's local or global dictionaries. If the function name is found in the local dictionary and it does not match the wrapped function (`self._fun`), the `update_local` function is called to update the local variable to the wrapped function. If the function name is found in the global dictionary and it does not match the wrapped function, the original function (an instance of `FunModule`) is saved in `_bundled_func`, and the global dictionary is updated to point to the wrapped function.

- **Return Event**: When the event is 'return', the function checks if the function name exists in the global dictionary. If it does, the global dictionary is restored to the original function saved in `_bundled_func`.

The `update_local` function is used within the tracer to update the local variables in the frame. This ensures that recursive calls invoke the unwrapped function, maintaining the correct function behavior.

**Note**: Points to note about the use of the code
- Ensure that the frame object passed to the tracer function is valid and corresponds to the correct execution context.
- Be cautious when modifying local and global variables in a frame, as it can affect the execution flow and state of the program.
- The tracer function relies on the `update_local` function to update local variables, which uses the `ctypes` module to interact with the Python C API. This may have implications for portability and compatibility across different Python versions and implementations.

**Output Example**: The tracer function returns itself, allowing it to be used as a callback for tracing events.
***
#### FunctionDef create_node(n)
**create_node**: The function of create_node is to convert an input into a Node object, specifically handling instances of FunModule by extracting their parameters if they exist.

**parameters**: The parameters of this Function.
· n: The input to be converted into a Node. This can be an instance of FunModule or any other type that the node function can handle.

**Code Description**: The create_node function is designed to facilitate the creation of Node objects from various inputs. It first checks if the input n is an instance of FunModule and whether it has a non-None parameter attribute. If both conditions are met, it assigns n to its parameter attribute. This step ensures that if n is a FunModule with a parameter, the parameter is used for the Node creation instead of the FunModule itself. After this check, the function calls the node function with n as its argument. The node function then processes n according to its own logic, which includes handling whether n is already a Node, and whether it should be trainable or have constraints.

**Note**: 
- This function is particularly useful when dealing with FunModule instances, as it ensures that their parameters are used for Node creation.
- The function relies on the node function to handle the actual creation of the Node object, including any additional parameters like name, trainable, and constraint.

**Output Example**: A possible return value of the create_node function could be a Node object created from the parameter of a FunModule instance, or directly from the input if it is not a FunModule. For example, if n is a FunModule with a parameter, the return value would be a Node object created from that parameter. If n is a simple message, the return value would be a Node object created from that message.
***
***
### FunctionDef wrap(self, output, inputs, external_dependencies)
**wrap**: The function of wrap is to wrap the output as a MessageNode of inputs as the parents.

**parameters**:
- output: The output of the operator function.
- inputs: The input nodes of the MessageNode. It can be a list or a dictionary.
- external_dependencies: A list of nodes that are used to create the outputs but not included in the inputs.

**Code Description**:
The `wrap` function is a method of the `FunModule` class in the `bundle.py` file. It is designed to wrap the output of the operator function as a `MessageNode` with the specified inputs as its parents. The function takes three parameters: `output`, `inputs`, and `external_dependencies`.

The `wrap` function first checks if the `wrap_output` attribute of the `FunModule` instance is `False`. If it is `False`, the function returns the output as is, assuming it is already a `Node` object. This is because there is no need to wrap the output if it is already a `Node`.

If the `wrap_output` attribute is `True`, the function proceeds to check if the `parameter` attribute of the `FunModule` instance is not `None`. If it is not `None`, it means that the operator is a trainable operation and a new op eval needs to be created. In this case, the `inputs` dictionary is updated with the `__code` parameter, which is the code block of the function. The `description` and `name` variables are set accordingly to indicate that this is an eval operator. The `fun_name` attribute of the `FunModule` instance is also updated to "eval".

If the `parameter` attribute is `None`, the `description` and `name` variables are set to the `description` and `name` attributes of the `FunModule` instance, respectively.

Next, the function checks if the `output` is `None`. If it is `None`, it creates a `MessageNode` with `None` as the value and the specified `description`, `inputs`, `name`, and `info` attributes. This is useful when the operator does not produce any output.

If the `output` is an instance of `Exception`, it creates an `ExceptionNode` with the `output` as the value and the specified `description`, `inputs`, `name`, and `info` attributes. The `ExceptionNode` represents an exception raised by the operator.

If the `output` is neither `None` nor an instance of `Exception`, it creates a copy of the `info` attribute and updates it with the `output` value. It then creates a `MessageNode` with the `output` as the value and the specified `description`, `inputs`, `name`, and updated `info` attributes.

The `wrap` function returns the created `MessageNode` or `ExceptionNode` depending on the type of the `output`.

**Note**:
- The `wrap` function is used to wrap the output of the operator function as a `MessageNode` or `ExceptionNode`.
- The `wrap_output` attribute of the `FunModule` instance determines whether the output needs to be wrapped.
- The `parameter` attribute of the `FunModule` instance determines whether the operator is a trainable operation.
- The `description`, `name`, and `info` attributes of the `FunModule` instance are used to provide additional information for the created nodes.

**Output Example**:
If the `output` is `None`, the function returns a `MessageNode` with `None` as the value:
```
MessageNode(None, description="[Node] This is a node in a computational graph.", inputs=inputs, name=name, info=info)
```
If the `output` is an exception, the function raises an `ExecutionError` with an `ExceptionNode` containing the exception details.
***
### FunctionDef is_valid_output(output)
**is_valid_output**: The function of is_valid_output is to check whether the given output is a valid output for a computational graph node.

**parameters**:
- output: The output to be checked.

**Code Description**:
The `is_valid_output` function takes an `output` as input and checks whether it is a valid output for a computational graph node. The function returns `True` if the `output` is an instance of the `Node` class or if it is a tuple containing only instances of the `Node` class. Otherwise, it returns `False`.

The function first checks if the `output` is an instance of the `Node` class using the `isinstance` function. If it is, the function returns `True`.

If the `output` is not an instance of the `Node` class, the function checks if it is a tuple using the `isinstance` function. If it is a tuple, the function uses a list comprehension and the `isinstance` function to check if all elements in the tuple are instances of the `Node` class. If all elements are instances of the `Node` class, the function returns `True`. Otherwise, it returns `False`.

**Note**:
- The `is_valid_output` function is used to validate the output of a computational graph node. It ensures that the output is compatible with the expected input types for further computations.
- The function assumes that the `Node` class is defined and imported correctly.

**Output Example**:
- Example 1:
    ```python
    output = Node(5)
    print(is_valid_output(output))
    ```
    Output:
    ```
    True
    ```

- Example 2:
    ```python
    output = (Node(1), Node(2), Node(3))
    print(is_valid_output(output))
    ```
    Output:
    ```
    True
    ```

- Example 3:
    ```python
    output = (Node(1), 2, Node(3))
    print(is_valid_output(output))
    ```
    Output:
    ```
    False
    ```
***
### FunctionDef __get__(self, obj, objtype)
**__get__**: The function of __get__ is to support instance methods by binding the __call__ method to an instance of the Module class.

**parameters**: The parameters of this Function.
· self: Refers to the instance of the FunModule class.
· obj: The instance of the class where the FunModule instance is accessed as an attribute.
· objtype: The type of the class where the FunModule instance is accessed as an attribute.

**Code Description**: The __get__ method is a descriptor method used to support instance methods in the FunModule class. When an instance of FunModule is accessed as an attribute of another class instance, the __get__ method is invoked. This method uses functools.partial to bind the __call__ method of the FunModule instance to the obj parameter, which is the instance of the class where FunModule is accessed.

By doing this, the __call__ method of the FunModule instance is effectively converted into an instance method of the obj instance. This allows the __call__ method to be invoked with obj as its first argument, enabling it to operate in the context of the obj instance.

In the context of the project, the __call__ method of the FunModule class is designed to invoke the forward method of the Module class with the provided arguments. The __get__ method ensures that when the __call__ method is accessed through an instance of another class, it behaves as an instance method, maintaining the correct binding to the obj instance.

**Note**: 
- The __get__ method is crucial for enabling the FunModule class to be used as a descriptor, allowing its __call__ method to be bound to instances of other classes.
- Ensure that the obj parameter is an instance of a class that correctly utilizes the FunModule instance as an attribute.

**Output Example**: The return value of the __get__ method is a functools.partial object that binds the __call__ method to the obj instance. This allows the __call__ method to be invoked as if it were an instance method of the obj instance. For example, if obj is an instance of a class that has a FunModule instance as an attribute, accessing this attribute and calling it will invoke the __call__ method with obj as its first argument.
***
## FunctionDef to_data(obj)
**to_data**: The function of to_data is to extract the data from a node or a container of nodes.

**parameters**:
- obj: The input object, which can be a node or a container of nodes.

**Code Description**:
The to_data function is designed to extract the data from a node or a container of nodes. It takes an input object and recursively extracts the data from each node in the object. The function handles different types of objects and performs specific operations based on their type.

For node containers (tuple, list, dict, set, NodeContainer), the function recursively extracts the data from each node in the container. It uses list comprehension or dictionary comprehension to iterate over the nodes and call the to_data function recursively on each node.

For individual nodes (instances of the Node class), the function simply returns the data attribute of the node.

If the input object is an instance of NodeContainer, the function creates a copy of the object and iterates over its attributes using the __dict__ attribute. It then sets the corresponding attribute in the output object to the result of calling the to_data function recursively on the attribute value.

If the input object is not a node or a node container, the function simply returns the object as is.

**Note**:
- The function relies on the isinstance() function to determine the type of the input object and perform the appropriate operations.
- The function uses the copy module to create a copy of the NodeContainer object.
- The function assumes that the Node and NodeContainer classes are defined and imported correctly.

**Output Example**:
- Input: Node(5)
  Output: 5

- Input: [Node(1), Node(2), Node(3)]
  Output: [1, 2, 3]

- Input: {Node(1): Node(2), Node(3): Node(4)}
  Output: {1: 2, 3: 4}
## FunctionDef update_local(frame, name, value)
**update_local**: The function of update_local is to update the value of a local variable in a given frame.

**parameters**: The parameters of this Function.
· frame: The frame object where the local variable resides.
· name: The name of the local variable to be updated.
· value: The new value to be assigned to the local variable.

**Code Description**: The update_local function is designed to modify the value of a local variable within a specific frame. It takes three parameters: the frame object, the name of the local variable, and the new value to be assigned to that variable. The function first updates the local variable in the frame's f_locals dictionary. Then, it calls the PyFrame_LocalsToFast function from the ctypes.pythonapi module to ensure that the changes are reflected in the frame's fast locals array, which is used by the Python interpreter for efficient variable access.

In the context of its usage within the project, update_local is called by the tracer function in the FunModule class's forward method. The tracer function is responsible for modifying the local and global dictionaries of a frame to handle recursive calls of a wrapped function. Specifically, update_local is used to replace the current function in the frame's local variables with the original function when a recursive call is detected. This ensures that the recursive call invokes the unwrapped function rather than the bundled function, maintaining the correct function behavior.

**Note**: Points to note about the use of the code
- Ensure that the frame object passed to update_local is valid and corresponds to the correct execution context.
- Be cautious when modifying local variables in a frame, as it can affect the execution flow and state of the program.
- The ctypes module is used to interact with the Python C API, which may have implications for portability and compatibility across different Python versions and implementations.
## FunctionDef test(x)
**test**: The function of test is to concatenate the string " world" to the data attribute of the input object.

**parameters**: The parameters of this Function.
· x: An object that must have a data attribute containing a string.

**Code Description**: The test function takes a single parameter, x, which is expected to be an object with a data attribute. The function accesses the data attribute of the input object and concatenates the string " world" to it. The result of this concatenation is then returned as the output of the function.

**Note**: 
- Ensure that the input object x has a data attribute that is a string; otherwise, the function will raise an AttributeError or TypeError.
- This function does not perform any type checking or error handling, so it is crucial to pass an appropriate object to avoid runtime errors.

**Output Example**: 
If the input object x has a data attribute with the value "Hello", the function will return "Hello world".
