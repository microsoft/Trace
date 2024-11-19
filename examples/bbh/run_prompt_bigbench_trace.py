import autogen
from opto.trace.nodes import node, GRAPH, ParameterNode
import string
import random
import numpy as np
from textwrap import dedent
from opto.optimizers import OptoPrime
from datasets import load_dataset

from typing import List
import copy
from opto.trace.nodes import Node
from opto.trace import model, bundle, ExecutionError

import re
from tqdm import tqdm
import ray  # for parallelization


def eval_metric(true, prediction):
    # two types of answers:
    # (A)/(B) or "syndrome therefrom"/8/No/invalid
    matches = re.findall(r"\([A-Z]\)", true)
    if matches:
        pred = prediction
        matches = re.findall(r"\([A-Z]\)", pred)
        parsed_answer = matches[-1] if matches else ""
        return parsed_answer == true
    else:
        # substring match
        return prediction == true


class LLMCallable:
    def __init__(self, config_list=None, max_tokens=1024, verbose=False):
        if config_list is None:
            config_list = autogen.config_list_from_json("OAI_CONFIG_LIST")
        self.llm = autogen.OpenAIWrapper(config_list=config_list)
        self.max_tokens = max_tokens
        self.verbose = verbose

    @bundle(catch_execution_error=False)
    def call_llm(self, user_prompt):
        """
        Sends the constructed prompt (along with specified request) to an LLM.
        """
        system_prompt = "You are a helpful assistant.\n"
        if self.verbose not in (False, "output"):
            print("Prompt\n", system_prompt + user_prompt)

        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]

        try:
            response = self.llm.create(
                messages=messages,
                response_format={"type": "json_object"},
            )
        except Exception:
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
                                             description="[ParameterNode] This is the Prompt Template to the LLM. " + \
                                                         "Need to include information about what the format of answers LLM should output. " + \
                                                         "They can be (A)/(B), a number like 8, or a string, or Yes/No.")

    @bundle(trainable=True, catch_execution_error=True, allow_external_dependencies=True)
    def extract_answer(self, prompt_template, question, response):
        """
        Need to read in the response, which can contain additional thought, delibration and an answer.
        Use code to process the response and find where the answer is.
        Can use self.call_llm("Return the answer from this text: " + response) again to refine the answer if necessary.

        Args:
            prompt_template: The prompt that was used to query LLM to get the response
            question: Question has a text describing the question but also "Options"
            response: LLM returned a string response
                      Process it and return the answer in the exact format that the evaluator wants to see.
                      Be mindful of the type of answer you need to produce.
                      It can be (A)/(B), a number like 8, or a string, or Yes/No.
        """
        answer = response.split("Answer:")[1].strip()
        return answer

    @bundle(trainable=True, catch_execution_error=True, allow_external_dependencies=True)
    def create_prompt(self, prompt_template, question):
        """
        The function takes in a question and then add to the prompt for LLM to answer.
        Args:
            prompt_template: some guidance/hints/suggestions for LLM
            question: the question for the LLM to answer
        """
        return prompt_template.format(question)

    def forward(self, question):
        """
        question: text

        We read in a question and produces a response
        """
        user_prompt = self.create_prompt(self.prompt_template, question)
        response = self.call_llm(user_prompt)
        answer = self.extract_answer(self.prompt_template, question, response)
        return answer


@model
class PredictCoT(LLMCallable):
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

    @bundle(trainable=True, catch_execution_error=True, allow_external_dependencies=True)
    def extract_answer(self, prompt_template, question, response):
        """
        Need to read in the response, which can contain additional thought, delibration and an answer.
        Use code to process the response and find where the answer is.
        Can use self.call_llm("Return the answer from this text: " + response) again to refine the answer if necessary.

        Args:
            response: LLM returned a string response
                      Process it and return the answer in the exact format that the evaluator wants to see.
                      Be mindful of the type of answer you need to produce.
                      It can be (A)/(B), a number like 8, or a string, or Yes/No.
            question: Question has a text describing the question but also "Options"
        """
        answer = response.split("Answer:")[1].strip()
        return answer

    @bundle(trainable=True, catch_execution_error=True, allow_external_dependencies=True)
    def create_prompt(self, prompt_template, question):
        """
        The function takes in a question and then add to the prompt for LLM to answer.
        The prompt should instruct the LLM to reason, think.
        Args:
            prompt_template: some guidance/hints/suggestions for LLM
            question: the question for the LLM to answer
        """
        return prompt_template.format(question)

    def forward(self, question):
        """
        question: text

        We read in a question and produces a resposne
        """
        user_prompt = self.create_prompt(self.prompt_template, question)
        response = self.call_llm(user_prompt)
        answer = self.extract_answer(self.prompt_template, question, response)
        return answer


