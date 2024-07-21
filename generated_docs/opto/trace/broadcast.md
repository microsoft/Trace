## FunctionDef apply_op(op, output)
**apply_op**: The function of apply_op is to perform a broadcasting operation that applies a given operator to a container of Nodes.

**parameters**:
- op (callable): The operator to be applied.
- output (Any): The container to be updated.
- *args (Any): The positional inputs of the operator.
- **kwargs (Any): The keyword inputs of the operator.

**Code Description**:
The apply_op function takes an operator (op), an output container, and positional and keyword inputs. It first combines the positional and keyword inputs into a single list called "inputs". It then checks if there are any containers in the inputs list. If there are no containers, indicating that all inputs are Nodes, the function simply applies the operator to the inputs and returns the result.

If there is at least one container in the inputs list, the function performs the broadcasting operation. It iterates over the output container and applies the operator recursively to each element of the output container, along with the corresponding elements from the positional and keyword inputs. The result of each recursive call is assigned back to the corresponding element in the output container.

The function handles different types of output containers:
- If the output is a list or tuple, the function checks that the output and inputs have the same length. It then applies the operator to each element of the output container, along with the corresponding elements from the positional and keyword inputs.
- If the output is a dictionary, the function iterates over the key-value pairs of the output and applies the operator to each value, along with the corresponding elements from the positional and keyword inputs.
- If the output is an instance of the NodeContainer class, the function iterates over the attributes of the output and applies the operator to each attribute, along with the corresponding elements from the positional and keyword inputs.

The apply_op function ensures that all inputs are either Nodes or have the same type as the output. It raises an assertion error if this condition is not met.

**Note**:
- The apply_op function relies on the NodeContainer class to identify containers of Nodes and apply the operator recursively to each attribute of the container.
- The function supports broadcasting operations on different types of output containers, including lists, tuples, dictionaries, and instances of the NodeContainer class.
- It is important to ensure that the inputs and output are compatible in terms of length and type to avoid errors during the broadcasting operation.

**Output Example**:
The updated output container after applying the operator to the inputs.
### FunctionDef admissible_type(x, base)
**admissible_type**: The function of admissible_type is to determine whether the type of an object is admissible for a given base type or if it is an instance of the Node class.

**parameters**:
- x: The object whose type needs to be checked.
- base: The base type against which the object's type is compared.

**Code Description**:
The admissible_type function takes two parameters, x and base, and returns a boolean value indicating whether the type of x is equal to the type of base or if x is an instance of the Node class.

The function first checks if the type of x is equal to the type of base using the "type" function. If the types are equal, it returns True.

If the types are not equal, the function uses the "isinstance" function to check if x is an instance of the Node class. If x is an instance of Node, it returns True. Otherwise, it returns False.

This function is useful when you want to check if an object's type is admissible for a specific base type or if it is an instance of a specific class.

**Note**:
- The function assumes that the Node class is defined and imported correctly.
- The function only checks for exact type equality, not inheritance relationships.

**Output Example**:
- admissible_type(5, int) returns True
- admissible_type("hello", str) returns True
- admissible_type(5, str) returns False
- admissible_type(Node(), Node) returns True
***
