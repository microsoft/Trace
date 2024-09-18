import autogen
from opto.trace.nodes import node
from opto.optimizers import OptoPrime, OPRO
from opto.optimizers.optosynth import OptoSynth
from textwrap import dedent
from opto.trace.bundle import bundle
from dataclasses import dataclass
from tqdm import tqdm
import wandb
import random

import os
import coding_env
import time
import json


@dataclass
class MBPPConfig:
    train: bool = True
    cot: bool = False
    load_ckpt: str = ""
    save_path: str = "."
    n_optimization_steps: int = 100
    with_mistral: bool = True
    split: str = "test"


@bundle(trainable=True, allow_external_dependencies=False)
def verify(feedback, reward, code):
    ''' This is a function that verifies the correctness of the code. '''
    # if reward is 1, then the code is correct
    if reward == 1:
        return feedback, True
    # if reward is 0, then the feedback should be processed for the next iteration to correct the code
    
    return feedback, random.random() > 0.5
    

def mbpp_generation(config: MBPPConfig, debug: bool = False, wandb_enabled: bool = False, optimizer_name: str = 'opto'):

    env = coding_env.CodeRepairEnv(split=config.split, with_mistral=config.with_mistral)
    env = coding_env.ObservationWrapper(env)

    results = []
    cumulative_reward = 0
    successes = 0
    print("Optimization starts")
    for step, task_idx in tqdm(enumerate(coding_env.TEST_INDICES)): #  tqdm(enumerate(range(len(env.data))))
        prompt, _ = env.reset(options=dict(task_idx=task_idx))
        prompt = coding_env.SYSTEM_PROMPT + '\n' + prompt
        feedback = None
        text_with_cot = node(env.d['mistral_output'], trainable=True)

        if optimizer_name == 'opto':
            optimizer = OptoPrime(
                                    [text_with_cot], 
                                    config_list=autogen.config_list_from_json("OAI_CONFIG_LIST_INT"),
                                    memory_size=0,
                                    wandb_enabled=wandb_enabled and not debug
                                    )
        elif optimizer_name == 'opro':
            optimizer = OPRO(
                                [text_with_cot], 
                                config_list=autogen.config_list_from_json("OAI_CONFIG_LIST_INT"),
                                )
        elif optimizer_name == 'synth':
            optimizer = OptoPrime(
                                    [text_with_cot], 
                                    config_list=autogen.config_list_from_json("OAI_CONFIG_LIST_INT"),
                                    memory_size=0,
                                    synthesize=True,
                                    wandb_enabled=wandb_enabled and not debug
                                    )
        optimizer.objective = prompt

        for i in range(5):
            code = bundle()(coding_env.extract_code)(text_with_cot)
            print(f"Iter {i}")
            print(f"Code: {code.data}")
            next_obs, reward, term, trunc, info = env.step(code.data)
            feedback = coding_env.construct_feedback(reward, info, code.data)
            
            optimizer_suggestion = None
            try:
                optimizer.zero_feedback()
                optimizer.backward(code, feedback)
                optimizer.step(verbose=True)
                # optimizer.step(verbose='output')
                optimizer_suggestion = optimizer.suggestion
            except:
                pass
                # optimizer_suggestion is None is a way to check if the optimizer failed
            
            results.append({
                'timestamp': time.time(),
                'task_idx': task_idx,
                'iter_idx': i,
                'text_with_cot': text_with_cot.data,
                'code': code.data,
                'reward': reward,
                'trace_output': info['trace_output'],
                'feedback': feedback,
                'code': code.data,
                'inner_feedback': optimizer.inner_feedback,
            })
                
            if term:
                cumulative_reward += reward
                if reward == 1:
                    successes += 1
                break

        if wandb_enabled and not debug:
            logged_keys = [
                    'task_idx',
                    'iter_idx',
                    'reward',
                    'feedback',
                    'code',
                    'inner_feedback'
            ] if optimizer_name == 'synth' else [
                    'task_idx',
                    'iter_idx',
                    'reward',
                    'feedback',
                    'code',
            ]
            logged_values = [[
                result['task_idx'],
                result['iter_idx'],
                result['reward'],
                result['feedback'],
                result['code'],
                result['inner_feedback']] for result in results] if optimizer_name == 'synth' else [[
                result['task_idx'],
                result['iter_idx'],
                result['reward'],
                result['feedback'],
                result['code']] for result in results]
            wandb.log({"steps": step, "reward": reward, "successes": successes, "cumulative reward": cumulative_reward, "iterations": wandb.Table(data=logged_values, columns=logged_keys)})

        filename = f'output/test1_{optimizer_name}_repair_results/full_test.jsonl'
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w') as f:
            for result in results:
                f.write(json.dumps(result) + '\n')

