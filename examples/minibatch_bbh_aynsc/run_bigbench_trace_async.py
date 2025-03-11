import re
from opto.trace.nodes import node, GRAPH, ParameterNode
from textwrap import dedent
from opto.optimizers import OptoPrime
from datasets import load_dataset
from opto.trace import model, bundle
import opto.trace.operators as trace_ops
import numpy as np
from tqdm import tqdm
import autogen
import pickle
import os
from opto.trainer.algorithms.basic_algorithm import MinibatchAlgorithm, evaluate
from opto.trainer.guide import AutoGuide


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


class BigBenchGuide(AutoGuide):
    """
    Custom guide that uses the eval_metric function to evaluate responses
    and provide feedback for the BigBench tasks.
    """
    
    def __init__(self):
        super().__init__()
    
    def forward(self, task, response, info, **kwargs):
        """
        Evaluate the response using the eval_metric function.
        
        Args:
            task: The question
            response: The model's answer
            info: The correct answer
            
        Returns:
            score: 1.0 if correct, 0.0 if incorrect
            feedback: Feedback message
        """
        try:
            correctness = eval_metric(info, response)
            score = 1.0 if correctness else 0.0
            
            if correctness:
                feedback = "The answer is correct! No need to change anything."
            else:
                feedback = f"The answer is wrong. We expect the output of your answer to be \"{info}\". Please modify the prompt and relevant parts of the program to help LLM produce the right answer."
            
            return score, feedback
        except Exception as e:
            return 0.0, f"Error occurred: {str(e)}. Please fix the error and try again."
            
    def metric(self, task, response, info, **kwargs):
        """
        Evaluate the response and return just the score.
        
        Args:
            task: The question
            response: The model's answer
            info: The correct answer
            
        Returns:
            score: 1.0 if correct, 0.0 if incorrect
        """
        score, _ = self.forward(task, response, info, **kwargs)
        return score


@model
class Predict:
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

    @bundle(trainable=True, allow_external_dependencies=True)
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

    @bundle(trainable=True, allow_external_dependencies=True)
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
        response = trace_ops.call_llm(user_prompt)
        answer = self.extract_answer(self.prompt_template, question, response)
        return answer


@model
class PredictCoT:
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

    @bundle(trainable=True, allow_external_dependencies=True)
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

    @bundle(trainable=True, allow_external_dependencies=True)
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
        response = trace_ops.call_llm(user_prompt)
        answer = self.extract_answer(self.prompt_template, question, response)
        return answer


def learn_predict(dp, optimizer, examples, val_examples, task_name, save_dir):
    """
    Train the model using the MinibatchUpdate algorithm.
    
    Args:
        dp: The model to train
        optimizer: The optimizer to use
        examples: Training examples
        val_examples: Validation examples
        task_name: Name of the task
        save_dir: Directory to save checkpoints
        
    Returns:
        dp: The trained model
        rewards: The final validation accuracy
    """
    # Create the guide
    guide = BigBenchGuide()
    
    # Prepare the training dataset
    train_dataset = {
        'inputs': [ex['question'] for ex in examples],
        'infos': [ex['answer'] for ex in examples]
    }
    
    # Prepare the validation dataset
    val_dataset = {
        'inputs': [ex['question'] for ex in val_examples],
        'infos': [ex['answer'] for ex in val_examples]
    }
    
    # Create the MinibatchUpdate algorithm
    algorithm = MinibatchAlgorithm(
        agent=dp,
        optimizer=optimizer,
        num_threads=4  # Adjust as needed
    )
    
    # Train the model
    train_score, val_score = algorithm.train(
        guide=guide,
        train_dataset=train_dataset,
        test_dataset=val_dataset,
        num_epochs=1,
        batch_size=4,  # Process multiple examples at a time
        eval_frequency=1,  # Evaluate every 5 steps
        save_frequency=5,  # Save every 5 steps
        save_dir=save_dir,
        num_threads=4,
        verbose=True,
        min_score=None  # No minimum score required
    )
    
    return dp, val_score


def evaluate_dp(dp, examples):
    """
    Evaluate the model on a set of examples using MinibatchAlgorithm's evaluate method.
    
    Args:
        dp: The model to evaluate
        examples: The examples to evaluate on
        
    Returns:
        accuracy: The accuracy of the model
        responses: The responses of the model
    """
    
    # Create the guide
    guide = BigBenchGuide()
    
    # Prepare the evaluation dataset
    inputs = [ex['question'] for ex in examples]
    infos = [ex['answer'] for ex in examples]
    
    # Use the evaluate function from basic_algorithm.py
    scores = evaluate(
        agent=dp,
        guide=guide,
        inputs=inputs,
        infos=infos,
        min_score=0.0,  # Use 0.0 as the minimum score when an exception occurs
        num_threads=4,  # Adjust as needed
        description=f"Evaluating on {len(examples)} examples"  # Add descriptive message for the progress bar
    )
    
    # Calculate accuracy
    accuracy = np.mean(scores) if scores else 0.0
    
    # Collect responses for analysis
    responses = []
    for example in tqdm(examples):
        try:
            response = dp.forward(example["question"])
            responses.append(response.data)
        except Exception as e:
            print(f"Error during evaluation: {str(e)}")
            responses.append(None)
    
    return accuracy, responses


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

            optimizer = OptoPrime(dp.parameters() + [dp.prompt_template])
            dp, rewards = learn_predict(dp, optimizer, trainset, valset, task, ckpt_save_name)
            stats['optimizer_log'] = optimizer.log
            stats['train_acc'] = rewards

        stats["learned_prompt"] = dp.prompt_template.data
        stats["extract_answer"] = dp.parameters_dict()['extract_answer'].data
        stats["create_prompt"] = dp.parameters_dict()['create_prompt'].data

        print(stats["extract_answer"])

        val_acc, responses = evaluate_dp(dp, test_set)
        stats['val_acc'] = val_acc
        stats['val_responses'] = responses

        with open(f"{args.save_path}/{save_name}", "wb") as f:
            pickle.dump(stats, f)
