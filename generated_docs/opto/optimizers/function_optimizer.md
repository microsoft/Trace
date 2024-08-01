## FunctionDef get_fun_name(node)
**get_fun_name**: The function of get_fun_name is to retrieve the name of a MessageNode object.

**parameters**:
- node: A MessageNode object.

**Code Description**:
The `get_fun_name` function is used to retrieve the name of a `MessageNode` object. It takes a `node` parameter, which is an instance of the `MessageNode` class.

The function first checks if the `info` attribute of the `node` object is a dictionary and if it contains the key "fun_name". If this condition is true, the function returns the value associated with that key.

If the condition is false, the function splits the `name` attribute of the `node` object using the ":" delimiter. It then returns the first part of the split.

The purpose of this function is to provide a convenient way to retrieve the name of a `MessageNode` object. The name can be used for various purposes, such as identifying the node in a graph or generating function calls.

This function is called by the `repr_function_call` function in the `function_optimizer.py` file of the `optimizers` module. It is used to retrieve the name of a `MessageNode` object and include it in a function call representation.

**Note**:
- The `get_fun_name` function assumes that the `node` object is an instance of the `MessageNode` class.
- The function relies on the `info` and `name` attributes of the `node` object to retrieve the name.

**Output Example**:
If the `info` attribute of the `node` object is a dictionary with the key "fun_name" and the associated value is "my_function", calling `get_fun_name(node)` will return "my_function".

## FunctionDef repr_function_call(child)
**repr_function_call**: The function of repr_function_call is to generate a string representation of a function call based on a MessageNode object.

**parameters**:
- child: A MessageNode object.

**Code Description**:
The `repr_function_call` function takes a `child` parameter, which is an instance of the `MessageNode` class. It generates a string representation of a function call based on the attributes of the `child` object.

The function first initializes the `function_call` variable with the format "{child.py_name} = {get_fun_name(child)}(". This sets the initial part of the function call string, which includes the name of the variable assigned to the function call and the name of the function itself.

Next, the function iterates over the `inputs` attribute of the `child` object, which is a dictionary containing the input nodes of the `MessageNode` object. For each key-value pair in the dictionary, the function appends "{k}={v.py_name}, " to the `function_call` string. This adds the input variable names and their corresponding values to the function call string.

After the loop, the function removes the trailing ", " from the `function_call` string and adds a closing parenthesis. This completes the function call string.

Finally, the function returns the `function_call` string.

The purpose of this function is to provide a convenient way to generate a string representation of a function call based on a `MessageNode` object. The function call string can be used for various purposes, such as logging, debugging, or generating code.

This function is called by the `node_to_function_feedback` function in the `function_optimizer.py` file of the `optimizers` module. It is used to generate the function call representation of a `MessageNode` object and include it in the `graph` list of the `FunctionFeedback` object.

**Note**:
- The `repr_function_call` function assumes that the `child` object is an instance of the `MessageNode` class.
- The function relies on the `py_name` attribute of the input nodes to retrieve their variable names.
- The function relies on the `get_fun_name` function to retrieve the name of the `child` object.

**Output Example**:
If the `child` object has the following attributes:
- `py_name`: "result"
- `inputs`: {"x": <Node object at 0x12345678>, "y": <Node object at 0x23456789>}

Calling `repr_function_call(child)` will return the following string:
"result = my_function(x=node_x, y=node_y)"
## FunctionDef node_to_function_feedback(node_feedback)
**node_to_function_feedback**: The function of node_to_function_feedback is to convert a TraceGraph object into a FunctionFeedback object. It processes the nodes in the TraceGraph, categorizes them into roots, intermediates, and outputs, and populates the corresponding attributes of the FunctionFeedback object.

**parameters**:
- node_feedback: A TraceGraph object representing the subgraph of nodes.

**Code Description**:
The `node_to_function_feedback` function takes a `node_feedback` parameter, which is an instance of the `TraceGraph` class. It converts the `TraceGraph` object into a `FunctionFeedback` object by processing the nodes in the graph and organizing them into different categories.

The function first initializes the `depth` variable based on the length of the `graph` attribute of the `node_feedback` object. If the `graph` attribute is empty, the depth is set to 0; otherwise, it is set to the last element's depth in the `graph` attribute.

Next, the function initializes empty lists and dictionaries for `graph`, `others`, `roots`, `output`, and `documentation`. These variables will store the processed data and information.

The function then creates a `visited` set to keep track of visited nodes. It iterates over the `graph` attribute of the `node_feedback` object, which contains tuples representing the level and node of the graph. For each level and node, it checks if the node is a root node by checking the `is_root` attribute. If it is a root node, it updates the `roots` dictionary with the node's name as the key and its data and constraint as the value.

If the node is not a root node, it checks if all of its parents have been visited. If they have, it categorizes the node as an intermediate node. It updates the `documentation` dictionary with the node's name as the key and its description as the value. It appends a tuple representing the level and a string representation of the function call to the `graph` list. If the level is equal to the depth, it updates the `output` dictionary with the node's name as the key and its data and constraint as the value. Otherwise, it updates the `others` dictionary with the node's name as the key and its data and constraint as the value.

If the node is not an intermediate node, it categorizes it as a blanket node and adds it to the `roots` dictionary.

Finally, the function returns a `FunctionFeedback` object with the populated `graph`, `others`, `roots`, `output`, `user_feedback`, and `documentation` attributes.

**Note**:
- The `node_to_function_feedback` function assumes that the `node_feedback` parameter is a valid instance of the `TraceGraph` class.
- The function relies on the attributes and methods of the `TraceGraph` class to process the nodes and extract the necessary information.
- The resulting `FunctionFeedback` object represents the converted feedback from the `TraceGraph` object.

