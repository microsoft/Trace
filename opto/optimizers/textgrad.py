import json
from textwrap import dedent

from opto.optimizers.optoprime import OptoPrime


class TextGrad(OptoPrime):
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
        Output_format: Your output should be in the following json format, satisfying the json syntax:

        {{
        "suggestion": {{
            <variable_1>: <suggested_value_1>,
            <variable_2>: <suggested_value_2>,
        }}
        }}

        When suggestion variables, write down the suggested values in "suggestion".  When <type> of a variable is (code), you should write the new definition in the format of python code without syntax errors, and you should not change the function name or the function signature.

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

        user_prompt = self.user_prompt_template.format(examples=examples, instruction=self.objective)
        return self.output_format_prompt, user_prompt
    

import textgrad as tg

tg.set_backward_engine("gpt-4o", override=True)

# Step 1: Get an initial response from an LLM.
model = tg.BlackboxLLM("gpt-4o")
question_string = ("If it takes 1 hour to dry 25 shirts under the sun, "
                   "how long will it take to dry 30 shirts under the sun? "
                   "Reason step by step")

question = tg.Variable(question_string,
                       role_description="question to the LLM",
                       requires_grad=False)

answer = model(question)

answer.set_role_description("concise and accurate answer to the question")

# Step 2: Define the loss function and the optimizer, just like in PyTorch!
# Here, we don't have SGD, but we have TGD (Textual Gradient Descent)
# that works with "textual gradients".
optimizer = tg.TGD(parameters=[answer])
evaluation_instruction = (f"Here's a question: {question_string}. "
                           "Evaluate any given answer to this question, "
                           "be smart, logical, and very critical. "
                           "Just provide concise feedback.")

# TextLoss is a natural-language specified loss function that describes
# how we want to evaluate the reasoning.
loss_fn = tg.TextLoss(evaluation_instruction)

# Step 3: Do the loss computation, backward pass, and update the punchline.
# Exact same syntax as PyTorch!
loss = loss_fn(answer)
loss.backward()
optimizer.step()
answer