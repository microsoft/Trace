from typing import Any, List, Dict, Union, Tuple
from dataclasses import dataclass
from opto.trace import ExecutionError
from opto.trace.nodes import ParameterNode, Node, MessageNode, ExceptionNode
from opto.optimizers.optimizer import Optimizer
from opto.trace.propagators import TraceGraph, GraphPropagator
from textwrap import dedent, indent
from opto.trace.propagators.propagators import Propagator
from opto.optimizers.buffers import FIFOBuffer
import autogen
import warnings
import json
import re


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


def get_external_nodes(node, visited=set(), external_nodes=set()):
    if node.has_external_dependency:
        external_nodes.add(node)
    elif isinstance(node, MessageNode) and isinstance(node.data, ExecutionError):
        external_nodes.add(node)
    visited.add(node)
    for parent in node.parents:
        if parent not in visited:
            visited, external_nodes = get_external_nodes(parent, visited=visited, external_nodes=external_nodes)
    return visited, external_nodes


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
    others: str
    outputs: str
    feedback: str
    constraints: str

    problem_template = dedent(
        """
        #Instruction
        {instruction}

        #Code (``` seperates different blocks of code)
        {code}

        #Documentation
        {documentation}

        #Variables
        {variables}

        #Constraints
        {constraints}

        #Inputs
        {inputs}

        #Others
        {others}

        #Outputs
        {outputs}

        #Feedback:
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
            others=self.others,
            feedback=self.feedback,
        )


class NestedFunctionOptimizer(Optimizer):
    # This is generic representation prompt, which just explains how to read the problem.
    representation_prompt = dedent(
        """
        You're tasked to solve a coding/algorithm problem. You will see the instruction, the code, the documentation of each function used in the code, and the feedback about the execution result.

        Specifically, a problem will be composed of the following parts:
        - #Instruction: the instruction which describes the things you need to do or the question you should answer.
        - #Code: the code defined in the problem.
        - #Documentation: the documentation of each function used in #Code. The explanation might be incomplete and just contain high-level description. You can use the values in #Others to help infer how those functions work.
        - #Variables: the input variables that you can change.
        - #Constraints: the constraints or descriptions of the variables in #Variables.
        - #Inputs: the values of other inputs to the code, which are not changeable.
        - #Others: the intermediate values created through the code execution.
        - #Outputs: the result of the code output.
        - #Feedback: the feedback about the code's execution result.

        In #Variables, #Inputs, #Outputs, and #Others, the format is:

        <data_type> <variable_name> = <value>

        If <type> is (code), it means <value> is the source code of a python code, which may include docstring and definitions.
        """
    )

    # Optimization
    default_objective = "You need to change the <value> of the variables in #Variables to improve the output in accordance to #Feedback."

    output_format_prompt = dedent(
        """
        Output_format: Your output should be in the following json format, satisfying the json syntax:

        {{
        "reasoning": <Your reasoning>,
        "answer": <Your answer>,
        "suggestion": {{
            <variable_1>: <suggested_value_1>,
            <variable_2>: <suggested_value_2>,
        }}
        }}

        You should write down your thought process in "reasoning". If #Instruction asks for an answer, write it down in "answer". If you need to suggest a change in the values of #Variables, write down the suggested values in "suggestion". Remember you can change only the values in #Variables, not others. When <type> of a variable is (code), you should write the new definition in the format of python code without syntax errors, and you should not change the function name or the function signature.

        If no changes or answer are needed, just output TERMINATE.
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

    # TODO
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
        )
        self.example_response = dedent(
            """
            {"reasoning": 'In this case, the desired response would be to change the value of input a to 14, as that would make the code return 10.',
             "answer", {},
             "suggestion": {"a": 10}
            }
            """
        )

        self.include_example = include_example
        self.max_tokens = max_tokens
        self.log = [] if log else None

    def default_propagator(self):
        """Return the default Propagator object of the optimizer."""
        return GraphPropagator()

    def nested_summarize(self, node):
        # TODO target node can be retrieved as the last node in the graph
        # TODO multiple targtes

        code, documentation, variables, constraints, inputs, outputs, others = [], set(), set(), set(), set(), set(), set()

        parameters = node.parameter_dependencies
        _, external_nodes = get_external_nodes(node, set(), set())
        tmp = set()
        for node in external_nodes:
            tmp = tmp | set(node.parents)

        feedbacks = [node.feedback for node in (parameters | tmp) if (node.trainable or node in tmp)]
        summary = sum(feedbacks[1:], feedbacks[0]) if len(feedbacks) > 1 else feedbacks[0]  # TraceGraph
        summary = node_to_function_feedback(summary)

        ### Append the code & documentation from main graph
        code += ["```"] + [v for k, v in sorted(summary.graph)] + ["```"]
        documentation = documentation | {v for v in summary.documentation.values()}
        ### Append the variables, inputs, constraints, variables from main graph
        trainable_param_dict = {p.py_name: p for p in parameters if p.trainable}
        ### Get the variables
        variables_dict ={
            py_name: data for py_name, data in summary.roots.items() if py_name in trainable_param_dict
        }
        ### Get the inputs
        if "inputs" in node.info:
            inputs_dict = {
                node.py_name: (node.data, None) for node in node.info['inputs']  if node.py_name not in trainable_param_dict
            }  # non-variable roots
        else:
            inputs_dict = {
                py_name: data for py_name, data in summary.roots.items() if py_name not in trainable_param_dict
            }  # non-variable roots
        variables = variables | self.repr_node_value(variables_dict)
        inputs = inputs | self.repr_node_value(inputs_dict)
        constraints = constraints | self.repr_node_constraint(variables_dict)
        others = others | self.repr_node_value(summary.others)

        ### Concat information from expanded subgraph to the main graph
        for node in external_nodes:
            if isinstance(node, ExceptionNode):
                next_node = node.data.exception_node
            else:
                next_node = node.info['output']
            next_node._name = node._name
            expanded_code, expanded_documentation, expanded_variables, \
            expanded_constraints, expanded_inputs, expanded_outputs, \
            expanded_others, _ = self.nested_summarize(next_node)
            code += [f"### Expanding the detailed operation of {node.py_name}"]
            code  += expanded_code
            documentation = documentation | expanded_documentation
            variables = variables | expanded_variables
            constraints = constraints | expanded_constraints
            inputs = inputs | expanded_inputs
            others = others | expanded_others
            if not isinstance(node, ExceptionNode):
                others = others | expanded_outputs
        outputs = self.repr_node_value(summary.output)
        feedback = summary.user_feedback
        return code, documentation, variables, constraints, inputs, outputs, others, feedback

    @staticmethod
    def repr_node_value(node_dict):
        temp_list = set()
        for k, v in node_dict.items():
            if "__code" not in k:
                if isinstance(v[0], str):
                    temp_list.add(f'''({type(v[0]).__name__}) {k}="{v[0]}"''')
                else:
                    temp_list.add(f"({type(v[0]).__name__}) {k}={v[0]}")
            else:
                temp_list.add(f"(code) {k}:{v[0]}")
        return temp_list

    @staticmethod
    def repr_node_constraint(node_dict):
        temp_list = set()
        for k, v in node_dict.items():
            if "__code" not in k:
                if v[1] is not None:
                    if isinstance(v[0], str):
                        temp_list.add(f"({type(v[0]).__name__}) {k}='{v[0]}'")
                    else:
                        temp_list.add(f"({type(v[0]).__name__}) {k}={v[0]}")
            else:
                if v[1] is not None:
                    temp_list.add(f"(code) {k}: {v[1]}")
        return temp_list

    def construct_prompt(self, problem_instance, mask=None, *args, **kwargs):
        """Construct the system and user prompt."""
        system_prompt = self.representation_prompt + self.output_format_prompt  # generic representation + output rule
        user_prompt = self.user_prompt_template.format(
            problem_instance=str(self.problem_instance(*problem_instance, mask=mask))
        )  # problem instance
        if self.include_example:
            user_prompt = (
                self.example_problem_template.format(
                    example_problem=self.example_problem, example_response=self.example_response
                )
                + user_prompt
            )
        user_prompt += self.final_prompt
        return system_prompt, user_prompt

    def problem_instance(self, code, documentation, variables, constraints, inputs,
                               outputs, others, feedback, mask):
        mask = mask or []
        return ProblemInstance(instruction=self.objective,
                               code="\n".join(code) if "#Code" not in mask else "",
                               documentation="\n".join(documentation) if "#Documentation" not in mask else "",
                               variables="\n".join(variables) if "#Variables" not in mask else "",
                               constraints="\n".join(constraints) if "#Constraints" not in mask else "",
                               inputs="\n".join(inputs) if "#Inputs" not in mask else "",
                               outputs="\n".join(outputs) if "#Outputs" not in mask else "",
                               others="\n".join(others) if "#Others" not in mask else "",
                               feedback=feedback if "#Feedback" not in mask else ""
                            )

    def _step(self, verbose=False, mask=None, *args, **kwargs) -> Dict[ParameterNode, Any]:
        assert isinstance(self.propagator, GraphPropagator)
        assert self._target is not None
        problem_instance = self.nested_summarize(self._target)
        system_prompt, user_prompt = self.construct_prompt(problem_instance, mask=mask)
        print(system_prompt, flush=True)
        print(user_prompt, flush=True)
        response = self.call_llm(
            system_prompt=system_prompt, user_prompt=user_prompt, verbose=verbose, max_tokens=self.max_tokens
        )
        print(response, flush=True)
        if "TERMINATE" in response:
            return {}

        suggestion = self.extract_llm_suggestion(response)
        update_dict = self.construct_update_dict(suggestion)
        print(update_dict)

        if self.log is not None:
            self.log.append({"system_prompt": system_prompt, "user_prompt": user_prompt, "response": response})

        return update_dict

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

    def extract_llm_suggestion(self, response: str):
        """Extract the suggestion from the response."""
        suggestion = {}
        attempt_n = 0
        while attempt_n < 2:
            try:
                suggestion = json.loads(response)["suggestion"]
                break
            except json.JSONDecodeError:  # TODO try to fix it
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
            print("Cannot extract suggestion from LLM's response:")
            print(response)

        return suggestion

    def call_llm(
        self, system_prompt: str, user_prompt: str, verbose: Union[bool, str] = False, max_tokens: int = 4096
    ):  # TODO Get this from utils?
        """Call the LLM with a prompt and return the response."""
        if verbose not in (False, "output"):
            print("Prompt\n", system_prompt + user_prompt)

        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]

        try:  # Try tp force it to be a json object
            response = self.llm.create(
                messages=messages,
                response_format={"type": "json_object"},
            )
        except Exception:
            response = self.llm.create(messages=messages, max_tokens=max_tokens)
        response = response.choices[0].message.content

        if verbose:
            print("LLM response:\n", response)
        return response


