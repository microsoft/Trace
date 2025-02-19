import json
from textwrap import dedent

from opto.optimizers.optoprime import OptoPrime


class OPRO(OptoPrime):
    user_prompt_template = dedent(
        """
        Below are some example variables and their feedbacks.

        {examples}

        ================================

        {instruction}
        """
    )

    output_format_prompt = dedent(
        """
        Output_format: Your output should be in the following json format, satisfying
        the json syntax:

        {{
        "suggestion": {{
            <variable_1>: <suggested_value_1>,
            <variable_2>: <suggested_value_2>,
        }}
        }}

        When suggestion variables, write down the suggested values in "suggestion".
        When <type> of a variable is (code), you should write the new definition in the
        format of python code without syntax errors, and you should not change the
        function name or the function signature.

        If no changes or answer are needed, just output TERMINATE.
        """
    )

    default_objective = "Come up with a new variable in accordance to feedback."

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.buffer = []

    def construct_prompt(self, summary, mask=None, *args, **kwargs):
        """Construct the system and user prompt."""
        self.buffer.append((summary.variables, summary.user_feedback))

        examples = []
        for variables, feedback in self.buffer:
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

        user_prompt = self.user_prompt_template.format(
            examples=examples, instruction=self.objective
        )
        return self.output_format_prompt, user_prompt
