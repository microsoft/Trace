# This script applies Trace to optimize the workflow in TextGrad's solution_optimization.py.

from opto import trace
from opto.optimizers import OptoPrime, TextGrad

import re
import json
import argparse
import concurrent
from tqdm import tqdm
import numpy as np
from dotenv import load_dotenv

load_dotenv(override=True)
from statistics import multimode

import textgrad as tg
from textgrad.tasks import load_instance_task

import numpy as np
import random
import scipy

import time


def set_seed(seed):
    np.random.seed(seed)
    random.seed(seed)


def config():
    parser = argparse.ArgumentParser(description="Optimize a prompt for a task.")
    parser.add_argument("--algo", type=str, default="ttextgrad", help="The algorithm to use for optimization.")
    parser.add_argument("--task", type=str, default="MMLU_machine_learning", help="The task to evaluate the model on.")
    parser.add_argument("--engine", type=str, default="gpt-4o-2024-08-06", help="The API to use for evaluation.")
    parser.add_argument("--max_iterations", type=int, default=3,
                        help="The maximum number of iterations of test-time updates.")
    parser.add_argument("--num_threads", type=int, default=4, help="The number of threads to use for evaluation.")
    parser.add_argument("--trial", type=int, default=1, help="Trial is used to help run repeated experiments. WARNING: Need to manually remove cache.")
    return parser.parse_args()


class MajorityVoting:
    def __init__(self):
        pass

    def __call__(self, predictions):
        ANSWER_PATTERN_MULTICHOICE = r"(?i)Answer\s*:\s*([A-D])"
        pred_labels = []
        for pred in predictions:
            match = re.search(ANSWER_PATTERN_MULTICHOICE, pred.value)
            extracted_answer = match.group(1) if match else None
            pred_labels.append(extracted_answer)

        modes = multimode(pred_labels)
        return tg.Variable(f"Answer: {modes[0]}", role_description="Majority ensemble")


def get_zeroshot_answer(question):
    """Getting the zero-shot answer from an LLM without optimizing the response at test time."""
    # The system prompt is from: https://github.com/openai/simple-evals/blob/main/sampler/chat_completion_sampler.py
    STARTING_SYSTEM_PROMPT = (
            "You are ChatGPT, a large language model trained by OpenAI, based on the GPT-4 architecture."
            + "\nKnowledge cutoff: 2023-12\nCurrent date: 2024-04-01"
    )
    system_prompt = tg.Variable(STARTING_SYSTEM_PROMPT, requires_grad=False,
                                role_description="system prompt to the language model")
    model = tg.BlackboxLLM(llm_engine, system_prompt)
    response = model(tg.Variable(question, requires_grad=False, role_description="question to the language model"))
    return response


def run_test_time_training(sample):
    performance_history = []
    start = time.time()
    question, answer, test_time_objective, instance_eval_fn = sample
    zero_shot_response = get_zeroshot_answer(question)

    instance_var = tg.Variable(zero_shot_response.value,
                               requires_grad=True,
                               role_description="creative and precise solution and the prediction for the multiple choice question")

    # Evaluate the zero-shot response
    performance_history.append(int(instance_eval_fn(instance_var)))

    optimizer = tg.TextualGradientDescent(engine=llm_engine,
                                          parameters=[instance_var],
                                          constraints=[
                                              "The last line of your response should be of the following format: 'Answer: $LETTER' (without quotes) where LETTER is one of ABCD."])

    predictions = []
    predictions.append(tg.Variable(
        instance_var.value,
        role_description=instance_var.role_description
    ))

    # Start test time training
    for _ in range(args.max_iterations):

        # do an early step
        if performance_history[-1] == 1:
            break

        optimizer.zero_grad()
        # Compute the test time loss
        test_time_loss = test_time_objective(instance_var)
        test_time_loss.backward()
        optimizer.step()
        performance_history.append(instance_eval_fn(instance_var))
        predictions.append(tg.Variable(
            instance_var.value,
            role_description=instance_var.role_description
        ))

    now = time.time()
    ensembled_prediction = ensembler(predictions)
    performance_history.append(instance_eval_fn(ensembled_prediction))
    predictions.append(ensembled_prediction)
    return performance_history, predictions, question, answer, now - start


def get_test_time_objective(test_time_objective, instance_var):
    """Return a string that represents the objective during test time."""
    return test_time_objective(tg.Variable(instance_var.data, requires_grad=False,
                                           role_description="creative and precise solution and the prediction for the multiple choice question")).value


def instance_eval_fn_wrap(instance_eval_fn, instance_var):
    return instance_eval_fn(
        tg.Variable(instance_var.data, requires_grad=False, role_description=instance_var.description))


def llm_solution(system_prompt, question):
    system_prompt = tg.Variable(system_prompt, requires_grad=False,
                                role_description="system prompt to the language model")
    model = tg.BlackboxLLM(llm_engine, system_prompt)
    response = model(tg.Variable(question, requires_grad=False, role_description="question to the language model"))
    return response.value