class NestedFunctionOptimizerV2(NestedFunctionOptimizer):
    # Make the reasoning part more explicit

    output_format_prompt = dedent(
        """
        Output_format: Your output should be in the following json format, satisfying the json syntax:

        {{
        "reasoning": <Your reasoning>,
        "answer": <Your answer>,
        "suggestion": {{
            <variable_1>: <suggested_value_1>,
            <variable_2>: <suggested_value_2>,
        }}
        }}

        In "reasoning", explain the problem: 1. what the #Instruction means 2. what the #Feedback on #Output means to #Variables considering how #Variables are used in #Code and other values in #Documentation, #Inputs, #Others. 3. Reasoning about the suggested changes in #Variables (if needed) and the expected result.

        If #Instruction asks for an answer, write it down in "answer".

        If you need to suggest a change in the values of #Variables, write down the suggested values in "suggestion". Remember you can change only the values in #Variables, not others. When <type> of a variable is (code), you should write the new definition in the format of python code without syntax errors, and you should not change the function name or the function signature.

        If no changes or answer are needed, just output TERMINATE.
        """
    )


class NestedFunctionOptimizerV2Memory(NestedFunctionOptimizerV2):
    # Add memory to the optimizer
    def __init__(self, *args, memory_size=0, **kwargs):
        super().__init__(*args, **kwargs)
        self.memory = FIFOBuffer(memory_size)

    def construct_prompt(self, summary, mask=None, *args, **kwargs):
        """Construct the system and user prompt."""
        system_prompt, user_prompt = super().construct_prompt(summary, mask=mask)
        if len(self.memory) > 0:  # Add examples
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