def learn_predict(dp, optimizer, examples, val_examples, task_name, save_dir):
    cum_reward = 0
    epochs = 1

    val_perfs = {}
    for epoch in range(epochs):
        for step, example in enumerate(tqdm(examples)):
            GRAPH.clear()
            # This is also online optimization
            # we have the opportunity to keep changing the function with each round of interaction
            try:
                response = dp.forward(example['question'])
                correctness = eval_metric(example['answer'], response.data)
                feedback = "The answer is correct! No need to change anything." if correctness else f"The answer is wrong. We expect the output of your answer to be \"{example['answer']}\". Please modify the prompt and relevant parts of the program to help LLM produce the right answer."
                no_error = True
            except ExecutionError as e:
                # load in the previous best checkpoint, and try to optimize from that again
                # an error recovery mode (error backtracking)
                if len(val_perfs) > 0:
                    best_checkpoint = max(val_perfs, key=val_perfs.get)
                    dp.load(best_checkpoint)
                    try:
                        response = dp.forward(example['question'])
                        correctness = eval_metric(example['answer'], response.data)
                        feedback = "The answer is correct! No need to change anything." if correctness else f"The answer is wrong. We expect the output of your answer to be \"{example['answer']}\". Please modify the prompt and relevant parts of the program to help LLM produce the right answer."
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

            print(example["question"])
            print("Expected answer:", example["answer"])
            print("Answer:", response.data)

            cum_reward += correctness
            checkpoint_name = f"{save_dir}/{task_name}/epoch_{epoch}_step_{step}.pkl"

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

    checkpoint_name = f"{save_dir}/{task_name}/best_ckpt.pkl"
    dp.save(checkpoint_name)

    print(f"Total reward: {cum_reward}")
    return dp, cum_reward


def evaluate_dp(dp, examples):
    rewards = 0
    responses = []
    for example in tqdm(examples):
        try:
            response = dp.forward(example["question"])
            responses.append(response.data)
            correctness = eval_metric(example["answer"], response.data)
        except:
            correctness = False
            responses.append(None)

        rewards += correctness
    return rewards / len(examples), responses


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--task", type=str, default="tracking_shuffled_objects_seven_objects")
    parser.add_argument("--task_start", type=int, default=-1, help="Start from a specific task")
    parser.add_argument("--task_end", type=int, default=-1, help="End at a specific task")
    parser.add_argument("--train", action="store_true", help="We add modules to add few-shot examples")
    parser.add_argument("--cot", action="store_true", help="Use and train CoT model instead")
    parser.add_argument("--save_path", type=str, default="results/bigbench")
    parser.add_argument("--load_ckpt", type=str, default="")
    args = parser.parse_args()

    import os

    if not os.path.exists(args.save_path):
        os.makedirs(args.save_path)

    tasks = ['tracking_shuffled_objects_seven_objects', 'salient_translation_error_detection',
             'tracking_shuffled_objects_three_objects', 'geometric_shapes', 'object_counting', 'word_sorting',
             'logical_deduction_five_objects', 'hyperbaton', 'sports_understanding', 'logical_deduction_seven_objects',
             'multistep_arithmetic_two', 'ruin_names', 'causal_judgement', 'logical_deduction_three_objects',
             'formal_fallacies', 'snarks', 'boolean_expressions', 'reasoning_about_colored_objects', 'dyck_languages',
             'navigate', 'disambiguation_qa', 'temporal_sequences', 'web_of_lies',
             'tracking_shuffled_objects_five_objects', 'penguins_in_a_table', 'movie_recommendation',
             'date_understanding']

    assert args.task in tasks, f"Task {args.task} not found in tasks."
    # note 0:27 covers all tasks
    run_tasks = tasks[args.task_start: args.task_end] if args.task_start != -1 and args.task_end != -1 else [args.task]

    for task in run_tasks:
        print(f"Running task {task}")

        save_name = f""
        ckpt_save_name = f"bigbench_trace_ckpt"

        if args.train:
            save_name += "trained_"
            ckpt_save_name += "_trained"
        if args.cot:
            save_name += "cot_"
            ckpt_save_name += "_cot"
        save_name += f"{task}.pkl"

        train = load_dataset("maveriq/bigbenchhard", task)["train"]
        examples = [{"question": r["input"], "answer": r["target"]} for r in train]

        print(f"There are {len(examples)} examples.")
        trainset = examples[:15]
        valset = examples[15:20]  # last 5 to validate the performance
        test_set = examples[20:]

        stats = {}

        if args.load_ckpt != "" and task == args.task:
            dp = Predict()
            dp.load(args.load_ckpt)
        else:
            if not args.cot:
                dp = Predict()
            else:
                dp = PredictCoT()

            optimizer = OptoPrime(dp.parameters() + [dp.prompt_template],
                                            config_list=autogen.config_list_from_json("OAI_CONFIG_LIST"))
            dp, rewards = learn_predict(dp, optimizer, trainset, valset, task, ckpt_save_name)
            stats['optimizer_log'] = optimizer.log
            stats['train_acc'] = rewards / len(trainset)

        stats["learned_prompt"] = dp.prompt_template.data
        stats["extract_answer"] = dp.parameters_dict()['extract_answer'].data
        stats["create_prompt"] = dp.parameters_dict()['create_prompt'].data

        print(stats["extract_answer"])

        val_acc, responses = evaluate_dp(dp, test_set)
        stats['val_acc'] = val_acc
        stats['val_responses'] = responses

        import pickle

        with open(f"{args.save_path}/{save_name}", "wb") as f:
            pickle.dump(stats, f)