def run_trace_test_time_training(sample):
    performance_history = []
    start = time.time()
    question, answer, test_time_objective, instance_eval_fn = sample

    STARTING_SYSTEM_PROMPT = (
            "You are ChatGPT, a large language model trained by OpenAI, based on the GPT-4 architecture."
            + "\nKnowledge cutoff: 2023-12\nCurrent date: 2024-04-01"
    )

    response = llm_solution(STARTING_SYSTEM_PROMPT, question)

    instance_var = trace.node(response, trainable=True, name='response',
                              description='Provide creative and precise solution and the prediction for the multiple choice question.',
                              constraint="The last line of your response should be of the following format: 'Answer: $LETTER' (without quotes) where LETTER is one of ABCD.")

    # Evaluate the zero-shot response
    # performance_history.append(int(instance_eval_fn(instance_var)))
    performance_history.append(int(instance_eval_fn_wrap(instance_eval_fn, instance_var)))

    if args.algo == "textgrad":
        # This runs Trace's TextGrad optimizer
        optimizer = TextGrad([instance_var], max_tokens=16383)
    else:  # This runs Trace's OptoPrime optimizer
        optimizer = OptoPrime([instance_var],
                              prompt_symbols={'variables': '#Parameters'},
                              max_tokens=16383)
    predictions = []
    predictions.append(tg.Variable(
        instance_var.data,
        role_description=instance_var.description
    ))

    # Start test time training
    for i in range(args.max_iterations):
        # do an early step
        if performance_history[-1] == 1:
            break

        optimizer.zero_feedback()
        test_time_loss = get_test_time_objective(test_time_objective, instance_var)

        @trace.bundle()
        def evaluate(question, response):
            """evaluation of the creative and precise solution and the prediction for the multiple choice question"""
            return test_time_loss

        response = evaluate(question, instance_var)

        response.backward("Improve correctness of the solution.")
        optimizer.step()  # verbose='output'
        performance_history.append(int(instance_eval_fn_wrap(instance_eval_fn, instance_var)))
        predictions.append(tg.Variable(
            instance_var.data,
            role_description=instance_var.description
        ))

    now = time.time()

    ensembled_prediction = ensembler(predictions)
    performance_history.append(instance_eval_fn(ensembled_prediction))
    predictions.append(ensembled_prediction)
    return performance_history, predictions, question, answer, now - start


def backfill(regret, maxlen):
    filled_regret = []
    for i in range(maxlen):
        if i < len(regret):
            filled_regret.append(regret[i])
        else:
            filled_regret.append(regret[-1])
    return filled_regret


args = config()
assert args.algo in ["textgrad", "trace", "ttextgrad"], "ttextgrad is Trace's implementation textgrad"

llm_engine = tg.get_engine(engine_name=args.engine)
tg.set_backward_engine(llm_engine, override=True)
test_set = load_instance_task(args.task, evaluation_api=llm_engine)
ensembler = MajorityVoting()

start = time.time()
all_solutions = {}
all_times = []
with concurrent.futures.ThreadPoolExecutor(max_workers=args.num_threads) as executor:
    futures = []
    for i, sample in enumerate(test_set):
        if args.algo in ["trace", 'textgrad']:
            future = executor.submit(run_trace_test_time_training, sample)
        else:
            future = executor.submit(run_test_time_training, sample)
        futures.append(future)

    all_history = []
    for future in tqdm(concurrent.futures.as_completed(futures), total=len(futures), position=0):
        performance_history, predictions, question, answer, time_spent = future.result()
        all_solutions[question] = {"predictions": [p.value for p in predictions], "answer": answer}
        all_solutions[question]["time"] = time_spent
        all_times.append(time_spent)
        all_history.append(performance_history)

now = time.time()

all_history = [backfill(history, 5) for history in all_history]
print(np.array(all_history).mean(axis=0))
all_results = {"task": args.task, "algo": args.algo,
               'mean': np.array(all_history).mean(axis=0).tolist(),
               'sem': scipy.stats.sem(np.array(all_history), axis=0).tolist(),
               'total time': now - start,
               'time (mean)': np.mean(all_times),
               'time (sem)': scipy.stats.sem(all_times)}

import json
import os

os.makedirs("textgrad_figures", exist_ok=True)

with open(f"./textgrad_figures/{args.task}_{args.algo}_trial_{args.trial}_results.json", "w") as f:
    json.dump(all_results, f)

with open(f"./textgrad_figures/{args.task}_{args.algo}_trial_{args.trial}_predictions.json", "w") as f:
    json.dump(all_solutions, f)

with open(f"./textgrad_figures/{args.task}_{args.algo}_trial_{args.trial}_all_history.json", "w") as f:
    json.dump(all_history, f)
