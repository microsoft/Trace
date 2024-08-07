from typing import Any, List, Dict, Union, Tuple
from textwrap import dedent

from opto.trace.nodes import ParameterNode, Node
from opto.optimizers.optimizer import Optimizer
from opto.optimizers.optoprime import ProblemInstance
from opto.optimizers.buffers import FIFOBuffer
import autogen
import json

class Synthesizer(Optimizer):
    # This is generic representation prompt, which explains how to read the problem.
    representation_prompt = dedent(
        """
        You're tasked to decompose user feedback into a rubric for a student to follow.
        You will be given the coding/algorithm problem. You will see the instruction, the code, the documentation of each function used in the code, and the feedback about the execution result.
        Your task is to come up with a rubric that the student can follow to improve the code based on the feedback.
        
        Specifically, a problem will be composed of the following parts:
        - #Instruction: the instruction which describes the things the student need to do or the question they should answer.
        - #Code: the code defined in the problem.
        - #Documentation: the documentation of each function used in #Code. The explanation might be incomplete and just contain high-level description. 
        - #Variables: the input variables that the student can change.
        - #Constraints: the constraints or descriptions of the variables in #Variables.
        - #Inputs: the values of other inputs to the code, which are not changeable.
        - #Others: the intermediate values created through the code execution.
        - #Outputs: the result of the code output.
        - #Feedback: the user's feedback about the code's execution result.

        In #Variables, #Inputs, #Outputs, and #Others, the format is:

        <data_type> <variable_name> = <value>

        If <type> is (code), it means <value> is the source code of a python code, which may include docstring and definitions.
        """
    )

    # Optimization
    default_objective = "You need to come up with a rubric that the student can follow to change the <value> of the variables in #Variables in accordance to #Feedback."

    output_format_prompt = dedent(
        """
        Output_format: Your output should be in the following json format, satisfying the json syntax:

        {{
        "reasoning": <Your reasoning>,
        "rubric": {{
            <rubric_1>: <rubric_description_1>,
            <rubric_2>: <rubric_description_2>,
        }}
        }}

        In "reasoning", explain the problem: 1. what the #Instruction means 2. what the #Feedback on #Output means to #Variables considering how #Variables are used in #Code and other values in #Documentation, #Inputs, #Others. 3. Reasoning about how the #Feedback can be decomposed into a rubric for the student to follow.

        Write down the rubrics in "rubric". You must incorporate past feedback into the rubric and keep the list consistent. 
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
        objective: Union[None, str] = None,
        ignore_extraction_error: bool = True,  # ignore the type conversion error when extracting updated values from LLM's suggestion
        include_example=False,  # TODO # include example problem and response in the prompt
        memory_size=0,  # Memory size to store the past feedback
        max_tokens=4096,
        log=True,
        **kwargs,
    ):
        super().__init__(parameters, *args, **kwargs)
        self.ignore_extraction_error = ignore_extraction_error
        if config_list is None:
            config_list = autogen.config_list_from_json("OAI_CONFIG_LIST")
        self.llm = autogen.OpenAIWrapper(config_list=config_list)
        self.objective = objective or self.default_objective
        # TODO: Change example problem and response
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

    def construct_prompt(self, summary, mask=None, *args, **kwargs):
        """Construct the system and user prompt."""
        system_prompt = self.representation_prompt + self.output_format_prompt  # generic representation + output rule
        user_prompt = self.user_prompt_template.format(
            problem_instance=str(self.probelm_instance(summary, mask=mask))
        )  # problem instance
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

    def _step(self, verbose=False, mask=None, *args, **kwargs) -> Dict[ParameterNode, Any]:
        summary = self.summarize()
        system_prompt, user_prompt = self.construct_prompt(summary, mask=mask)
        response = self.call_llm(
            system_prompt=system_prompt, user_prompt=user_prompt, verbose=verbose, max_tokens=self.max_tokens
        )

        if "TERMINATE" in response:
            return {}

        suggestion = self.extract_llm_suggestion(response)
        update_dict = self.construct_update_dict(suggestion)

        if self.log is not None:
            self.log.append({"system_prompt": system_prompt, "user_prompt": user_prompt, "response": response})
            self.summary_log.append({'problem_instance': self.probelm_instance(summary), 'summary': summary})

        return update_dict