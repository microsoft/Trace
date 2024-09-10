import create_repair_dataset
import gymnasium as gym
import numpy as np
from textwrap import dedent
import re
import file_utils

TEST_INDICES = [   0,   79,  158,  237,  316,  395,  474,  553,  632,  711,  790,
        869,  948, 1027, 1106, 1185, 1264, 1343, 1422, 1501, 1580, 1659,
       1738, 1817, 1896, 1975, 2054, 2133, 2212, 2291, 2370, 2449, 2528,
       2607, 2686, 2765, 2844, 2923, 3002, 3081, 3160, 3239, 3318, 3397,
       3476, 3555, 3634, 3713, 3792, 3871, 3950]

# TEST_INDICES = [0, 158]


# TODO also bundle this
def extract_code(text):
    pattern = r'```(?:python)?(.*?)```'
    matches = re.findall(pattern, text, re.DOTALL)
    marked_code = [match.strip() for match in matches]
    if len(marked_code) > 0:
        return marked_code[0]

    # No code block was found. Maybe the text itself is code?
    # We test by using exec, which is not safe.
    _, timed_out, caught_exc = create_repair_dataset.run_function_with_timeout(exec, args=(text,), timeout=0.01)
    if caught_exc:
        # If it's not code, then return None. Failed to extract.
        return ""
    else:
        # If it doesn't fail from exception, then it is code so return it.
        return text


def construct_feedback(reward, info, code):
    feedback = dedent(f"""The reward is {reward} and the feedback is: {info['feedback']}.
""")
    if code == "":
        feedback += "Failed to extract code from the response. Please provide a code block in Markdown format.\n"

    if 'trace_output' not in info:
        return feedback

    # also compute next trace feedback
    trace_output = info['trace_output']
    for i, result in enumerate(trace_output):
        feedback += dedent(f"""\n## Trace {i}:
### Exception: {result['exc']}.
### Timeout: {result['timeout']}.
{result['trace']}
[End Trace {i}]
""")
    return feedback

class CodeRepairEnv(gym.Env):
    def __init__(self, split='train', with_mistral=False, path_override=None):
        if path_override is None:
            if with_mistral:
                self.data = file_utils.load_jsonl(f'notebooks/repair_data/{split}_repair_dataset_with_mistral.jsonl')
            else:
                self.data = file_utils.load_jsonl(f'notebooks/repair_data/{split}_repair_dataset.jsonl')
        else:
            self.data = file_utils.load_jsonl(path_override)
        print(f"Read repair dataset with {len(self.data)} tasks.")

    def run_code_against_tests(self, code):
        num_failed = 0
        outputs = []
        for test_case in self.test_list:
            output = create_repair_dataset.obtain_traced_program(
                code, test_case, self.test_setup_code)
            outputs.append(output)

            if output['exc'] or output['timeout']:
                num_failed += 1
        return num_failed, outputs

    def reset(self, seed=None, options=None):
        task_idx = options.get('task_idx', None) if options else None
        if task_idx is None:
            task_idx = np.random.randint(0, len(self.data))
        self.task_idx = task_idx
        self.d = self.data[self.task_idx]
        self.instruction = self.d['instruction']
        self.test_setup_code = self.d['test_setup_code']
        self.test_list = self.d['test_cases']
        self.buggy_code = self.d['buggy_code']
        self.internal_obs = {
            'instruction': self.instruction,
            'test_setup_code': self.test_setup_code,
            'test_list': self.test_list,
            'buggy_code': self.buggy_code,
            'trace_output': self.d['trace_results'],
        }
        # _, trace_output = self.run_code_against_tests(self.buggy_code)
        # self.internal_obs['trace_output'] = trace_output
        info = {'trace_output': self.internal_obs['trace_output']}

        return self.internal_obs, info


    def step(self, code):
        assert isinstance(code, str), f"expected str type but got {type(code)}"
        num_failed, trace_output = self.run_code_against_tests(code)
        failed_test = None
        for i, result in enumerate(trace_output):
            if result['exc'] or result['timeout']:
                failed_test = self.test_list[i]
                break
        done = num_failed == 0
        reward = (len(self.test_list) - num_failed) / len(self.test_list)
        self.internal_obs['buggy_code'] = code  # Replace buggy code for iterative debugging
        self.internal_obs['trace_output'] = trace_output
        feedback = f"Your code passed {len(self.test_list) - num_failed} out of {len(self.test_list)} test cases."
        feedback += f"The first test case you failed is: {failed_test}." if failed_test else ""
        info = {
            'feedback': feedback,
            'trace_output': trace_output,
        }
        return self.internal_obs, reward, done, done, info


# def default_prompt_cons(instruction, test_setup_code, test_list, buggy_code, trace_output):
#     problem_prompt = dedent("""
#         Coding Problem Prompt:
#         {instruction}

#         Test Cases:
#         {tests}

#         Buggy Code:
#         {buggy_code}
#     """)
#     test_str = '\n'.join(test_list)
#     if test_setup_code:
#         test_str = test_setup_code + '\n' + test_str
#     problem_prompt = problem_prompt.format(
#         instruction=instruction,
#         tests=test_str,
#         buggy_code=buggy_code.strip(),
#     )
#     if trace_output:
#         trace_template = dedent("""
#         Execution Traces of the Buggy Code:
#         {traces}
#         """)
#         trace_str = ""
#         for i, trace in enumerate(trace_output):
#             trace_str += f"*Trace {i}*:\n"
#             exception = 'TIMEOUT' if trace['timeout'] else trace['exc']
#             trace_str += f"EXCEPTION: {exception}\n"
#             trace_str += f"{trace['trace']}\n\n"

#         problem_prompt += trace_template.format(traces=trace_str)
#     return problem_prompt


def construct_code_repair_prompt(instruction, test_setup_code, test_list, buggy_code, trace_output=None):
    test_str = '\n'.join(test_list)
    if test_setup_code:
        test_str = test_setup_code + '\n' + test_str
    return dedent(f"""You will receive a coding problem with a buggy program.
Your goal is to generate a correct piece of code that passes all the test cases.
A test case will be shown to you if you fail to pass it.

# Coding Problem
{instruction.strip()}
[END OF PROMPT]

# Buggy Code
```\n{buggy_code.strip()}\n```
[END OF BUGGY CODE]
""").strip()


class ObservationWrapper(gym.ObservationWrapper):
    def __init__(self, env, prompt_cons = construct_code_repair_prompt):
        super().__init__(env)
        self.prompt_cons = prompt_cons

    def observation(self, obs):
        assert isinstance(obs, dict), f"expected dict type but got {type(obs)}"
        instruction = obs['instruction'].strip()
        test_setup_code = obs['test_setup_code']
        test_list = obs['test_list']
        buggy_code = obs['buggy_code'].strip()
        trace_output = obs.get('trace_output', [])
        return self.prompt_cons(instruction, test_setup_code, test_list, buggy_code, trace_output)

# Note: already using CoT
SYSTEM_PROMPT = """You are a coding assistant for Python programming tasks. You will receive a coding problem. Think step-by-step before writing the code. Provide code in Markdown format:\n```CODE```."""