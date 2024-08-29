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
import sys, importlib.util

@dataclass
class MBPPConfig:
    train: bool = True
    cot: bool = False
    load_ckpt: str = ""
    save_path: str = "."
    n_optimization_steps: int = 100
    

def mbpp_generation(config: MBPPConfig, debug: bool = False, wandb_enabled: bool = False, optimizer_name: str = 'opto'):
    ds = load_dataset("google-research-datasets/mbpp", "full")
    trainset = ds['train']
    # valset = ds['validation']
    # test_set = ds['test']

    global program
    @bundle(trainable=True, catch_execution_error=True, allow_external_dependencies=True)
    def program(var1, var2=None, var3=None, var4=None):
        """
        A function that processes inputs into an output.
        """
        return var1


    @bundle(trainable=False, catch_execution_error=True, allow_external_dependencies=True)
    def evaluate_test(program, tests):
        """
        A function that runs a test on the program. 
        """
        func_name = tests[0].replace('assert ', '').split('(')[0]
        tests = [test.replace(func_name, 'program').replace('assert ', '') for test in tests]
        # use eval() method to evaluate expressions
        def eval_test(test):
            return eval(test)
        for test in tests:
            try:
                if not eval_test(test):
                    return False, test, None
            except ExecutionError as e:
                print(e.exception_node.data)
                return False, test, e.exception_node
        return True, None, None

    successes = []
    returns = []
    print("Optimization starts")
    for i, example in enumerate(trainset):
        if i == 0: continue
        print("Optimization starts for example", i)

        GRAPH.clear()
        if optimizer_name == 'opto':
            optimizer = OptoPrime(
                                    program.parameters(), 
                                    config_list=autogen.config_list_from_json("OAI_CONFIG_LIST_INT"),
                                    memory_size=0,
                                    )
        elif optimizer_name == 'opro':
            optimizer = OPRO(
                                program.parameters(), 
                                config_list=autogen.config_list_from_json("OAI_CONFIG_LIST_INT"),
                                )
        elif optimizer_name == 'synth':
            optimizer = OptoPrime(
                                    program.parameters(), 
                                    config_list=autogen.config_list_from_json("OAI_CONFIG_LIST_INT"),
                                    memory_size=0,
                                    synthesize=True,
                                    wandb_enabled=wandb_enabled and not debug
                                    )
            
        
        question = example["text"]
        answer = example["code"]
        test_cases = example["test_list"]
        steps = 0
        
        optimizer.objective = question + optimizer.default_objective
        for j in range(config.n_optimization_steps):
            optimizer.zero_feedback()
            # TODO: hide test cases from the optimizer
            correctness, unsatisfied_test, error = evaluate_test(program, test_cases)

            if error:
                feedback = error.data
            elif correctness:
                feedback = "The generated program is correct! No need to change anything."
            else:
                feedback = f"The answer is wrong. We expect your generated program to satisfy the test \"{unsatisfied_test.data}\". Please modify the program to produce the right answer that passes the test."
            optimizer.backward(correctness, feedback)
            optimizer.step(verbose=debug)

            print(f"Step: {steps} code: \n{program.parameters()[0].data}\n feedback: {feedback}")
            if correctness:
                successes.append(i)
                break
            steps += 1
        returns.append(-1 * steps)
        successes.append(correctness)
        if wandb_enabled and not debug:
            wandb.log({"steps": steps, "success": correctness, "success rate": sum(successes) / len(successes)})
        print(f"Example {i} done in {steps} steps")

    print(f"Optimization finished. Success rate: {sum(successes)}/{len(successes)}")
    print(f"Average steps: {- sum(returns) / len(returns)}")
    print(f"Max steps: {- min(returns)}")
    print(f"Min steps: {- max(returns)}")
    if wandb_enabled and not debug:
        wandb.finish()
    return program