**Output Example**:
A possible return value of the `node_to_function_feedback` function could be a `FunctionFeedback` object with the following attributes:
- `graph`: [(0, "function_call_1"), (1, "function_call_2"), ...]
- `others`: {"node_name_1": (data_1, constraint_1), "node_name_2": (data_2, constraint_2), ...}
- `roots`: {"root_name_1": (data_1, constraint_1), "root_name_2": (data_2, constraint_2), ...}
- `output`: {"output_name_1": (data_1, constraint_1), "output_name_2": (data_2, constraint_2), ...}
- `user_feedback`: "User feedback string"
- `documentation`: {"node_name_1": "Node description 1", "node_name_2": "Node description 2", ...}
## ClassDef FunctionFeedback
**FunctionFeedback**: The function of FunctionFeedback is to serve as a feedback container used by the FunctionPropagator.

**attributes**: The attributes of this Class.
· graph: Each item is a representation of a function call. The items are topologically sorted.
· documentation: Function name and its documentation string.
· others: Intermediate variable names and their data.
· roots: Root variable name and its data.
· output: Leaf variable name and its data.
· user_feedback: User feedback at the leaf of the graph.

**Code Description**: The FunctionFeedback class is designed to encapsulate feedback information used by the FunctionPropagator. It organizes and stores various types of data related to function calls and their execution within a graph structure. The attributes of this class are as follows:

- `graph`: This attribute holds a list of tuples, where each tuple represents a function call. The tuples are topologically sorted, ensuring that the order of function calls respects their dependencies.
- `documentation`: This dictionary maps function names to their corresponding documentation strings, providing a reference for understanding the purpose and behavior of each function.
- `others`: This dictionary stores intermediate variable names along with their associated data. These variables are neither root nor leaf nodes in the function call graph.
- `roots`: This dictionary contains root variable names and their data. Root variables are the starting points in the function call graph.
- `output`: This dictionary holds leaf variable names and their data. Leaf variables are the endpoints in the function call graph.
- `user_feedback`: This string captures user feedback at the leaf of the graph, providing insights or comments from the user regarding the final output.

The FunctionFeedback class is utilized by the `node_to_function_feedback` function, which converts a TraceGraph into a FunctionFeedback instance. This conversion involves processing the nodes of the TraceGraph, categorizing them into roots, intermediates (others), and outputs, and then populating the corresponding attributes of the FunctionFeedback instance. The `node_to_function_feedback` function ensures that the graph is correctly sorted and that all relevant data and documentation are accurately captured.

**Note**: Points to note about the use of the code
- Ensure that the input TraceGraph to the `node_to_function_feedback` function is correctly structured and sorted.
- The FunctionFeedback class relies on the accurate categorization of nodes into roots, intermediates, and outputs for proper functionality.
- User feedback should be meaningful and relevant to the final output to provide valuable insights.
## ClassDef ProblemInstance
**ProblemInstance**: The function of ProblemInstance is to encapsulate and format the details of a problem instance for optimization tasks.

**attributes**: The attributes of this Class.
· instruction: A string containing the instructions for the problem.
· code: A string representing the code to be executed.
· documentation: A string providing documentation for the code.
· variables: A string listing the variables involved in the problem.
· inputs: A string detailing the inputs required for the code.
· others: A string for any additional information related to the problem.
· outputs: A string specifying the expected outputs of the code.
· feedback: A string containing feedback on the problem instance.
· constraints: A string outlining any constraints on the variables or the problem.

**Code Description**: The ProblemInstance class is designed to encapsulate various components of a problem instance, such as instructions, code, documentation, variables, inputs, outputs, feedback, and constraints. It uses a predefined template to format these components into a structured string representation.

The class includes a `problem_template` attribute, which is a formatted string template that organizes the problem details into sections. The `__repr__` method is overridden to return a formatted string representation of the problem instance using this template.

The ProblemInstance class is utilized in the FunctionOptimizer class, specifically in its `__init__` and `probelm_instance` methods. In the `__init__` method, an example problem instance is created using the ProblemInstance class to demonstrate the expected format and structure. The `probelm_instance` method generates a new ProblemInstance based on the provided summary and an optional mask to exclude certain sections.

**Note**: When using the ProblemInstance class, ensure that all attributes are properly populated to generate a meaningful and complete problem instance. The class relies on the provided template to format the output, so any missing or incorrect information may result in an incomplete or inaccurate representation.

**Output Example**: 
```
#Instruction
Optimize the function to achieve the desired output.

#Code
y = add(x=a,y=b)
z = subtract(x=y, y=c)

#Documentation
add: add x and y 
subtract: subtract y from x

#Variables
(int) a = 5

#Constraints
a: a > 0

#Inputs
(int) b = 1
(int) c = 5

#Others
(int) y = 6

#Outputs
(int) z = 1

#Feedback:
The result of the code is not as expected. The result should be 10, but the code returns 1
```
### FunctionDef __repr__(self)
**__repr__**: The function of __repr__ is to provide a formatted string representation of the ProblemInstance object.

**parameters**: The parameters of this function.
· self: Refers to the instance of the ProblemInstance class.

**Code Description**: The __repr__ function returns a string that represents the ProblemInstance object in a human-readable format. It uses the problem_template attribute of the instance to format the string. The placeholders in the problem_template are filled with the corresponding attributes of the instance, which include:
- instruction: Instructions related to the problem instance.
- code: The code associated with the problem instance.
- documentation: Documentation details of the problem instance.
- variables: Variables involved in the problem instance.
- constraints: Constraints applied to the problem instance.
- inputs: Inputs required for the problem instance.
- outputs: Outputs expected from the problem instance.
- others: Any other relevant information about the problem instance.
- feedback: Feedback related to the problem instance.

**Note**: Ensure that the problem_template attribute is properly defined and contains the necessary placeholders for all the attributes used in the format method. If any attribute is missing or the template is incorrectly formatted, it may result in a runtime error.

