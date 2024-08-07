import json
from textwrap import dedent
import re

from opto.trace.propagators import TraceGraph, GraphPropagator
from opto.optimizers.optoprime import OptoPrime

### Agenda
# (done) 1. Establish an interaction interface between synth and optimizer (in the code)
# 2. Implement the synth class
# 3. Refine the synth class

class OptoSynth(OptoPrime):
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
        You should provide a most concise and clear rubric that captures the essence of the feedback. 
        Each rubric should target one specific aspect of the feedback. 
        Each rubric should contain a rule the output must satisfy. It is okay to have multiple rubric items for one feedback.
        Each rubric item should not overlap with others. It is okay to have only one rubric.
        Based on one rubric, the student should be able to make a change to the code to satisfy the rule.
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

    # TODO: change this
    user_prompt_template = dedent(
        """
        Now you see problem instance:

        ================================
        {problem_instance}
        ================================

        """
    )

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.buffer = []

    # def construct_prompt(self, summary, mask=None, *args, **kwargs):
    #     """Construct the system and user prompt."""
    #     self.buffer.append((summary.variables, summary.user_feedback))

    #     examples = []
    #     for variables, feedback in self.buffer:
    #         examples.append(
    #             json.dumps(
    #                 {
    #                     "variables": {k: v[0] for k, v in variables.items()},
    #                     "feedback": feedback,
    #                 },
    #                 indent=4,
    #             )
    #         )
    #     examples = "\n".join(examples)

    #     user_prompt = self.user_prompt_template.format(examples=examples, instruction=self.objective)
    #     return self.output_format_prompt, user_prompt

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _step(self, verbose=False, mask=None, *args, **kwargs):
        assert isinstance(self.propagator, GraphPropagator)
        summary = self.summarize()
        system_prompt, user_prompt = self.construct_prompt(summary, mask=mask)
        response = self.call_llm(
            system_prompt=system_prompt, user_prompt=user_prompt, verbose=verbose, max_tokens=self.max_tokens
        )

        if "TERMINATE" in response:
            return {}


        rubric = self.extract_llm_rubric(response)
        # update_dict = self.construct_update_dict(suggestion)
        output = self.format_rubric(rubric)

        if self.log is not None:
            self.log.append({"system_prompt": system_prompt, "user_prompt": user_prompt, "response": response})
            self.summary_log.append({'problem_instance': self.probelm_instance(summary), 'summary': summary})

        return output
    
    def format_rubric(self, rubrics) -> str:
        """Format the rubric for the optimizer"""
        inner_feedback = ""
        breakpoint()
        for rubric, value in rubrics.items():
            inner_feedback += value + "\n"

        return inner_feedback

    def extract_llm_rubric(self, response: str):
        """Extract the rubric from the response."""
        rubric = {}
        attempt_n = 0
        while attempt_n < 2:
            try:
                rubric = json.loads(response)["rubric"]
                break
            except json.JSONDecodeError:
                # Remove things outside the brackets
                response = re.findall(r"{.*}", response, re.DOTALL)
                if len(response) > 0:
                    response = response[0]
                attempt_n += 1
            except Exception:
                attempt_n += 1

        if len(rubric) == 0:
            # we try to extract key/value separately and return it as a dictionary
            pattern = r'"rubric"\s*:\s*\{(.*?)\}'
            rubric_match = re.search(pattern, str(response), re.DOTALL)
            if rubric_match:
                rubric = {}
                # Extract the entire content of the rubric dictionary
                rubric_content = rubric_match.group(1)
                # Regex to extract each key-value pair;
                # This scheme assumes double quotes but is robust to missing cammas at the end of the line
                pair_pattern = r'"([a-zA-Z0-9_]+)"\s*:\s*"(.*)"'
                # Find all matches of key-value pairs
                pairs = re.findall(pair_pattern, rubric_content, re.DOTALL)
                for key, value in pairs:
                    rubric[key] = value

        if len(rubric) == 0:
            if not self.ignore_extraction_error:
                print("Cannot extract rubric from LLM's response:")
                print(response)

        # if the suggested value is a code, and the entire code body is empty (i.e., not even function signature is present)
        # then we remove such rubric
        for key, value in rubric.items():
            if "__code" in key and value == '':
                del rubric[key]

        return rubric