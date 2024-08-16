from typing import Any, List, Dict, Union, Tuple
from dataclasses import dataclass, asdict
from opto.trace.nodes import ParameterNode, Node, MessageNode
from opto.optimizers.optimizer import Optimizer

from opto.trace.propagators import TraceGraph, GraphPropagator
from textwrap import dedent, indent
from opto.trace.propagators.propagators import Propagator
from opto.optimizers.buffers import FIFOBuffer
import autogen
import warnings
import json

import re

MAX_ROUND = 5

def get_fun_name(node: MessageNode):
    if isinstance(node.info, dict) and "fun_name" in node.info:
        return node.info["fun_name"]
    return node.name.split(":")[0]


def repr_function_call(child: MessageNode):
    function_call = f"{child.py_name} = {get_fun_name(child)}("
    for k, v in child.inputs.items():
        function_call += f"{k}={v.py_name}, "
    function_call = function_call[:-2] + ")"
    return function_call


def node_to_function_feedback(node_feedback: TraceGraph):
    """Convert a TraceGraph to a FunctionFeedback. roots, others, outputs are dict of variable name and its data and constraints."""
    depth = 0 if len(node_feedback.graph) == 0 else node_feedback.graph[-1][0]
    graph = []
    others = {}
    roots = {}
    output = {}
    documentation = {}

    visited = set()
    for level, node in node_feedback.graph:
        # the graph is already sorted
        visited.add(node)

        if node.is_root:  # Need an or condition here
            roots.update({node.py_name: (node.data, node._constraint)})
        else:
            # Some might be root (i.e. blanket nodes) and some might be intermediate nodes
            # Blanket nodes belong to roots
            if all([p in visited for p in node.parents]):
                # this is an intermediate node
                assert isinstance(node, MessageNode)
                documentation.update({get_fun_name(node): node.description})
                graph.append((level, repr_function_call(node)))
                if level == depth:
                    output.update({node.py_name: (node.data, node._constraint)})
                else:
                    others.update({node.py_name: (node.data, node._constraint)})
            else:
                # this is a blanket node (classified into roots)
                roots.update({node.py_name: (node.data, node._constraint)})

    return FunctionFeedback(
        graph=graph,
        others=others,
        roots=roots,
        output=output,
        user_feedback=node_feedback.user_feedback,
        documentation=documentation,
    )


@dataclass
class FunctionFeedback:
    """Feedback container used by FunctionPropagator."""

    graph: List[
        Tuple[int, str]
    ]  # Each item is is a representation of function call. The items are topologically sorted.
    documentation: Dict[str, str]  # Function name and its documentationstring
    others: Dict[str, Any]  # Intermediate variable names and their data
    roots: Dict[str, Any]  # Root variable name and its data
    output: Dict[str, Any]  # Leaf variable name and its data
    user_feedback: str  # User feedback at the leaf of the graph


@dataclass
class ProblemInstance:
    instruction: str
    code: str
    documentation: str
    variables: str
    inputs: str
    feedback: str
    outputs: str
    constraints: str

    problem_template = dedent(
        """
        #Instruction
        {instruction}

        #Code
        {code}

        #Documentation
        {documentation}

        #Variables
        {variables}

        #Constraints
        {constraints}

        #Inputs
        {inputs}

        #Outputs
        {outputs}

        #Feedback
        {feedback}

        
        """
    )

    def __repr__(self) -> str:
        return self.problem_template.format(
            instruction=self.instruction,
            code=self.code,
            documentation=self.documentation,
            variables=self.variables,
            constraints=self.constraints,
            inputs=self.inputs,
            outputs=self.outputs,
            feedback=self.feedback,
        )

#- #Variables of which values could be checked: a list of variables that you could request a value check
#- #Variables of which values have been already checked: the values of intermediate variables in the code, which you have previously requested a check.