**Output Example**: A possible appearance of the code's return value could be:
```
ProblemInstance(
    instruction='Optimize the function',
    code='def optimize(): pass',
    documentation='This function optimizes the given parameters.',
    variables={'x': 10, 'y': 20},
    constraints='x + y <= 30',
    inputs=['x', 'y'],
    outputs=['result'],
    others='Additional information',
    feedback='No issues found'
)
```
***
## ClassDef FunctionOptimizer
**FunctionOptimizer**: The function of FunctionOptimizer is to serve as a base class for optimizers, responsible for updating parameters based on feedback.

**attributes**:
- parameters: A list of ParameterNode objects that the optimizer will manage and update.

**Code Description**:
The FunctionOptimizer class is a subclass of the Optimizer class and provides a base implementation for optimizing functions. It extends the Optimizer class and overrides some of its methods to customize the optimization process.

The `__init__` method initializes the FunctionOptimizer object by calling the superclass's `__init__` method and passing the parameters list. It also sets the `representation_prompt` attribute, which is a generic representation prompt explaining how to read and understand the problem.

The `default_objective` attribute defines the default objective of the optimizer, which is to change the values of the variables in the `#Variables` section to improve the output according to the feedback.

The `output_format_prompt` attribute defines the output format of the optimizer's response. It specifies that the output should be in JSON format and provides a template for the structure of the response.

The `example_problem_template` attribute defines a template for an example problem instance and response. It includes placeholders for the problem instance and the response, which can be filled in with actual values.

The `user_prompt_template` attribute defines a template for the user prompt. It includes placeholders for the problem instance and the instruction, which can be filled in with actual values.

The `example_prompt` attribute is currently empty and marked as a TODO. It is intended to provide feasible but not optimal solutions for the current problem instance as a hint to help users understand the problem better.

The `final_prompt` attribute defines a template for the final prompt, which prompts the user to provide their response.

The `__init__` method also initializes other attributes such as `propagator`, `llm`, `ignore_extraction_error`, `include_example`, `max_tokens`, and `log` with default values or values passed as arguments.

The `default_propagator` method returns the default Propagator object of the optimizer. This method is implemented in the Optimizer class and must be overridden by subclasses.

The `summarize` method aggregates the feedback from all the parameters and constructs the summary object. It then classifies the root nodes into variables and others.

The `repr_node_value` method takes a dictionary of node values and returns a string representation of the values.

The `repr_node_constraint` method takes a dictionary of node constraints and returns a string representation of the constraints.

The `probelm_instance` method constructs a ProblemInstance object based on the summary and a mask. The mask is used to exclude certain sections from the problem instance.

The `construct_prompt` method constructs the system and user prompts based on the summary and a mask. The system prompt includes the representation prompt and the output format prompt. The user prompt includes the problem instance and the final prompt.

The `_step` method is an abstract method that must be implemented by subclasses. It is responsible for proposing new parameter values based on feedback and returning the update dictionary.

The `construct_update_dict` method converts the suggestion in text format into the right data type and constructs an update dictionary.

The `extract_llm_suggestion` method extracts the suggestion from the response received from the LLM (Language Model).

The `call_llm` method calls the LLM with a prompt and returns the response.

**Note**:
- The FunctionOptimizer class is designed to be subclassed and extended to create specific optimizers for different types of problems.
- Subclasses of FunctionOptimizer must implement the `_step` and `default_propagator` methods.
- The FunctionOptimizer class provides a consistent interface and behavior for managing and updating parameters based on feedback.
- The class uses the LLM to generate suggestions for updating the parameters.
- The class includes methods for constructing prompts, extracting suggestions, and calling the LLM.

**Output Example**:
{
    "reasoning": "In this case, the desired response would be to change the value of input a to 14, as that would make the code return 10.",
    "answer": {},
    "suggestion": {
        "a": 10
    }
}
### FunctionDef __init__(self, parameters, config_list)
**__init__**: The function of __init__ is to initialize an instance of the FunctionOptimizer class.

**parameters**:
- parameters: A list of ParameterNode objects representing the trainable nodes in the computational graph.
- config_list: A list of configurations for the OpenAIWrapper. Default is None.
- *args: Additional positional arguments.
- propagator: An instance of the Propagator class. Default is None.
- objective: A string representing the objective of the optimization task. Default is None.
- ignore_extraction_error: A boolean indicating whether to ignore type conversion errors when extracting updated values from LLM's suggestion. Default is True.
- include_example: A boolean indicating whether to include an example problem and response in the prompt. Default is False.
- max_tokens: An integer representing the maximum number of tokens allowed in the prompt. Default is 4096.
- log: A boolean indicating whether to log the optimization process. Default is True.
- **kwargs: Additional keyword arguments.

**Code Description**: The __init__ method of the FunctionOptimizer class initializes an instance of the class. It takes in various parameters such as parameters, config_list, *args, propagator, objective, ignore_extraction_error, include_example, max_tokens, log, and **kwargs.

The method first calls the __init__ method of the superclass (Optimizer) to initialize the parameters and propagator attributes. It then sets the ignore_extraction_error attribute based on the provided ignore_extraction_error parameter.

If the config_list parameter is None, it uses the autogen.config_list_from_json function to retrieve the configuration list from the "OAI_CONFIG_LIST" JSON file. It then initializes the llm attribute with an instance of the autogen.OpenAIWrapper class, passing the config_list as a parameter.

The objective attribute is set to the provided objective parameter if it is not None, otherwise it is set to the default_objective attribute of the class.

The example_problem attribute is initialized with a formatted string template that represents an example problem instance. It includes placeholders for the instruction, code, documentation, variables, constraints, inputs, others, outputs, and feedback sections.

