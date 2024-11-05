# This script applies Trace to optimize the workflow in TextGrad's prompt_optimization.py.

from opto import trace
from opto.optimizers import OptoPrime, TextGrad
import time

import argparse
import concurrent
from dotenv import load_dotenv
load_dotenv(override=True)

from tqdm import tqdm
import textgrad as tg
from textgrad.tasks import load_task

import numpy as np
import random

def set_seed(seed):
    np.random.seed(seed)
    random.seed(seed)

def config():
    parser = argparse.ArgumentParser(description="Optimize a prompt for a task.")
    parser.add_argument("--algo", type=str, default="textgrad", help="The algorithm to use for optimization.")
    parser.add_argument("--task", type=str, default="BBH_object_counting", help="The task to evaluate the model on.")
    parser.add_argument("--evaluation_engine", type=str, default="gpt-4o", help="The API to use for evaluation.")
    parser.add_argument("--test_engine", type=str, default="gpt-3.5-turbo-0125", help="The API to use for evaluation.")
    parser.add_argument("--batch_size", type=int, default=3, help="The batch size to use for training.")
    parser.add_argument("--max_epochs", type=int, default=3, help="The maximum number of epochs to train for.")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--run_validation", action="store_true", help="Whether to run validation or not.")
    parser.add_argument("--do_not_run_larger_model", action="store_true", help="Whether to run the larger model or not.")
    parser.add_argument("--num_threads", type=int, default=32, help="The number of threads to use for evaluation.")
    return parser.parse_args()

args = config()

def eval_sample(item, eval_fn, model):
    x, y = item
    x = tg.Variable(x, requires_grad=False, role_description="query to the language model")
    if  np.issubdtype(type(y), np.integer):
        y = int(y)
    y = tg.Variable(y, requires_grad=False, role_description="correct answer for the query")
    response = model(x)
    try:
        eval_output_variable = eval_fn(inputs=dict(prediction=response, ground_truth_answer=y))
        return int(eval_output_variable.value)
    except:
        eval_output_variable = eval_fn([x, y, response])
        eval_output_parsed = eval_fn.parse_output(eval_output_variable)
        return int(eval_output_parsed)

def eval_dataset(test_set, eval_fn, model, max_samples: int=None):
    if max_samples is None:
        max_samples = len(test_set)
    accuracy_list = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        futures = []
        for _, sample in enumerate(test_set):

            future = executor.submit(eval_sample, sample, eval_fn, model)
            futures.append(future)
            if len(futures) >= max_samples:
                break
        tqdm_loader = tqdm(concurrent.futures.as_completed(futures), total=len(futures), position=0)
        for future in tqdm_loader:
            acc_item = future.result()
            accuracy_list.append(acc_item)
            tqdm_loader.set_description(f"Accuracy: {np.mean(accuracy_list)}")
    return accuracy_list

def run_validation_revert(system_prompt: tg.Variable, results, model, eval_fn, val_set):
    val_performance = np.mean(eval_dataset(val_set, eval_fn, model))
    previous_performance = np.mean(results["validation_acc"][-1])
    print("val_performance: ", val_performance)
    print("previous_performance: ", previous_performance)
    previous_prompt = results["prompt"][-1]

    if val_performance < previous_performance:
        print(f"rejected prompt: {system_prompt.value}")
        system_prompt.set_value(previous_prompt)
        val_performance = previous_performance

    results["validation_acc"].append(val_performance)


set_seed(args.seed)
llm_api_eval = tg.get_engine(engine_name=args.evaluation_engine)
llm_api_test = tg.get_engine(engine_name=args.test_engine)
# tg.set_backward_engine(llm_api_eval, override=True)

# Load the data and the evaluation function
train_set, val_set, test_set, eval_fn = load_task(args.task, evaluation_api=llm_api_eval)
print("Train/Val/Test Set Lengths: ", len(train_set), len(val_set), len(test_set))
STARTING_SYSTEM_PROMPT = train_set.get_task_description()

train_loader = tg.tasks.DataLoader(train_set, batch_size=args.batch_size, shuffle=True)
print(STARTING_SYSTEM_PROMPT)

# Testing the 0-shot performance of the evaluation engine
system_prompt = trace.node(STARTING_SYSTEM_PROMPT,
                           trainable=True,
                           constraint="structured system prompt to a somewhat capable language model that specifies the behavior and strategies for the QA task")

