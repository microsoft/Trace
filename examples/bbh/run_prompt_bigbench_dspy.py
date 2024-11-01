import sys

import dspy
from datasets import load_dataset
from dspy.evaluate import Evaluate

from dspy.teleprompt import BootstrapFewShotWithRandomSearch, COPRO

import re
from tqdm import tqdm


def eval_metric(true, prediction, trace=None):
    # two types of answers:
    # (A)/(B) or "syndrome therefrom"/8/No/invalid
    prediction = prediction.answer
    true = true.answer
    matches = re.findall(r"\([A-Z]\)", true)
    if matches:
        pred = prediction
        matches = re.findall(r"\([A-Z]\)", pred)
        parsed_answer = matches[-1] if matches else ""
        return parsed_answer == true
    else:
        # substring match
        return prediction == true


class BasicQA(dspy.Module):
    def __init__(self):
        super().__init__()
        self.prog = dspy.Predict("question -> answer")

    def forward(self, question):
        return self.prog(question=question)


class CoT(dspy.Module):
    def __init__(self):
        super().__init__()
        self.prog = dspy.ChainOfThought("question -> answer")

    def forward(self, question):
        return self.prog(question=question)

def evaluate_dp(dp, examples):
    rewards = 0
    responses = []
    for example in tqdm(examples):
        try:
            response = dp.forward(example['question'])
            responses.append(response.data)
            correctness = eval_metric(example['answer'], response.data)
        except:
            correctness = False

        rewards += correctness
    return rewards / len(examples), responses


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--task", type=str, default="salient_translation_error_detection")
    parser.add_argument("--task_start", type=int, default=-1, help="Start from a specific task")
    parser.add_argument("--task_end", type=int, default=-1, help="End at a specific task")
    parser.add_argument("--train", action="store_true", help="Enabled few-shot optimization over training samples")
    parser.add_argument("--copro", action="store_true", help="Do prompt template optimization")
    parser.add_argument("--cot", action="store_true", help="Use and train CoT model instead")
    parser.add_argument("--save_path", type=str, default="results/bigbench_dspy")
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
             'date_understanding']  # 27 tasks

    rerun_tasks = []

    assert args.task in tasks, f"Task {args.task} not found in tasks."
    # note 0:27 covers all tasks
    run_tasks = tasks[args.task_start:args.task_end] if args.task_start != -1 and args.task_end != -1 else [args.task]

    for task in run_tasks:
        print(f"Running task {task}")

        save_name = f""
        if args.train:
            save_name += "trained_"
        if args.cot:
            save_name += "cot_"
        if args.copro:
            save_name += "copro_"

        save_name += f"{task}.pkl"

        if os.path.exists(f"{args.save_path}/{save_name}") and task not in rerun_tasks:
            print(f"Task {task} already finished and not in rerun task. Skipping.")
            continue

        ds = load_dataset("maveriq/bigbenchhard", task)["train"]
        examples = [dspy.Example({"question": r["input"], "answer": r["target"]}).with_inputs("question") for r in ds]

        print(f"There are {len(examples)} examples.")
        trainset = examples[:20]
        valset = examples[20:]

        stats = {}

        llm = dspy.OpenAI(model="gpt-4-turbo-2024-04-09", max_tokens=512)
        dspy.settings.configure(lm=llm)

        if args.cot:
            basic_qa = CoT()
        else:
            basic_qa = BasicQA()

        try:
            if args.train:
                config = dict(max_bootstrapped_demos=2, max_labeled_demos=4, num_candidate_programs=2, num_threads=6)

                teleprompter = BootstrapFewShotWithRandomSearch(metric=eval_metric, **config)
                # train on first 15, val on the next 5
                optimized_qa = teleprompter.compile(basic_qa, trainset=trainset[:15], valset=trainset[15:])
            elif args.copro:
                teleprompter = COPRO(metric=eval_metric)
                kwargs = dict(num_threads=3, display_progress=True,
                              display_table=10)  # Used in Evaluate class in the optimization process
                optimized_qa = teleprompter.compile(basic_qa, trainset=trainset, eval_kwargs=kwargs)

            evaluate = Evaluate(devset=valset, metric=eval_metric, num_threads=6, display_progress=True, display_table=10, return_outputs=True)
        except:
            continue

        if args.train or args.copro:
            print("Evaluating optimized model")
            val_acc, return_outputs = evaluate(optimized_qa)
        else:
            val_acc, return_outputs = evaluate(basic_qa)

        stats['train_acc'] = 0  # rewards / len(trainset)

        stats['val_acc'] = val_acc
        stats['val_responses'] = []
        for r in return_outputs:
            try:
                stats['val_responses'].append(r[1].answer)
            except:
                stats['val_responses'].append(None)

        import pickle

        save_name = f""
        if args.train:
            save_name += "trained_"
        if args.cot:
            save_name += "cot_"
        if args.copro:
            save_name += "copro_"

        save_name += f"{task}.pkl"
        with open(f"{args.save_path}/{save_name}", "wb") as f:
            pickle.dump(stats, f)