The example_response attribute is initialized with a formatted string that represents an example response to the problem instance. It includes placeholders for the reasoning, answer, and suggestion sections.

The include_example, max_tokens, and log attributes are set based on the provided parameters.

**Note**: 
- The FunctionOptimizer class is a subclass of the Optimizer class.
- The parameters attribute represents the trainable nodes in the computational graph.
- The config_list attribute represents the configuration list for the OpenAIWrapper.
- The propagator attribute represents the propagator for the optimization process.
- The objective attribute represents the objective of the optimization task.
- The ignore_extraction_error attribute indicates whether to ignore type conversion errors when extracting updated values from LLM's suggestion.
- The include_example attribute indicates whether to include an example problem and response in the prompt.
- The max_tokens attribute represents the maximum number of tokens allowed in the prompt.
- The log attribute indicates whether to log the optimization process.

**Output Example**: 
```
FunctionOptimizer(
    parameters=[ParameterNode: (name, dtype=<class 'type'>, data=value)],
    config_list=[...],
    propagator=Propagator(),
    objective="...",
    ignore_extraction_error=True,
    include_example=False,
    max_tokens=4096,
    log=True,
    ...
)
```
***
### FunctionDef default_propagator(self)
**default_propagator**: The function of default_propagator is to return the default Propagator object of the optimizer.

**parameters**: The parameters of this Function.
· None

**Code Description**: The default_propagator function is a method within the FunctionOptimizer class. Its primary purpose is to return an instance of the GraphPropagator class. When this method is called, it creates and returns a new GraphPropagator object. The GraphPropagator class, which is a subclass of the Propagator class, is designed to collect all the nodes seen in a path and compute the propagated feedback to the parent nodes based on the child node's description, data, and feedback. This method does not take any parameters and simply returns a new GraphPropagator instance, which can then be used by the optimizer for its propagation tasks.

**Note**: This method is straightforward and does not require any parameters. It is designed to provide a default propagator for the optimizer, ensuring that the optimizer has a predefined mechanism for handling propagation tasks.

**Output Example**: 
```python
GraphPropagator()
```
***
### FunctionDef summarize(self)
**summarize**: The function of summarize is to aggregate feedback from all the parameters, construct variables and update others, and classify the root nodes into variables and others.

**parameters**:
- self: The instance of the class.

**Code Description**:
The `summarize` function is a method of the `FunctionOptimizer` class. It aggregates feedback from all the parameters by calling the `aggregate` method of the `propagator` object. The feedbacks are obtained from the trainable parameters by iterating over the `parameters` attribute of the class instance and filtering out the non-trainable nodes. The feedbacks are then summed up using the `sum` function.

After aggregating the feedback, the function converts the resulting `TraceGraph` object into a `FunctionFeedback` object by calling the `node_to_function_feedback` function. This function processes the nodes in the `TraceGraph` object, categorizes them into roots, intermediates, and outputs, and populates the corresponding attributes of the `FunctionFeedback` object.

Next, the function constructs variables and updates others based on the trainable nodes. It creates a dictionary called `trainable_param_dict` that maps the parameter names to their corresponding parameter objects. It then updates the `variables` attribute of the `summary` object by filtering the `roots` dictionary based on the keys present in the `trainable_param_dict`. Similarly, it updates the `inputs` attribute of the `summary` object by filtering the `roots` dictionary based on the keys not present in the `trainable_param_dict`.

Finally, the function returns the `summary` object, which represents the aggregated feedback, variables, and inputs.

The `summarize` function is called in the `_step` method of the `FunctionOptimizer` class. It is used to summarize the feedback from the trainable parameters and construct prompts for further processing. The `summarize` function relies on the `propagator` object and the `node_to_function_feedback` function to perform its tasks.

**Note**:
- The `summarize` function assumes that the `propagator` object is correctly initialized and contains the necessary methods and attributes.
- The function assumes that the `parameters` attribute of the class instance contains the necessary trainable nodes.
- The `node_to_function_feedback` function should be defined and accessible within the project for the `summarize` function to work correctly.
- The resulting `summary` object represents the aggregated feedback, variables, and inputs from the trainable parameters.

**Output Example**:
A possible return value of the `summarize` function could be a `FunctionFeedback` object with the following attributes:
- `graph`: [(0, "function_call_1"), (1, "function_call_2"), ...]
- `others`: {"node_name_1": (data_1, constraint_1), "node_name_2": (data_2, constraint_2), ...}
- `roots`: {"root_name_1": (data_1, constraint_1), "root_name_2": (data_2, constraint_2), ...}
- `output`: {"output_name_1": (data_1, constraint_1), "output_name_2": (data_2, constraint_2), ...}
- `user_feedback`: "User feedback string"
- `documentation`: {"node_name_1": "Node description 1", "node_name_2": "Node description 2", ...}
***
### FunctionDef repr_node_value(node_dict)
**repr_node_value**: The function of repr_node_value is to generate a formatted string representation of the values in a given dictionary, excluding keys that contain the substring "__code".

**parameters**: The parameters of this Function.
· node_dict: A dictionary where each key is a string and each value is a list, with the first element of the list being the value to be represented.

**Code Description**: The repr_node_value function processes a dictionary (node_dict) and creates a list of formatted strings based on the dictionary's contents. It iterates over each key-value pair in the dictionary. For each pair, if the key does not contain the substring "__code", it appends a string to the list in the format "(type) key=value", where "type" is the type of the first element in the value list, and "key" and "value" are the key and the first element of the value list, respectively. If the key contains the substring "__code", it appends a string in the format "(code) key:value". Finally, the function joins all the strings in the list with newline characters and returns the resulting string.

This function is utilized in the probelm_instance method of the FunctionOptimizer class. In this context, repr_node_value is called to generate string representations of various components of a summary object, such as variables, inputs, outputs, and others. These string representations are then used to construct a ProblemInstance object, which encapsulates the details of a problem instance in a structured format.

