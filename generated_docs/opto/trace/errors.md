## ClassDef ExecutionError
**ExecutionError**: The function of ExecutionError is to serve as a base class for handling execution errors in code tracing.

**attributes**: The attributes of this Class.
· exception_node: An instance of ExceptionNode that contains details about the exception.

**Code Description**: The ExecutionError class is designed to encapsulate errors that occur during the execution of code within a tracing context. It inherits from the built-in Exception class, providing additional context through the exception_node attribute.

- The `__init__` method initializes the ExecutionError instance with an ExceptionNode object, which contains detailed information about the exception, including the error message, inputs, and other metadata. The base Exception class is then initialized with the data from the exception_node.

- The `__str__` method provides a string representation of the ExecutionError, which includes the data from the exception_node. This makes it easier to understand the nature of the error when it is printed or logged.

In the project, ExecutionError is used in the following contexts:

1. **opto\trace\bundle.py/FunModule/fun**: Within the `fun` method, ExecutionError is raised when there is a SyntaxError, NameError, KeyError, or OSError during the execution of dynamically generated code. The ExceptionNode is created with details about the error and passed to ExecutionError, which is then raised to signal the issue.

2. **opto\trace\bundle.py/FunModule/wrap**: In the `wrap` method, ExecutionError is raised if the output of a function is an exception. An ExceptionNode is created with the exception details and passed to ExecutionError, which is then raised to indicate the error.

3. **opto\trace\nodes.py/ExceptionNode/__init__**: The ExceptionNode class's `__init__` method checks if the value is an instance of ExecutionError. If not, it formats the exception message accordingly. This ensures that ExecutionError instances are handled correctly within the ExceptionNode.

**Note**: When using ExecutionError, ensure that the exception_node provided contains all necessary information about the error, as this will be used to initialize the base Exception class and provide a meaningful error message.

**Output Example**: 
If an ExecutionError is raised due to a SyntaxError in the dynamically executed code, the string representation might look like:
```
ExecutionError: (SyntaxError) invalid syntax (<string>, line 1)
```
This output indicates that a SyntaxError occurred, providing the specific error message and location.
### FunctionDef __init__(self, exception_node)
**__init__**: The function of __init__ is to initialize an instance of the ExecutionError class with a given ExceptionNode.

**parameters**: The parameters of this Function.
· exception_node: An instance of ExceptionNode that contains the exception message and related data.

**Code Description**: The __init__ method of the ExecutionError class is responsible for initializing an instance of the class. It takes one parameter, exception_node, which is an instance of ExceptionNode. This ExceptionNode contains the exception message and related data.

Upon initialization, the method assigns the provided exception_node to the instance variable self.exception_node. It then calls the __init__ method of its superclass with the data retrieved from the exception_node. This is achieved by accessing the data attribute of the exception_node, which returns the internal data of the node. The superclass's __init__ method is thus provided with this data, ensuring that the ExecutionError instance is properly initialized with the relevant exception information.

The relationship with its callees in the project is as follows:
- The data method of the ExceptionNode class is called to retrieve the internal data of the node. This data is then passed to the superclass's __init__ method to complete the initialization process.

**Note**: It is important to ensure that the exception_node parameter is a valid instance of ExceptionNode, as the method relies on the data attribute of this object to function correctly. If the exception_node does not have the expected structure, the initialization process may fail.
***
### FunctionDef __str__(self)
**__str__**: The function of __str__ is to provide a string representation of the ExecutionError object, specifically detailing the error message associated with the exception node.

**parameters**: The parameters of this Function.
· self: Refers to the instance of the ExecutionError class.

**Code Description**: The __str__ method is designed to return a formatted string that represents the ExecutionError instance. It accesses the `exception_node` attribute of the ExecutionError object and retrieves its data using the `data` method. The `data` method, defined in the AbstractNode class, returns the internal data of the node, which in this context is the error message or relevant data associated with the exception. The __str__ method then formats this data into a string prefixed with "ExecutionError: ", providing a clear and concise description of the error for debugging and logging purposes.

**Note**: This method assumes that the `exception_node` attribute is properly initialized and contains a valid node object with accessible data. If the `exception_node` is not set or its data is not retrievable, this could lead to unexpected behavior or errors.

**Output Example**: A possible return value of the __str__ method could be:
```
ExecutionError: File not found
```
This output indicates that the error message stored in the `exception_node` is "File not found".
***
## ClassDef TraceMissingInputsError
**TraceMissingInputsError**: The TraceMissingInputsError class represents an exception that is raised when not all nodes used in the operator function are specified as inputs of the returned node.

**Attributes**:
- message: A string representing the error message.

**Code Description**:
The TraceMissingInputsError class is a subclass of the built-in Exception class. It is used to handle the case where not all nodes used in the operator function are specified as inputs of the returned node. 

The class has an `__init__` method that takes a `message` parameter and initializes the `message` attribute with the provided message. It also calls the `__init__` method of the parent Exception class with the message.

The class also overrides the `__str__` method to return the error message when the exception is converted to a string.

This exception is raised in the `forward` method of the `FunModule` class in the `opto.trace.bundle` module. The `forward` method is responsible for executing the operator function and handling any exceptions that occur during execution. If the `catch_execution_error` flag is set to `True`, the exception is caught and stored in the `outputs` variable. Otherwise, the exception is raised and propagated.

**Note**: 
- This exception is raised when not all nodes used in the operator function are specified as inputs of the returned node.
- The error message can be accessed through the `message` attribute of the exception object.

**Output Example**:
```
TraceMissingInputsError: Not all nodes used in the operator <function fun at 0x00000123456789> are specified as inputs of the returned node. Missing ['node_x']
```
### FunctionDef __init__(self, message)
**__init__**: The function of __init__ is to initialize an instance of the TraceMissingInputsError class with a specific error message.

**parameters**: The parameters of this Function.
· message: A string that contains the error message to be associated with the TraceMissingInputsError instance.

**Code Description**: The __init__ method is a constructor for the TraceMissingInputsError class. It takes a single parameter, `message`, which is a string representing the error message. Inside the method, the `message` parameter is assigned to the instance variable `self.message`. The constructor then calls the `__init__` method of its superclass using `super().__init__(self.message)`, passing the error message to the base class's constructor. This ensures that the error message is properly initialized and can be accessed through the standard exception handling mechanisms.

**Note**: 
- Ensure that the `message` parameter is a string to avoid type errors.
- This method is essential for setting up the error message that will be displayed when the TraceMissingInputsError is raised.
***
### FunctionDef __str__(self)
**__str__**: The function of __str__ is to return the error message associated with the TraceMissingInputsError instance.

**parameters**: The parameters of this Function.
· None: This method does not take any parameters.

**Code Description**: The __str__ method in the TraceMissingInputsError class is designed to provide a human-readable representation of the error. When this method is called, it returns the value of the `message` attribute of the instance. This attribute typically contains a descriptive error message that explains the nature of the TraceMissingInputsError. The method ensures that when the error is printed or converted to a string, the message is displayed, making it easier for developers to understand the issue.

**Note**: 
- This method overrides the default __str__ method provided by Python's base Exception class.
- Ensure that the `message` attribute is properly set when initializing the TraceMissingInputsError instance to provide meaningful error information.

**Output Example**: 
If the `message` attribute of the TraceMissingInputsError instance is set to "Input data is missing", calling the __str__ method will return:
```
"Input data is missing"
```
***
