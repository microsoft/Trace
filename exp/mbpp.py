import autogen
from opto.trace.nodes import node, GRAPH, ParameterNode
from opto.optimizers import OptoPrime, OPRO
from datasets import load_dataset
from textwrap import dedent
from opto.trace.bundle import bundle
from opto.trace.modules import model
from opto.trace.errors import ExecutionError
from opto.trace.nodes import ExceptionNode
from typing import List
from dataclasses import dataclass, field
import re
from tqdm import tqdm
import wandb
from datasets import load_dataset
from big_bench_hard import LLMCallable

@dataclass
class MBPPConfig:
    train: bool = True
    cot: bool = False
    load_ckpt: str = ""
    save_path: str = "."


def eval_metric(true, prediction, tests):
    # TODO: Change
    breakpoint()
    # use eval() method to evaluate expressions
    def eval_test(test):
        return eval(test)
    # check if the prediction is correct
    if all([eval_test(test) for test in tests]):
        return True
    return False
    

@model
class Generate(LLMCallable):
    # TODO: regulate LLM output to a certain format or let it learn
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
        answer = response.split("Answer:")[1].strip().split("```python\n")[1].split("\n```")[0]
        return answer

    @bundle(trainable=True, catch_execution_error=True, allow_external_dependencies=True)
    def create_prompt(self, prompt_template, question):
        return prompt_template.format(question)

    @bundle(trainable=True, catch_execution_error=True, allow_external_dependencies=True)
    def program(self, var1, var2=None, var3=None, var4=None):
        return var1

    def forward(self, question):
        user_prompt = self.create_prompt(self.prompt_template, question)
        response = self.call_llm(user_prompt)
        answer = self.extract_answer(self.prompt_template, question, response)
        return answer
    

@model
class GenerateCoT(LLMCallable):
    def __init__(self):
        super().__init__()

        self.demos = []
        self.prompt_template = dedent("""
        Given the fields `question`, produce the fields `answer`.

        ---

        Follow the following format.

        Question: question
        Reasoning: Let's think step by step in order to produce the answer. We ...
        Answer: answer

        ---
        Question: {}
        """)

        self.prompt_template = ParameterNode(self.prompt_template, trainable=True,
                                             description="[ParameterNode] This is the Prompt Template to the LLM. " + \
                                                         "Need to include information about what the format of answers LLM should output. " + \
                                                         "They can be (A)/(B), a number like 8, or a string, or Yes/No.")
    