**Note**: 
- Ensure that the input dictionary (node_dict) has lists as values, with the first element of each list being the value to be represented.
- Keys containing the substring "__code" will be treated differently and formatted as "(code) key:value".

**Output Example**: 
Given the input dictionary:
{
    "var1": [10],
    "var2": ["example"],
    "func__code": ["def func(): pass"]
}
The function would return:
```
(int) var1=10
(str) var2=example
(code) func__code:def func(): pass
```
***
### FunctionDef repr_node_constraint(node_dict)
**repr_node_constraint**: The function of repr_node_constraint is to generate a formatted string representation of the constraints in a given node dictionary.

**parameters**: The parameters of this Function.
· node_dict: A dictionary where keys are node identifiers and values are tuples containing node attributes.

**Code Description**: The repr_node_constraint function processes a dictionary of nodes, where each key-value pair represents a node and its attributes. The function iterates through each item in the dictionary. For each key-value pair, it checks if the key does not contain the substring "__code". If this condition is met and the second element of the value tuple (v[1]) is not None, it appends a formatted string to a temporary list (temp_list). The formatted string includes the type of the first element of the value tuple (v[0]), the key, and the second element of the value tuple (v[1]). If the key contains the substring "__code" and the second element of the value tuple (v[1]) is not None, it appends a different formatted string to the temporary list, indicating that the key is related to code. Finally, the function joins all the strings in the temporary list with newline characters and returns the resulting string.

This function is called by the probelm_instance method of the FunctionOptimizer class. In this context, repr_node_constraint is used to generate a string representation of the constraints in the summary.variables dictionary, which is then included in the ProblemInstance object. This ensures that the constraints are properly formatted and included in the problem instance's representation.

**Note**: Ensure that the node_dict parameter is correctly structured, with each value being a tuple where the second element can be None or a meaningful value to be included in the output.

**Output Example**: 
```
(int) node1: 10
(str) node2: constraint_value
(code) node3__code: some_code
```
***
### FunctionDef probelm_instance(self, summary, mask)
**probelm_instance**: The function of probelm_instance is to generate a ProblemInstance object based on the provided summary and an optional mask. It encapsulates and formats the details of a problem instance for optimization tasks.

**parameters**:
- summary: A summary object containing the necessary information for the problem instance.
- mask (optional): A list of strings specifying the sections to exclude from the ProblemInstance object.

**Code Description**: The probelm_instance function takes a summary object and an optional mask as input. It first checks if a mask is provided, and if not, initializes it as an empty list. 

The function then creates a ProblemInstance object by passing the following parameters:
- instruction: The instruction for the problem instance, obtained from the summary object.
- code: A string representing the code to be executed. It is obtained by joining the values of the sorted summary.graph dictionary, excluding the sections specified in the mask.
- documentation: A string providing documentation for the code. It is obtained by joining the values of the summary.documentation dictionary, excluding the sections specified in the mask.
- variables: A string listing the variables involved in the problem. It is obtained by calling the repr_node_value function on the summary.variables dictionary, excluding the sections specified in the mask.
- constraints: A string outlining any constraints on the variables or the problem. It is obtained by calling the repr_node_constraint function on the summary.variables dictionary, excluding the sections specified in the mask.
- inputs: A string detailing the inputs required for the code. It is obtained by calling the repr_node_value function on the summary.inputs dictionary, excluding the sections specified in the mask.
- outputs: A string specifying the expected outputs of the code. It is obtained by calling the repr_node_value function on the summary.output dictionary, excluding the sections specified in the mask.
- others: A string for any additional information related to the problem. It is obtained by calling the repr_node_value function on the summary.others dictionary, excluding the sections specified in the mask.
- feedback: A string containing feedback on the problem instance. It is obtained from the summary.user_feedback attribute, excluding the sections specified in the mask.

The ProblemInstance object is then returned.

The probelm_instance function is utilized in the FunctionOptimizer class, specifically in its __init__ method and construct_prompt method. In the __init__ method, it is used to create an example problem instance using the ProblemInstance class. In the construct_prompt method, it is called to generate the problem instance string representation, which is included in the user prompt.

**Note**: When using the probelm_instance function, ensure that the summary object is properly populated with the required information. The mask parameter can be used to exclude specific sections from the generated ProblemInstance object.

**Output Example**:
```
#Instruction
Optimize the function to achieve the desired output.

#Code
y = add(x=a,y=b)
z = subtract(x=y, y=c)

#Documentation
add: add x and y 
subtract: subtract y from x

#Variables
(int) a = 5

#Constraints
a: a > 0

#Inputs
(int) b = 1
(int) c = 5

#Others
(int) y = 6

#Outputs
(int) z = 1

#Feedback:
The result of the code is not as expected. The result should be 10, but the code returns 1
```
***
### FunctionDef construct_prompt(self, summary, mask)
**construct_prompt**: The function of construct_prompt is to construct the system and user prompts based on the provided summary and optional mask.

**parameters**:
- summary: A summary object containing the necessary information for the problem instance.
- mask (optional): A list of strings specifying the sections to exclude from the ProblemInstance object.
- *args: Additional positional arguments.
- **kwargs: Additional keyword arguments.

**Code Description**: The construct_prompt function is designed to generate system and user prompts for optimization tasks. It begins by creating a system prompt by concatenating the representation_prompt and output_format_prompt attributes, which provide a generic representation and output rules.

Next, the function constructs a user prompt using the user_prompt_template attribute. It formats this template with a string representation of a problem instance, generated by calling the probelm_instance method with the provided summary and mask. This problem instance encapsulates and formats the details of the problem for the user prompt.

If the include_example attribute is set to True, the function prepends an example problem and response to the user prompt. This is done by formatting the example_problem_template attribute with the example_problem and example_response attributes.

