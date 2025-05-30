from typing import Any, List, Dict, Union, Tuple
from dataclasses import dataclass, asdict
from textwrap import dedent, indent
import warnings
import json
import re
import copy
from opto.trace.nodes import ParameterNode, Node, MessageNode
from opto.trace.propagators import TraceGraph, GraphPropagator
from opto.trace.propagators.propagators import Propagator
from opto.optimizers.optimizer import Optimizer
from opto.optimizers.buffers import FIFOBuffer
from opto.utils.llm import AbstractModel, LLM

from black import format_str, FileMode

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
    others: str
    outputs: str
    feedback: str
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

        #Others
        {others}

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
            others=self.others,
            feedback=self.feedback,
        )


class OptoPrime(Optimizer):
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

        In "reasoning", explain the problem: 1. what the #Instruction means 2. what the #Feedback on #Output means to #Variables considering how #Variables are used in #Code and other values in #Documentation, #Inputs, #Others. 3. Reasoning about the suggested changes in #Variables (if needed) and the expected result.

        If #Instruction asks for an answer, write it down in "answer".

        If you need to suggest a change in the values of #Variables, write down the suggested values in "suggestion". Remember you can change only the values in #Variables, not others. When <type> of a variable is (code), you should write the new definition in the format of python code without syntax errors, and you should not change the function name or the function signature.

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

    default_prompt_symbols = {
        "variables": "#Variables",
        "constraints": "#Constraints",
        "inputs": "#Inputs",
        "outputs": "#Outputs",
        "others": "#Others",
        "feedback": "#Feedback",
        "instruction": "#Instruction",
        "code": "#Code",
        "documentation": "#Documentation",
    }

    def __init__(
        self,
        parameters: List[ParameterNode],
        llm: AbstractModel = None,
        *args,
        propagator: Propagator = None,
        objective: Union[None, str] = None,
        ignore_extraction_error: bool = True,  # ignore the type conversion error when extracting updated values from LLM's suggestion
        include_example=False,  # TODO # include example problem and response in the prompt
        memory_size=0,  # Memory size to store the past feedback
        max_tokens=4096,
        log=True,
        prompt_symbols=None,
        **kwargs,
    ):
        super().__init__(parameters, *args, propagator=propagator, **kwargs)
        self.ignore_extraction_error = ignore_extraction_error
        self.llm = llm or LLM()
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
        self.summary_log = [] if log else None
        self.memory = FIFOBuffer(memory_size)
        self.prompt_symbols = copy.deepcopy(self.default_prompt_symbols)
        if prompt_symbols is not None:
            self.prompt_symbols.update(prompt_symbols)

    def default_propagator(self):
        """Return the default Propagator object of the optimizer."""
        return GraphPropagator()

    def summarize(self):
        # Aggregate feedback from all the parameters
        feedbacks = [
            self.propagator.aggregate(node.feedback)
            for node in self.parameters
            if node.trainable
        ]
        summary = sum(feedbacks)  # TraceGraph
        # Construct variables and update others
        # Some trainable nodes might not receive feedback, because they might not be connected to the output
        summary = node_to_function_feedback(summary)
        # Classify the root nodes into variables and others
        # summary.variables = {p.py_name: p.data for p in self.parameters if p.trainable and p.py_name in summary.roots}

        trainable_param_dict = {p.py_name: p for p in self.parameters if p.trainable}
        summary.variables = {
            py_name: data
            for py_name, data in summary.roots.items()
            if py_name in trainable_param_dict
        }
        summary.inputs = {
            py_name: data
            for py_name, data in summary.roots.items()
            if py_name not in trainable_param_dict
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

    def problem_instance(self, summary, mask=None):
        mask = mask or []
        return ProblemInstance(
            instruction=self.objective if "#Instruction" not in mask else "",
            code=(
                "\n".join([v for k, v in sorted(summary.graph)])
                if "#Code" not in mask
                else ""
            ),
            documentation=(
                "\n".join([v for v in summary.documentation.values()])
                if "#Documentation" not in mask
                else ""
            ),
            variables=(
                self.repr_node_value(summary.variables)
                if "#Variables" not in mask
                else ""
            ),
            constraints=(
                self.repr_node_constraint(summary.variables)
                if "#Constraints" not in mask
                else ""
            ),
            inputs=(
                self.repr_node_value(summary.inputs) if "#Inputs" not in mask else ""
            ),
            outputs=(
                self.repr_node_value(summary.output) if "#Outputs" not in mask else ""
            ),
            others=(
                self.repr_node_value(summary.others) if "#Others" not in mask else ""
            ),
            feedback=summary.user_feedback if "#Feedback" not in mask else "",
        )

    def construct_prompt(self, summary, mask=None, *args, **kwargs):
        """Construct the system and user prompt."""
        system_prompt = (
            self.representation_prompt + self.output_format_prompt
        )  # generic representation + output rule
        user_prompt = self.user_prompt_template.format(
            problem_instance=str(self.problem_instance(summary, mask=mask))
        )  # problem instance
        if self.include_example:
            user_prompt = (
                self.example_problem_template.format(
                    example_problem=self.example_problem,
                    example_response=self.example_response,
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

    def replace_symbols(self, text: str, symbols: Dict[str, str]) -> str:
        for k, v in symbols.items():
            text = text.replace(self.default_prompt_symbols[k], v)
        return text

    def _step(
        self, verbose=False, mask=None, *args, **kwargs
    ) -> Dict[ParameterNode, Any]:
        assert isinstance(self.propagator, GraphPropagator)
        summary = self.summarize()
        system_prompt, user_prompt = self.construct_prompt(summary, mask=mask)

        system_prompt = self.replace_symbols(system_prompt, self.prompt_symbols)
        user_prompt = self.replace_symbols(user_prompt, self.prompt_symbols)

        response = self.call_llm(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            verbose=verbose,
            max_tokens=self.max_tokens,
        )

        if "TERMINATE" in response:
            return {}

        suggestion = self.extract_llm_suggestion(response)
        update_dict = self.construct_update_dict(suggestion)

        if self.log is not None:
            self.log.append(
                {
                    "system_prompt": system_prompt,
                    "user_prompt": user_prompt,
                    "response": response,
                }
            )
            self.summary_log.append(
                {"problem_instance": self.problem_instance(summary), "summary": summary}
            )

        return update_dict

    def construct_update_dict(
        self, suggestion: Dict[str, Any]
    ) -> Dict[ParameterNode, Any]:
        """Convert the suggestion in text into the right data type."""
        # TODO: might need some automatic type conversion
        update_dict = {}
        for node in self.parameters:
            if node.trainable and node.py_name in suggestion:
                try:
                    formatted_suggestion = suggestion[node.py_name]
                    # use black formatter for code reformatting
                    if type(formatted_suggestion) == str and 'def' in formatted_suggestion:
                        formatted_suggestion = format_str(formatted_suggestion, mode=FileMode())
                    update_dict[node] = type(node.data)(formatted_suggestion)
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
            except json.JSONDecodeError:
                # Remove things outside the brackets
                response = re.findall(r"{.*}", response, re.DOTALL)
                if len(response) > 0:
                    response = response[0]
                attempt_n += 1
            except Exception:
                attempt_n += 1

        if not isinstance(suggestion, dict):
            suggestion = {}

        if len(suggestion) == 0:
            # we try to extract key/value separately and return it as a dictionary
            pattern = r'"suggestion"\s*:\s*\{(.*?)\}'
            suggestion_match = re.search(pattern, str(response), re.DOTALL)
            if suggestion_match:
                suggestion = {}
                # Extract the entire content of the suggestion dictionary
                suggestion_content = suggestion_match.group(1)
                # Regex to extract each key-value pair;
                # This scheme assumes double quotes but is robust to missing commas at the end of the line
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
        keys_to_remove = []
        for key, value in suggestion.items():
            if "__code" in key and value.strip() == "":
                keys_to_remove.append(key)
        for key in keys_to_remove:
            del suggestion[key]

        return suggestion

    def call_llm(
        self,
        system_prompt: str,
        user_prompt: str,
        verbose: Union[bool, str] = False,
        max_tokens: int = 4096,
    ):
        """Call the LLM with a prompt and return the response."""
        if verbose not in (False, "output"):
            print("Prompt\n", system_prompt + user_prompt)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        try:  # Try tp force it to be a json object
            response = self.llm(
                messages=messages,
                response_format={"type": "json_object"},
                max_tokens=max_tokens,
            )
        except Exception:
            response = self.llm(messages=messages, max_tokens=max_tokens)
        response = response.choices[0].message.content

        if verbose:
            print("LLM response:\n", response)
        return response