def learn_generate(dp, optimizer, examples, val_examples, save_dir):
    cum_reward = 0
    epochs = 1

    val_perfs = {}
    # convert test cases to assertions
    for epoch in range(epochs):
        for step, example in enumerate(tqdm(examples)):
            GRAPH.clear()
            question = example['text']
            answer = example['code']
            test_cases = example['test_list']
            try:
                breakpoint()
                response = dp.forward(question)
                correctness, unsatisfied_tests = eval_metric(response, answer, test_cases)
                feedback = "The answer is correct! No need to change anything." if correctness else f"The answer is wrong. We expect the output of your answer to satisfy tests \"{unsatisfied_tests.join(',')}\". Please modify the program to produce the right answer."
                no_error = True
            except Exception as e:
                # load in the previous best checkpoint, and try to optimize from that again
                # an error recovery mode (similar to MCTS!?)
                if len(val_perfs) > 0:
                    breakpoint()
                    best_checkpoint = max(val_perfs, key=val_perfs.get)
                    dp.load(best_checkpoint)
                    try:
                        response = dp.forward(question)
                        correctness, unsatisfied_tests = eval_metric(response.data, answer, test_cases)
                        feedback = "The answer is correct! No need to change anything." if correctness else f"The answer is wrong. We expect the output of your answer to satisfy tests \"{unsatisfied_tests.join(',')}\". Please modify the program to produce the right answer."
                        no_error = True
                    except:
                        response = e.exception_node
                        feedback = response.data
                        correctness = False
                        no_error = False
                else:
                    response = e.exception_node
                    feedback = response.data
                    correctness = False
                    no_error = False

            print(question)
            print("Expected answer:", answer)
            print("Answer:", response.data)

            cum_reward += correctness
            checkpoint_name = f"{save_dir}/epoch_{epoch}_step_{step}.pkl"

            # if we can handle the case, no need to optimize
            if correctness:
                # evaluate on val examples
                try:
                    val_perf, _ = evaluate_dp(dp, val_examples)
                    val_perfs[checkpoint_name] = val_perf
                    dp.save(checkpoint_name)
                except:
                    pass

                continue

            # if val_perf is completely empty and there is no immediate error, we save two checkpoints
            if no_error and len(val_perfs) < 2:
                try:
                    val_perf, _ = evaluate_dp(dp, val_examples)
                    val_perfs[checkpoint_name] = val_perf
                    dp.save(checkpoint_name)
                except:
                    pass

            optimizer.zero_feedback()
            optimizer.backward(response, feedback)

            print(f"output={response.data}, feedback={feedback}, variables=\n")  # logging
            for p in optimizer.parameters:
                print(p.name, p.data)
            optimizer.step(verbose=False)
    # in the end, we select the best checkpoint on validation set
    # by here we have at least one checkpoint
    best_checkpoint = max(val_perfs, key=val_perfs.get)
    print(f"Best checkpoint: {best_checkpoint}", f"Val performance: {val_perfs[best_checkpoint]}")
    dp.load(best_checkpoint)

    checkpoint_name = f"{save_dir}/best_ckpt.pkl"
    dp.save(checkpoint_name)

    print(f"Total reward: {cum_reward}")
    return dp, cum_reward


def evaluate_dp(dp, examples):
    rewards = 0
    responses = []
    for example in tqdm(examples):
        try:
            response = dp.forward(example["text"])
            responses.append(response.data)
            correctness, _ = eval_metric(example["code"], response.data, example["test_list"])
        except:
            correctness = False
            responses.append(None)

        rewards += correctness
    return rewards / len(examples), responses


def mbpp_generation(config: MBPPConfig, debug: bool = False, wandb_enabled: bool = False, optimizer_name: str = 'opto'):
    save_name = f"./output/"
    ckpt_save_name = f"./output/mbpp"

    if config.train:
        save_name += "trained_"
        ckpt_save_name += "_train"
    if config.cot:
        save_name += "cot_"
        ckpt_save_name += "_cot"
    save_name += f".pkl"

    ds = load_dataset("google-research-datasets/mbpp", "full")
    trainset = ds['train']
    valset = ds['validation']
    test_set = ds['test']
    
    stats = {}

    if config.load_ckpt != "":
        dp = Generate()
        dp.load(config.load_ckpt)
    else:
        if not config.cot:
            dp = Generate()
        else:
            dp = GenerateCoT()
        
        if optimizer_name == 'opto':
            optimizer = OptoPrime(dp.parameters() + [dp.prompt_template],
                                    config_list=autogen.config_list_from_json("OAI_CONFIG_LIST"))
        elif optimizer_name == 'opro':
            optimizer = OPRO(dp.parameters() + [dp.prompt_template],
                                    config_list=autogen.config_list_from_json("OAI_CONFIG_LIST"))
        elif optimizer_name == 'synth':
            optimizer = OptoPrime(dp.parameters() + [dp.prompt_template],
                                    config_list=autogen.config_list_from_json("OAI_CONFIG_LIST"),
                                    synthesize=True,
                                    wandb_enabled=wandb_enabled and not debug
                                    )
        dp, rewards = learn_generate(dp, optimizer, trainset, valset, ckpt_save_name)
        stats['optimizer_log'] = optimizer.log
        stats['train_acc'] = rewards / len(trainset)

    