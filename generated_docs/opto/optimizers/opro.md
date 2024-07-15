## ClassDef OPRO
**OPRO**: The function of OPRO is to serve as a subclass of the FunctionOptimizer class, implementing the optimization process for a specific problem. It overrides the `_step` method to propose new parameter values based on feedback and constructs the update dictionary. It also provides methods for constructing prompts, extracting suggestions, and calling the Language Model (LLM).

**attributes**:
- user_prompt_template: A template for the user prompt, including placeholders for the problem instance and the instruction.
- output_format_prompt: A template for the output format of the optimizer's response, specifying the JSON format and providing a structure for the response.
- default_objective: The default objective of the optimizer, which is to change the values of the variables in the `#Variables` section to improve the output according to the feedback.
- buffer: A list used to store the variables and feedback from each step of the optimization process.

**Code Description**:
The OPRO class is a subclass of the FunctionOptimizer class and provides a specific implementation for optimizing a problem. It extends the FunctionOptimizer class and overrides the `_step` method to propose new parameter values based on feedback and construct the update dictionary.

The `__init__` method initializes the OPRO object by calling the superclass's `__init__` method and passing the arguments. It also initializes the `buffer` attribute as an empty list.

The `construct_prompt` method constructs the system and user prompts based on the summary and a mask. It uses the `user_prompt_template` attribute to format the user prompt, including the problem instance and the instruction.

The `_step` method is responsible for proposing new parameter values based on feedback. It calls the LLM with the system and user prompts and extracts the suggestion from the response. It then constructs the update dictionary using the `construct_update_dict` method.

The `construct_update_dict` method converts the suggestion in text format into the right data type and constructs an update dictionary. It iterates over the trainable parameters and checks if the parameter is present in the suggestion. If it is, it tries to convert the suggestion value to the data type of the parameter and adds it to the update dictionary.

The `extract_llm_suggestion` method extracts the suggestion from the response received from the LLM. It first tries to parse the response as a JSON object and extract the suggestion from the "suggestion" field. If that fails, it tries to extract the suggestion key-value pairs using regular expressions.

The `call_llm` method calls the LLM with a prompt and returns the response. It formats the prompt as a list of messages with system and user roles and calls the LLM's `create` method. It then retrieves the response from the LLM's `choices` attribute.

**Note**:
- The OPRO class is designed to be subclassed and extended to create specific optimizers for different types of problems.
- Subclasses of OPRO must implement the `_step` method.
- The OPRO class provides methods for constructing prompts, extracting suggestions, and calling the LLM.
- The class uses the FunctionOptimizer class as its superclass and inherits its attributes and methods.

**Output Example**:
{
    "reasoning": "In this case, the desired response would be to change the value of input a to 14, as that would make the code return 10.",
    "answer": {},
    "suggestion": {
        "a": 10
    }
}
### FunctionDef __init__(self)
**__init__**: The function of __init__ is to initialize an instance of the OPRO class.

**parameters**: The parameters of this Function.
· *args: Variable length argument list.
· **kwargs: Arbitrary keyword arguments.

**Code Description**: The __init__ method is a constructor that initializes an instance of the OPRO class. It begins by calling the __init__ method of its superclass using the super() function, passing along any arguments (*args) and keyword arguments (**kwargs) it received. This ensures that the parent class is properly initialized. After the superclass initialization, it creates an instance variable named 'buffer' and initializes it as an empty list. This 'buffer' can be used to store data or objects that are relevant to the instance of the OPRO class.

**Note**: 
- Ensure that the superclass of OPRO is correctly defined and its __init__ method is compatible with the arguments passed.
- The 'buffer' list is initialized as empty and can be used to store any necessary data during the lifecycle of the OPRO instance.
***
### FunctionDef construct_prompt(self, summary, mask)
**construct_prompt**: The function of construct_prompt is to construct the system and user prompt based on the provided summary and optional mask.

**parameters**: The parameters of this Function.
· summary: An object containing variables and user feedback.
· mask: An optional parameter that can be used to filter or modify the prompt construction process.
· *args: Additional positional arguments.
· **kwargs: Additional keyword arguments.

**Code Description**: The construct_prompt function begins by appending a tuple of summary variables and user feedback to the buffer. It then iterates over the buffer to create a list of examples. Each example is a JSON-formatted string that includes the variables and feedback. The variables are formatted such that only the first element of each variable's value is included. These examples are joined into a single string with newline characters separating them.

Next, the function constructs the user prompt by formatting the user_prompt_template with the examples and the objective. Finally, it returns a tuple containing the output_format_prompt and the constructed user prompt.

**Note**: 
- Ensure that the summary object contains the necessary attributes: variables and user_feedback.
- The buffer is assumed to be an attribute of the class instance and should be initialized before calling this function.
- The user_prompt_template and objective should also be defined as attributes of the class instance.

**Output Example**: 
Assuming the buffer contains two entries with the following data:
1. variables: {'var1': ['value1'], 'var2': ['value2']}
   feedback: 'Good'
2. variables: {'var3': ['value3'], 'var4': ['value4']}
   feedback: 'Needs improvement'

The returned tuple might look like:
('output_format_prompt_value', 'User prompt with examples:\n{\n    "variables": {\n        "var1": "value1",\n        "var2": "value2"\n    },\n    "feedback": "Good"\n}\n{\n    "variables": {\n        "var3": "value3",\n        "var4": "value4"\n    },\n    "feedback": "Needs improvement"\n}\nInstruction: objective_value')
***