class OptoPrimeNewV1(Optimizer):
    # This is generic representation prompt, which just explains how to read the problem.
    representation_prompt = dedent(
        """
        You're tasked to solve a coding/algorithm problem. You will see the instruction, the code, the documentation of each function used in the code, and the feedback about the execution result.

        Specifically, a problem will be composed of the following parts:
        - #Instruction: the instruction which describes the things you need to do or the question you should answer.
        - #Code: the code defined in the problem.
        - #Documentation: the documentation of each function used in #Code. The explanation might be incomplete and just contain high-level description. You can use the values shown below to help infer how those functions work. 
        - #Parameters: the input variables that you can change.
        - #Constraints: the constraints or descriptions of the variables in #Variables.
        - #Inputs: the values of other inputs to the code, which are not changeable.
        - #Outputs: the result of the code output.
        - #Feedback: the feedback about the code's execution result.

        In #Parameters, #Inputs, #Outputs, the format is:

        <data_type> <variable_name> = <value>

        If <type> is (code), it means <value> is the source code of a python code, which may include docstring and definitions.
        """
    )

    # Optimization
    default_objective = dedent(
    """
        You need to change the <value> of the variables in #Variables to improve the output in accordance to #Feedback.
        But before making a suggestion of the update, you may need to check the intermediate values of variables appeared in #Code.
        
        You will see a list of values of the variables that you have requested to check, as well as the collection of all the available variables for value check.
        You only need to check values of variables that do not appear in #Inputs and #Outputs since the values of variables there have already been provided.
        Please don't make any unnecessary checks. Keep your number of checks as small as possible. 
    """
    )


    output_format_prompt = dedent(
        """
        Output_format: Your output should be in the following json format, satisfying the json syntax:

        {{
        "reasoning": <Your reasoning>,
        "answer": <Your answer>,
        "value_check": <A list of variable names of which you want to check their values>
        "suggestion": {{
            <variable_1>: <suggested_value_1>,
            <variable_2>: <suggested_value_2>,
        }}
        }}

        In "reasoning", explain the problem: 1. what the #Instruction means 2. what the #Feedback on #Output means to #Variables considering how #Variables are used in #Code and other values in #Documentation, #Inputs, #Others. 3. Reasoning about the suggested changes in #Variables (if needed) and the expected result.

        If #Instruction asks for an answer, write it down in "answer".
        
        If you need to suggest a change in the values of #Variables, write down the suggested values in "suggestion". Remember you can change only the values in #Variables, not others. When <type> of a variable is (code), you should write the new definition in the format of python code without syntax errors, and you should not change the function name or the function signature.

        If no changes or answer are needed, just output TERMINATE.

        If the information is insuffcient to provide “answer “or “suggestion”, then you can put their names in the "value_check" sections of your response and leave "suggestion" section empty.

        Example Format of the output if you want to check values of some intermediate variables:
        {{
        "reasoning": "<Your reasoning>",
        "answer": <Your answer>,
        "value_check": [var1,..., varN]
        "suggestion":  
        }}

        Example Format of the output if you are ready to make a suggestion of the update:
        {{
        "reasoning": "<Your reasoning>",
        "answer": <Your answer>,
        "value_check": 
        "suggestion":  <Your suggested update of the values>
        }}
        
        """
    )

    example_problem_template = dedent(
        """
        Here is an example of problem instance and response:

        ================================
        {example_problem}
        ================================

        Your response:
        {example_response}
        """
    )

    user_prompt_template = dedent(
        """
        Now you see problem instance:

        ================================
        {problem_instance}
        ================================

        """
    )

    example_prompt = dedent(
        """

        Here are some feasible but not optimal solutions for the current problem instance. Consider this as a hint to help you understand the problem better.

        ================================

        {examples}

        ================================
        """
    )

    final_prompt = dedent(
        """
        Your response:
        """
    )

    def __init__(
        self,
        parameters: List[ParameterNode],
        config_list: List = None,
        *args,
        propagator: Propagator = None,
        objective: Union[None, str] = None,
        ignore_extraction_error: bool = True,  # ignore the type conversion error when extracting updated values from LLM's suggestion
        include_example=False,  # TODO # include example problem and response in the prompt
        memory_size=0,  # Memory size to store the past feedback
        max_tokens=4096,
        log=True,
        **kwargs,
    ):
        super().__init__(parameters, *args, propagator=propagator, **kwargs)
        self.ignore_extraction_error = ignore_extraction_error
        if config_list is None:
            config_list = autogen.config_list_from_json("OAI_CONFIG_LIST")
        self.llm = autogen.OpenAIWrapper(config_list=config_list)
        self.objective = objective or self.default_objective
        self.example_problem = ProblemInstance.problem_template.format(
            instruction=self.default_objective,
            code="y = add(x=a,y=b)\nz = subtract(x=y, y=c)",
            documentation="add: add x and y \nsubtract: subtract y from x",
            variables="(int) a = 5",
            constraints="a: a > 0",
            outputs="(int) z = 1",
            others="(int) y = 6",
            inputs="(int) b = 1\n(int) c = 5",
            feedback="The result of the code is not as expected. The result should be 10, but the code returns 1",
            stepsize=1,
            variable_list="y"
        )
        self.example_response = dedent(
            """
            {"reasoning": 'In this case, the desired response would be to change the value of input a to 14, as that would make the code return 10.',
             "answer", {{}},
             "value_check": [],
             "suggestion": {"a": 10}
            }
            """
        )

        self.include_example = include_example
        self.max_tokens = max_tokens
        self.log = [] if log else None
        self.summary_log = [] if log else None
        self.memory = FIFOBuffer(memory_size)

    def default_propagator(self):
        """Return the default Propagator object of the optimizer."""
        return GraphPropagator()

    def summarize(self):
        # Aggregate feedback from all the parameters
        feedbacks = [self.propagator.aggregate(node.feedback) for node in self.parameters if node.trainable]
        summary = sum(feedbacks)  # TraceGraph
        # Construct variables and update others
        # Some trainable nodes might not receive feedback, because they might not be connected to the output
        summary = node_to_function_feedback(summary)
        # Classify the root nodes into variables and others
        # summary.variables = {p.py_name: p.data for p in self.parameters if p.trainable and p.py_name in summary.roots}

        trainable_param_dict = {p.py_name: p for p in self.parameters if p.trainable}
        summary.variables = {
            py_name: data for py_name, data in summary.roots.items() if py_name in trainable_param_dict
        }
        summary.inputs = {
            py_name: data for py_name, data in summary.roots.items() if py_name not in trainable_param_dict
        }  # non-variable roots

        return summary

    @staticmethod
    def repr_node_value(node_dict):
        temp_list = []
        for k, v in node_dict.items():
            if "__code" not in k:
                temp_list.append(f"({type(v[0]).__name__}) {k}={v[0]}")
            else:
                temp_list.append(f"(code) {k}:{v[0]}")
        
        return "\n".join(temp_list)

    @staticmethod
    def repr_node_constraint(node_dict):
        temp_list = []
        for k, v in node_dict.items():
            if "__code" not in k:
                if v[1] is not None:
                    temp_list.append(f"({type(v[0]).__name__}) {k}: {v[1]}")
            else:
                if v[1] is not None:
                    temp_list.append(f"(code) {k}: {v[1]}")
        return "\n".join(temp_list)

    def probelm_instance(self, summary, mask=None):
        mask = mask or []

        return ProblemInstance(
            instruction=self.objective if '#Instruction' not in mask else "",
            code="\n".join([v for k, v in sorted(summary.graph)]) if "#Code" not in mask else "",
            documentation="\n".join([v for v in summary.documentation.values()])
            if "#Documentation" not in mask
            else "",
            variables=self.repr_node_value(summary.variables) if "#Variables" not in mask else "",
            constraints=self.repr_node_constraint(summary.variables) if "#Constraints" not in mask else "",
            inputs=self.repr_node_value(summary.inputs) if "#Inputs" not in mask else "",
            outputs=self.repr_node_value(summary.output) if "#Outputs" not in mask else "",
            feedback=summary.user_feedback if "#Feedback" not in mask else "",
        )
    
    def get_variable_check_prompt(self, variable_list, checked_value):
        variables_check_prompt = dedent(
            """
            Here is a list of variables of which values could be checked:
            {variable_list}

            Here is a list of the values from intermediate variables in the code, which you have previously requested a check.
            {checked_value}
            """
        ).format(variable_list=variable_list, checked_value=checked_value)
        return variables_check_prompt

    def construct_prompt(self, summary, mask=None,  variable_list="", checked_node_dict={}, *args, **kwargs):
        """Construct the system and user prompt."""
        system_prompt = self.representation_prompt + self.output_format_prompt  # generic representation + output rule

        user_prompt = self.user_prompt_template.format(
            problem_instance=str(self.probelm_instance(summary, mask=mask))
        )  # problem instance
        user_prompt += self.get_variable_check_prompt(variable_list, self.repr_node_value(checked_node_dict))

        if self.include_example:
            user_prompt = (
                self.example_problem_template.format(
                    example_problem=self.example_problem, example_response=self.example_response
                )
                + user_prompt
            )
        user_prompt += self.final_prompt

        # Add examples
        if len(self.memory) > 0:
            prefix = user_prompt.split(self.final_prompt)[0]
            examples = []
            for variables, feedback in self.memory:
                examples.append(
                    json.dumps(
                        {
                            "variables": {k: v[0] for k, v in variables.items()},
                            "feedback": feedback,
                        },
                        indent=4,
                    )
                )
            examples = "\n".join(examples)
            user_prompt = (
                prefix
                + f"\nBelow are some variables and their feedbacks you received in the past.\n\n{examples}\n\n"
                + self.final_prompt
            )
        self.memory.add((summary.variables, summary.user_feedback))

        return system_prompt, user_prompt

    def _step(self, verbose=False, mask=None, hide_intermediate_values=False, screenshot_list=None, *args, **kwargs) -> Dict[ParameterNode, Any]:
        assert isinstance(self.propagator, GraphPropagator)
        summary = self.summarize()
        value_map = summary.others | summary.variables | summary.inputs | summary.output
        
        ### Prepare the list of variables that are allowed for value check
        variable_set = set()
        for k, v in summary.others.items():
            variable_set.add(k)
        checked_node_dict={}
        round = 0

        while round < MAX_ROUND:
            variable_list = ", ".join(variable_set)
            system_prompt, user_prompt = self.construct_prompt(summary, mask=mask, 
                                                               variable_list=variable_list,
                                                               checked_node_dict=checked_node_dict)
            response = self.call_llm(
                system_prompt=system_prompt, user_prompt=user_prompt, 
                verbose=verbose, 
                max_tokens=self.max_tokens,
                screenshot_list=screenshot_list
            )

            if "TERMINATE" in response:
                return {}, response
            
            variables = self.extract_variables(response)
            if len(variables) == 0:
                break
            else:
                for variable in variables:
                    checked_node_dict[variable] = value_map[variable]
                    variable_set.discard(variable)
            round += 1
        
        suggestion = self.extract_llm_suggestion(response)
        update_dict = self.construct_update_dict(suggestion)

        if self.log is not None:
            self.log.append({"system_prompt": system_prompt, "user_prompt": user_prompt, "response": response})
            self.summary_log.append({'problem_instance': self.probelm_instance(summary), 'summary': summary})

        return update_dict, response

    def construct_update_dict(self, suggestion: Dict[str, Any]) -> Dict[ParameterNode, Any]:
        """Convert the suggestion in text into the right data type."""
        # TODO: might need some automatic type conversion
        update_dict = {}
        for node in self.parameters:
            if node.trainable and node.py_name in suggestion:
                try:
                    update_dict[node] = type(node.data)(suggestion[node.py_name])
                except (ValueError, KeyError) as e:
                    # catch error due to suggestion missing the key or wrong data type
                    if self.ignore_extraction_error:
                        warnings.warn(
                            f"Cannot convert the suggestion '{suggestion[node.py_name]}' for {node.py_name} to the right data type"
                        )
                    else:
                        raise e
        return update_dict


    def extract_variables(self, response: str):
        """Extract the variable names to check"""
        variables = []
        try:
            # Attempt to load JSON directly
            parsed_json = json.loads(response)
            variables = parsed_json.get("value_check", [])
        except json.JSONDecodeError:
            # If JSON decoding fails, attempt to extract the value_check content using regex
            match = re.search(r'"value_check":\s*\[(.*?)\]', response, re.DOTALL)
            if match:
                # Find all variables inside the brackets, regardless of single or double quotes
                variables = re.findall(r"[\"']\s*([^\"']+)\s*[\"']", match.group(1))

        return variables




    def extract_llm_suggestion(self, response: str):
        """Extract the suggestion from the response."""
        suggestion = {}
        attempt_n = 0
        while attempt_n < 2:
            try:
                suggestion = json.loads(response)["suggestion"]
                break
            except json.JSONDecodeError:
                # Remove things outside the brackets
                response = re.findall(r"{.*}", response, re.DOTALL)
                if len(response) > 0:
                    response = response[0]
                attempt_n += 1
            except Exception:
                attempt_n += 1

        if len(suggestion) == 0:
            # we try to extract key/value separately and return it as a dictionary
            pattern = r'"suggestion"\s*:\s*\{(.*?)\}'
            suggestion_match = re.search(pattern, str(response), re.DOTALL)
            if suggestion_match:
                suggestion = {}
                # Extract the entire content of the suggestion dictionary
                suggestion_content = suggestion_match.group(1)
                # Regex to extract each key-value pair;
                # This scheme assumes double quotes but is robust to missing cammas at the end of the line
                pair_pattern = r'"([a-zA-Z0-9_]+)"\s*:\s*"(.*)"'
                # Find all matches of key-value pairs
                pairs = re.findall(pair_pattern, suggestion_content, re.DOTALL)
                for key, value in pairs:
                    suggestion[key] = value

        if len(suggestion) == 0:
            if not self.ignore_extraction_error:
                print("Cannot extract suggestion from LLM's response:")
                print(response)

        # if the suggested value is a code, and the entire code body is empty (i.e., not even function signature is present)
        # then we remove such suggestion
        try:
            for key, value in suggestion.items():
                if "__code" in key and value == '':
                    del suggestion[key]
        except:
            print("Cannot extract suggestion from LLM's response")
            print(response)

        return suggestion

    def call_llm(
        self, system_prompt: str, user_prompt: str, 
        verbose: Union[bool, str] = False, 
        max_tokens: int = 4096,
        screenshot_list = None,
    ):
        """Call the LLM with a prompt and return the response."""
        if verbose not in (False, "output"):
            print("Prompt\n", system_prompt + user_prompt)

        messages = [{"role": "system", "content": system_prompt}]
        if screenshot_list is not None:
            import base64
            for screenshot_path in screenshot_list:
                with open(screenshot_path, "rb") as image_file:
                    image_base64 = base64.b64encode(image_file.read()).decode('utf-8')
                    image_url = f"data:image/png;base64,{image_base64}"
                    messages.append({"role":"user", "content": [
                        {"type": "text", "text":f"Here is the screenshot image saved at {screenshot_path}"},
                        {"type": "image_url", "image_url":{"url": image_url}}
                    ]})
        messages.append({"role": "user", "content": user_prompt})

        try:  # Try tp force it to be a json object
            response = self.llm.create(
                messages=messages,
                response_format={"type": "json_object"},
                max_tokens=max_tokens,
            )
        except Exception:
            response = self.llm.create(messages=messages, max_tokens=max_tokens)
        response = response.choices[0].message.content

        if verbose:
            print("LLM response:\n", response)
        return response