Finally, the function appends the final_prompt attribute to the user prompt and returns both the system prompt and the user prompt.

The construct_prompt function is called within the _step method of the FunctionOptimizer class. In this context, it is used to generate the necessary prompts for interacting with a language model, which then provides suggestions for optimizing the function.

**Note**: Ensure that the summary object is properly populated with the required information before calling construct_prompt. The mask parameter can be used to exclude specific sections from the generated ProblemInstance object.

**Output Example**:
```
system_prompt: "Generic representation and output rules"
user_prompt: "Example problem and response (if include_example is True) + Problem instance details + Final prompt"
```
***
### FunctionDef _step(self, verbose, mask)
**_step**: The `_step` function is responsible for executing a single optimization step in the `FunctionOptimizer` class. It performs various operations such as summarizing feedback, constructing prompts, calling the language model, extracting suggestions, constructing an update dictionary, and logging the interaction.

**parameters**:
- `self`: The instance of the `FunctionOptimizer` class.
- `verbose` (optional): A boolean indicating whether to print verbose output. Default is `False`.
- `mask` (optional): A list of strings specifying sections to exclude from the problem instance. Default is `None`.
- `*args`: Additional positional arguments.
- `**kwargs`: Additional keyword arguments.

**Code Description**:
The `_step` function begins by asserting that the `propagator` attribute of the `FunctionOptimizer` instance is an instance of the `GraphPropagator` class. This ensures that the necessary methods and attributes are available for the subsequent operations.

Next, the function calls the `summarize` method of the `FunctionOptimizer` class to aggregate feedback from all the parameters. This is done by invoking the `summarize` function defined in the `function_optimizer.py` file. The `summarize` function aggregates feedback by calling the `aggregate` method of the `propagator` object and processes the resulting `TraceGraph` object.

After summarizing the feedback, the function constructs system and user prompts by calling the `construct_prompt` method of the `FunctionOptimizer` class. This method formats the prompts using the `representation_prompt`, `output_format_prompt`, and `user_prompt_template` attributes of the class. It also generates a problem instance string by calling the `problem_instance` method with the provided summary and mask. The prompts are then concatenated and stored in the `system_prompt` and `user_prompt` variables.

The function proceeds to call the `call_llm` method of the `FunctionOptimizer` class to interact with a language model. This method sends the system and user prompts to the language model and retrieves the generated response. The response is stored in the `response` variable.

If the response contains the string "TERMINATE", the function returns an empty dictionary.

Otherwise, the function calls the `extract_llm_suggestion` method of the `FunctionOptimizer` class to extract a suggestion dictionary from the response. This method attempts to parse the response as JSON and retrieve the "suggestion" key. If the parsing fails, it falls back to extracting key-value pairs using regular expressions. The extracted suggestion dictionary is stored in the `suggestion` variable.

The function then calls the `construct_update_dict` method of the `FunctionOptimizer` class to convert the suggestion into the appropriate data types. This method iterates over the parameters of the optimizer and checks if each parameter is trainable and if its name exists in the suggestion dictionary. If both conditions are met, it attempts to convert the suggestion value to the data type of the parameter using the `type` function. The parameter and its updated value are added to the `update_dict` dictionary.

If the `log` attribute of the optimizer is not `None`, the function appends a dictionary containing the system prompt, user prompt, and response to the log.

Finally, the function returns the `update_dict` dictionary, which maps `ParameterNode` objects to their corresponding updated values.

The `_step` function is an essential part of the optimization process in the `FunctionOptimizer` class. It relies on the `summarize`, `construct_prompt`, `call_llm`, `extract_llm_suggestion`, and `construct_update_dict` methods to perform its tasks. The function assumes that the necessary methods and attributes are correctly initialized and accessible within the class.

**Note**:
- The `summarize` function assumes that the `propagator` object is correctly initialized and contains the necessary methods and attributes.
- The `summarize` function assumes that the `parameters` attribute of the class instance contains the necessary trainable nodes.
- The `node_to_function_feedback` function should be defined and accessible within the project for the `summarize` function to work correctly.
- The resulting `summary` object represents the aggregated feedback, variables, and inputs from the trainable parameters.
- The `construct_prompt` function assumes that the summary object is properly populated with the required information before calling it.
- The `construct_prompt` function assumes that the `representation_prompt`, `output_format_prompt`, `user_prompt_template`, `example_problem_template`, `example_problem`, `example_response`, and `final_prompt` attributes are correctly initialized within the class.
- The `call_llm` function assumes that the `llm` object is correctly initialized and contains the necessary methods and attributes.
- The `extract_llm_suggestion` function assumes that the response string contains a "suggestion" key within a JSON object.
- The `construct_update_dict` function assumes that the `parameters` attribute exists and is a list of `ParameterNode` objects.
- The `construct_update_dict` function assumes that the suggestion dictionary contains the keys corresponding to the `py_name` attribute of the `ParameterNode` objects.
- If the suggestion is missing a key or the conversion fails, an exception is raised unless the `ignore_extraction_error` flag is set to `True`.
- The `_step` function assumes that the necessary methods and attributes are correctly initialized within the class.

**Output Example**:
A possible return value of the `_step` function could be a dictionary mapping `ParameterNode` objects to their corresponding updated values:
```
{
    <ParameterNode object>: <updated value>,
    <ParameterNode object>: <updated value>,
    ...
}
```
***
### FunctionDef construct_update_dict(self, suggestion)
**construct_update_dict**: The function of construct_update_dict is to convert the suggestion in text into the right data type.

**parameters**:
- suggestion: A dictionary containing suggestions in text form.
    - Type: Dict[str, Any]
- return: A dictionary mapping ParameterNode objects to their corresponding updated values.
    - Type: Dict[ParameterNode, Any]

