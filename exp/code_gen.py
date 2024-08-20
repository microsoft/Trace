import autogen
from opto.trace.nodes import node, GRAPH, ParameterNode
from opto.optimizers import OptoPrime
from datasets import load_dataset
from textwrap import dedent
from opto.trace.bundle import bundle
from opto.trace.modules import model
from opto.trace.errors import ExecutionError
from opto.trace.nodes import ExceptionNode
from typing import List
import re

def eval_metric(true, prediction):
    matches = re.findall(r"\([A-Z]\)", true)
    if matches:
        pred = prediction
        matches = re.findall(r"\([A-Z]\)", pred)
        parsed_answer = matches[-1] if matches else ""
        return parsed_answer == true
    else:
        return prediction == true
    
class LLMCallable:
    def __init__(self, config_list=None, max_tokens=1024, verbose=False):
        if config_list is None:
            config_list = autogen.config_list_from_json("OAI_CONFIG_LIST")
        self.llm = autogen.OpenAIWrapper(config_list=config_list)
        self.max_tokens = max_tokens
        self.verbose = verbose

    @bundle(catch_execution_error=True)
    def call_llm(self, user_prompt):
        system_prompt = "You are a helpful assistant.\n"
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]
        response = self.llm.create(messages=messages, max_tokens=self.max_tokens)
        response = response.choices[0].message.content

        if self.verbose:
            print("LLM response:\n", response)
        return response
    
@model
class Predict(LLMCallable):
    def __init__(self):
        super().__init__()

        self.demos = []
        self.prompt_template = dedent(
            """
        Given the fields `question`, produce the fields `answer`.

        ---

        Follow the following format.

        Question: 
        Answer: 

        ---
        Question: {}
        Answer:
        """
        )
        self.prompt_template = ParameterNode(self.prompt_template, trainable=True,
                                             description="This is the Prompt Template to the LLM. " + \
                                                         "Need to include information about what the format of answers LLM should output. " + \
                                                         "They can be (A)/(B), a number like 8, or a string, or Yes/No.")

    @bundle(trainable=True, catch_execution_error=True, allow_external_dependencies=True)
    def extract_answer(self, prompt_template, question, response):
        answer = response.split("Answer:")[1].strip()
        return answer

    @bundle(trainable=True, catch_execution_error=True, allow_external_dependencies=True)
    def create_prompt(self, prompt_template, question):
        return prompt_template.format(question)

    def forward(self, question):
        user_prompt = self.create_prompt(self.prompt_template, question)
        response = self.call_llm(user_prompt)
        answer = self.extract_answer(self.prompt_template, question, response)
        return answer
    
def learn_predict(dp, optimizer, examples):
    for step, example in enumerate(examples):
        GRAPH.clear()
        try:
            response = dp.forward(example['question'])
            correctness = eval_metric(example['answer'], response)
            feedback = "The answer is correct! No need to change anything." if correctness else f"The answer is wrong. We expect the output of your answer to be \"{example['answer']}\". Please modify the prompt and relevant parts of the program to help LLM produce the right answer."
        except ExecutionError as e:
            response = e.exception_node
            feedback = response.data
            correctness = False
            
        print("Question:", example["question"])
        print("Expected answer:", example["answer"])
        print("Answer:", response)

        if correctness:
            continue

        optimizer.zero_feedback()
        optimizer.backward(response, feedback)

        print(f"Output: {response}, Feedback: {feedback}, Variables:")  # Logging
        for p in optimizer.parameters:
            print(p.name, p.data)
        optimizer.step(verbose=True)

task = "sports_understanding"
train = load_dataset("maveriq/bigbenchhard", task)["train"]
examples = [{"question": r["input"], "answer": r["target"]} for r in train]

dp = Predict()
optimizer = OptoPrime(dp.parameters(),
                                    config_list=autogen.config_list_from_json("OAI_CONFIG_LIST"))

print("Training on a few examples:")
learn_predict(dp, optimizer, examples[:5])
    
print("\nTesting on new examples:")
for example in examples[5:6]:
    try:
        response = dp.forward(example["question"])
        print("Question:", example["question"])
        print("Expected answer:", example["answer"])
        print("Answer:", response.data)
    except ExecutionError as e:
        print("Question:", example["question"])
        print("Expected answer:", example["answer"])
        print("Error:", e.exception_node.data)

