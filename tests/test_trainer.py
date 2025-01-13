import datasets
import numpy as np
from opto import trace
from opto.utils.llm import AutoGenLLM
from opto.optimizers.utils import print_color
from opto.optimizers import OptoPrime
from opto.trainer import train
from typing import Any


@trace.model
class Student:
    # A basic LLM agent.

    def __init__(self, system_prompt: str = "You're a helpful agent",
                       user_prompt_template: str = "Query: {message}",
                       llm: AutoGenLLM = None):
        self.system_prompt = trace.node(system_prompt, trainable=True)
        self.user_prompt_template = trace.node(user_prompt_template)
        self.llm = llm or AutoGenLLM()

    @trace.bundle()
    def model(self, system_prompt: str, user_prompt_template: str, message: str) -> str:
        """ Call the LLM model. system_prompt specifies
        the behavior of the agent. user prompt is the input to the agent, which
        is formatted as user_prompt_template.format(message=message)."""

        if '{message}' not in user_prompt_template:
            raise ValueError("user_prompt_template must contain '{message}'")

        response = self.llm(
              messages = [{"role": "system", "content": system_prompt},
                          {"role": "user", "content": user_prompt_template.format(message=message)}]
        )
        return response.choices[0].message.content

    def forward(self, message: Any) -> Any:
        """ Forward pass of the agent. """
        return self.model(self.system_prompt, self.user_prompt_template, message)


def teacher(student_answer, info, model="gpt-4o-mini_2024-07-18"):
    """ Use LLM to evaluate the student answer. """
    llm = AutoGenLLM(filter_dict={"model": [model]})
    system_prompt = "You're a match teacher who helps students to learn. "
    user_prompt_template = "The student answered: {}. The correct answer is {}. If the student answer is correct, please say 'Correct [TERMINATE]'. Otherwise, if the student answer is incorrect, please provide feedback to the student. The feedback should be specific and actionable."
    true_answer = info

    response = llm(
              messages = [{"role": "system", "content": system_prompt},
                          {"role": "user", "content": user_prompt_template.format(student_answer, true_answer)}]
        )

    response = response.choices[0].message.content
    score = 1 if 'Correct [TERMINATE]' in response else 0
    return score, response



class Logger:
    def log(self, message, color=None, **kwargs):
        print_color(message, color=color)



def main():
    # set seed
    seed = 42
    num_epochs = 1
    batch_size = 1
    eval_frequency = 1
    teacher_model = "gpt-4o-mini_2024-07-18"
    student_model = "gpt-35-turbo_1106"

    np.random.seed(seed)

    train_dataset = datasets.load_dataset('openai/gsm8k', 'main')['train'][:10]  # NOTE for now, we train on a smaller portion
    train_dataset = dict(inputs=train_dataset['question'], infos=train_dataset['answer'])
    test_dataset = train_dataset # NOTE for now, we just look at training error


    train(agent=Student(llm=AutoGenLLM(filter_dict={"model": ["gpt-35-turbo_1106"]})),
          teacher=lambda *args, **kwargs : teacher(model=teacher_model, *args, **kwargs),
          train_dataset=train_dataset,
          num_epochs=num_epochs,
          logger=Logger(),
          batch_size=batch_size,
          test_dataset=test_dataset,
          eval_frequency=eval_frequency
    )


if __name__ == "__main__":
    main()