**Code Description**:
The `construct_update_dict` function takes a suggestion in text form and converts it into the appropriate data type. It iterates over the `parameters` list of the current instance and checks if each parameter is trainable and if its name exists in the suggestion dictionary. If both conditions are met, it attempts to convert the suggestion value to the data type of the parameter using the `type` function. If the conversion is successful, the parameter and its updated value are added to the `update_dict` dictionary.

In case the suggestion is missing the key or the conversion fails due to an incorrect data type, an exception is raised. However, if the `ignore_extraction_error` flag is set to True, a warning is issued instead of raising an exception.

The `update_dict` dictionary, containing the ParameterNode objects and their updated values, is then returned as the output of the function.

This function is called by the `_step` method of the `FunctionOptimizer` class in the `function_optimizer.py` file. In the `_step` method, the `construct_update_dict` function is used to convert the suggestion obtained from the language model into the appropriate data types for updating the parameters of the optimizer.

**Note**:
- The `construct_update_dict` function assumes that the `parameters` attribute exists and is a list of ParameterNode objects.
- The `construct_update_dict` function assumes that the suggestion dictionary contains the keys corresponding to the `py_name` attribute of the ParameterNode objects.
- If the suggestion is missing a key or the conversion fails, an exception is raised unless the `ignore_extraction_error` flag is set to True.

**Output Example**:
A possible return value of the `construct_update_dict` function could be a dictionary mapping ParameterNode objects to their corresponding updated values. For example:
```
{
    <ParameterNode object>: <updated value>,
    <ParameterNode object>: <updated value>,
    ...
}
```
***
### FunctionDef extract_llm_suggestion(self, response)
**extract_llm_suggestion**: The function of extract_llm_suggestion is to extract a suggestion dictionary from a given response string.

**parameters**: The parameters of this Function.
· response: A string containing the response from which the suggestion needs to be extracted.

**Code Description**: The extract_llm_suggestion function is designed to parse a response string, typically from a language model, and extract a dictionary of suggestions. The function attempts to decode the response as JSON and retrieve the "suggestion" key. If the initial attempt fails due to a JSONDecodeError, the function tries to clean the response by extracting content within curly braces and attempts to decode it again. If the suggestion dictionary is still empty, the function uses a regular expression to manually extract key-value pairs from the response string.

The function is called by the _step method within the same class, FunctionOptimizer. In the _step method, the extract_llm_suggestion function is used to process the response from a language model call and extract meaningful suggestions, which are then used to construct an update dictionary. This update dictionary is crucial for the subsequent steps in the optimization process.

**Note**: 
- The function makes two attempts to decode the response as JSON before resorting to regular expression parsing.
- If the suggestion dictionary remains empty after all attempts, the function prints an error message indicating the failure to extract suggestions.
- The function assumes that the response string contains a "suggestion" key within a JSON object.

**Output Example**: 
If the response string is '{"suggestion": {"param1": "value1", "param2": "value2"}}', the function will return:
```
{
    "param1": "value1",
    "param2": "value2"
}
```
***
### FunctionDef call_llm(self, system_prompt, user_prompt, verbose, max_tokens)
**call_llm**: The function of call_llm is to interact with a language model (LLM) using provided prompts and return the generated response.

**parameters**: The parameters of this Function.
· system_prompt: A string representing the initial prompt given to the LLM, typically setting the context or instructions for the LLM.
· user_prompt: A string representing the user's input or query that follows the system prompt.
· verbose: A boolean or string parameter that controls the verbosity of the function. If set to True or "output", the prompts and responses are printed to the console.
· max_tokens: An integer specifying the maximum number of tokens the LLM should generate in its response. The default value is 4096.

**Code Description**: The call_llm function is designed to facilitate communication with a language model by sending it a structured prompt and retrieving its response. The function first checks the verbosity setting; if verbose is set to True or "output", it prints the combined system and user prompts. It then constructs a message list with roles "system" and "user" to format the prompts appropriately for the LLM.

The function attempts to generate a response from the LLM in JSON format. If this attempt fails, it falls back to a simpler response generation method, using the max_tokens parameter to limit the response length. The response content is extracted from the LLM's output and, if verbosity is enabled, printed to the console. Finally, the function returns the LLM's response content.

This function is called by the _step method within the same module. The _step method uses call_llm to generate suggestions or updates based on the current state summarized by the system and user prompts. The response from call_llm is then processed to extract actionable suggestions, which are used to update the system's state.

**Note**: 
- Ensure that the LLM instance (self.llm) is properly initialized before calling this function.
- The verbose parameter can be used to debug or log the interaction with the LLM by printing the prompts and responses.
- Handle exceptions appropriately when the LLM fails to generate a JSON response.

**Output Example**: 
A possible return value of the function might look like:
```
"Sure, I can help you with that. What specific information are you looking for?"
```
***
## ClassDef FunctionOptimizerV2
**FunctionOptimizerV2**: The function of FunctionOptimizerV2 is to serve as an enhanced version of the FunctionOptimizer class, providing additional functionality and improvements to the optimization process.

**attributes**:
- output_format_prompt: A string that defines the output format of the optimizer's response.
- example_problem_template: A string template for an example problem instance and response.
- user_prompt_template: A string template for the user prompt.
- example_prompt: A string that provides feasible but not optimal solutions for the current problem instance as a hint.
- final_prompt: A string template for the final prompt.

**Code Description**:
The FunctionOptimizerV2 class is a subclass of the FunctionOptimizer class and provides an enhanced version of the optimization process. It extends the FunctionOptimizer class and overrides some of its methods to add additional functionality.

The `__init__` method initializes the FunctionOptimizerV2 object by calling the superclass's `__init__` method and passing the arguments. It also initializes the `memory` attribute, which is a FIFOBuffer object used to store past variables and feedbacks.