# model_evaluation = tg.BlackboxLLM(llm_api_eval, system_prompt)
def model_evaluation(x):
    return tg.BlackboxLLM(llm_api_eval, system_prompt.data)(x)

if not args.do_not_run_larger_model:
    reference = np.mean(eval_dataset(test_set, eval_fn, model_evaluation))


def model(x):
    return tg.BlackboxLLM(llm_api_test, system_prompt.data)(x)

if args.algo == "textgrad":
    # This runs Trace's TextGrad optimizer
    optimizer = TextGrad([system_prompt])
else:  # This runs Trace's OptoPrime optimizer
    optimizer = OptoPrime([system_prompt], prompt_symbols={'variables':'#Parameters'})

results = {"test_acc": [], "prompt": [], "validation_acc": []}
results["test_acc"].append(eval_dataset(test_set, eval_fn, model))
results["validation_acc"].append(eval_dataset(val_set, eval_fn, model))
results["prompt"].append(system_prompt.data)


# We define Trace operations by wrapping the original TextGrad codes

@trace.bundle()
def query(system_prompt, *inputs):
    """ Query the language model with the system prompt and the input query """
    return tg.BlackboxLLM(llm_api_test, system_prompt)(*inputs)

@trace.bundle()
def eval_response(response, ground_truth_answer):
    """ Evaluate the response of the language model with respect to the ground truth answer. 1 means correct, 0 means incorrect """
    try:
        eval_output_variable = eval_fn(inputs=dict(prediction=response, ground_truth_answer=ground_truth_answer))
    except:
        eval_output_variable = eval_fn([x, ground_truth_answer, response])
    return eval_output_variable

@trace.bundle()
def concat(*items):
    """ Concatenate the items into a single string """
    output = ''
    for i, item in enumerate(items):
        output += f'{[i]}: {item}\n\n'
    return output

start_time = time.time()

for epoch in range(args.max_epochs):
    for steps, (batch_x, batch_y) in enumerate((pbar := tqdm(train_loader, position=0))):

        success = False
        while not success:
            try:
                pbar.set_description(f"Training step {steps}. Epoch {epoch}")
                optimizer.zero_feedback()
                feedbacks = []
                for (x, y) in zip(batch_x, batch_y):
                    x = tg.Variable(x, requires_grad=False, role_description="query to the language model")
                    if  np.issubdtype(type(y), np.integer):
                        y = int(y)
                    y = tg.Variable(y, requires_grad=False, role_description="correct answer for the query")
                    # trace these operations
                    response =  query(system_prompt, x)  # node
                    eval_output_variable = eval_response(response, y)  # node
                    feedbacks.append(eval_output_variable) # list of nodes

                target = concat(*feedbacks) # node
                target.backward("Improve correctness.")
                optimizer.step(verbose='output')

                if args.run_validation:
                    # to implement the run_validation_revert in TextGrad
                    tg_system_prompt =tg.Variable(system_prompt.data,
                                                requires_grad=True,
                                                role_description="structured system prompt to a somewhat capable language model that specifies the behavior and strategies for the QA task")
                    run_validation_revert(tg_system_prompt, results, model, eval_fn, val_set)
                    system_prompt._data = tg_system_prompt.value

                print("sys prompt: ", system_prompt.data)
                test_acc = eval_dataset(test_set, eval_fn, model)
                results["test_acc"].append(test_acc)
                results["prompt"].append(system_prompt.data)

                # Log intermediate results
                time_taken = time.time() - start_time
                results["time_taken"] = time_taken
                import json
                import os
                os.makedirs("textgrad_figures", exist_ok=True)
                with open(f"./textgrad_figures/_tmp_results_{args.task}_{args.test_engine}_{args.algo}_{args.seed}.json", "w") as f:
                    json.dump(results, f)

                success = True
            except Exception as e:
                print("Exception: ", e)
                input("Press Enter to continue...")
                success = False

        if steps == 3:
            break



time_taken = time.time() - start_time
results["time_taken"] = time_taken

# Also dump the final results
import json
import os
os.makedirs("textgrad_figures", exist_ok=True)
with open(f"./textgrad_figures/results_{args.task}_{args.test_engine}_{args.algo}_{args.seed}.json", "w") as f:
    json.dump(results, f)