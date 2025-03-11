import json
from textwrap import dedent, indent
from opto.optimizers.optoprime import OptoPrime


class OptoprimeBatchOpt(OptoPrime):
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
        What are your suggestions on variables {names}?
        
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

        var_names = []
        for k, v in summary.variables.items():
            var_names.append(f"{k}")  # ({type(v[0]).__name__})
        var_names = ", ".join(var_names)

        user_prompt += self.final_prompt.format(names=var_names)

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