The `construct_prompt` method overrides the superclass's method to add examples from the memory to the user prompt. It checks if the memory is not empty and adds the variables and feedbacks from the memory to the user prompt.

**Note**:
- The FunctionOptimizerV2 class is designed to enhance the optimization process by adding memory functionality.
- The class extends the FunctionOptimizer class and overrides some of its methods to add the desired functionality.
- The `memory` attribute stores past variables and feedbacks.
- The `construct_prompt` method adds examples from the memory to the user prompt.

**Output Example**:
{
    "reasoning": "In this case, the desired response would be to change the value of input a to 14, as that would make the code return 10.",
    "answer": {},
    "suggestion": {
        "a": 10
    }
}
## ClassDef FunctionOptimizerV2Memory
**FunctionOptimizerV2Memory**: The function of FunctionOptimizerV2Memory is to enhance the optimization process by incorporating a memory mechanism that stores past variables and feedbacks.

**attributes**: The attributes of this Class.
· memory: A FIFOBuffer object that stores past variables and feedbacks.

**Code Description**: The FunctionOptimizerV2Memory class extends the FunctionOptimizerV2 class by adding a memory mechanism to the optimization process. This class is designed to improve the optimization process by utilizing past experiences stored in memory.

The `__init__` method initializes the FunctionOptimizerV2Memory object. It calls the superclass's `__init__` method with the provided arguments and initializes the `memory` attribute as a FIFOBuffer object with a specified memory size.

The `construct_prompt` method constructs the system and user prompts by calling the superclass's `construct_prompt` method. It then checks if the memory contains any past variables and feedbacks. If the memory is not empty, it adds these examples to the user prompt. The method splits the user prompt at the final prompt, adds a section containing past variables and feedbacks, and then reconstructs the user prompt. Finally, it adds the current summary's variables and user feedback to the memory.

This class is used within the project to enhance the functionality of the FunctionOptimizerV2 by adding a memory component, which allows the optimizer to consider past experiences when constructing prompts.

**Note**:
- The memory attribute is a FIFOBuffer that stores past variables and feedbacks.
- The construct_prompt method enhances the user prompt by including examples from the memory.
- This class is designed to improve the optimization process by leveraging past experiences.

**Output Example**:
```json
{
    "system_prompt": "System prompt content here...",
    "user_prompt": "User prompt content here...\nBelow are some variables and their feedbacks you received in the past.\n\n{\n    \"variables\": {\n        \"var1\": \"value1\",\n        \"var2\": \"value2\"\n    },\n    \"feedback\": \"feedback content\"\n}\n\nFinal prompt content here..."
}
```
### FunctionDef __init__(self)
**__init__**: The function of __init__ is to initialize an instance of the FunctionOptimizerV2Memory class with optional memory size and other parameters.

**parameters**: The parameters of this Function.
· *args: Variable length argument list.
· memory_size: An optional integer parameter that specifies the size of the FIFO buffer. Default is 0.
· **kwargs: Arbitrary keyword arguments.

**Code Description**: The __init__ method is the constructor for the FunctionOptimizerV2Memory class. It begins by calling the constructor of its superclass using `super().__init__(*args, **kwargs)`, ensuring that any initialization logic in the parent class is executed. Following this, it initializes a FIFOBuffer instance with the specified memory size by passing the `memory_size` parameter to the FIFOBuffer constructor. The FIFOBuffer is assigned to the `self.memory` attribute of the FunctionOptimizerV2Memory instance.

The FIFOBuffer class, which is used here, manages a First-In-First-Out (FIFO) buffer of a specified size. This buffer is designed to store a limited number of items, automatically discarding the oldest items when new ones are added beyond its capacity. In the context of FunctionOptimizerV2Memory, the FIFOBuffer likely serves to maintain a history of optimization states or results, ensuring that only the most recent entries are kept.

**Note**: 
- Ensure that the `memory_size` parameter is a non-negative integer to avoid unexpected behavior.
- The FIFOBuffer will automatically discard the oldest items when new items are added beyond its capacity, maintaining the specified buffer size.
***
### FunctionDef construct_prompt(self, summary, mask)
**construct_prompt**: The function of construct_prompt is to construct the system and user prompt.

**parameters**: The parameters of this Function.
· summary: A summary object containing variables and user feedback.
· mask: An optional parameter to mask certain parts of the prompt.
· *args: Additional positional arguments.
· **kwargs: Additional keyword arguments.

**Code Description**: The construct_prompt function is designed to create both system and user prompts by leveraging the functionality of its superclass. Initially, it calls the superclass's construct_prompt method to generate the base system and user prompts. 

If the memory buffer contains any entries, the function enhances the user prompt by adding examples from past interactions. It does this by splitting the user prompt at a predefined final prompt and then appending a formatted string that includes past variables and their corresponding feedback. These examples are formatted as JSON strings for clarity and are joined together with newline characters.

After constructing the enhanced user prompt, the function adds the current summary's variables and user feedback to the memory buffer using the add method from the FIFOBuffer class. This ensures that the memory buffer is updated with the latest interaction, maintaining a record of past interactions for future use.

**Note**: 
- The memory buffer must be properly initialized and managed to ensure that past interactions are correctly stored and retrieved.
- Proper handling of the mask parameter is essential if masking functionality is required.
- The function relies on the superclass's construct_prompt method, so any changes to the superclass method may affect this function's behavior.

**Output Example**: 
A possible return value of the function could be:
```
system_prompt: "System prompt content"
user_prompt: "User prompt content\nBelow are some variables and their feedbacks you received in the past.\n\n{\n    \"variables\": {\n        \"var1\": \"value1\",\n        \"var2\": \"value2\"\n    },\n    \"feedback\": \"positive\"\n}\n\nFinal prompt content"
```
***
