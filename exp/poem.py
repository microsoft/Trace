import llfbench as gym
import autogen
from opto.trace.nodes import node
from opto.trace.bundle import bundle
from opto.optimizers import FunctionOptimizer
from opto.trace.nodes import GRAPH
from llfbench.agents.llm import make_llm
from llfbench.agents.basic_ai_agent import BasicAIAgent
from textwrap import dedent
import numpy as np

def reformat(program_str: str):
    # remove empty lines and leading/trailing whitespaces
    return dedent(program_str).strip()

# The hierarchical poem generation task
env = gym.make('llf-poem-HierarchicalLineSyllableConstrainedPoem-v0') # alternative: Tanka; more general: LineSyllableConstrainedPoem

done = False
cumulative_reward = 0.0

system_prompt = BasicAIAgent.system_prompt
llm = make_llm("gpt-35-turbo", system_prompt=system_prompt)
agent = BasicAIAgent(llm, verbose=True)

# Basic (b), partial (p), and complete (c)
# INSTRUCTION_TYPES = ('b')        # ('b', 'p', 'c')

# Feedback type:
# n: none
# m: mixed
# a: all
# r: reward
# hn: hindsight negative
# hp: hindsight positive
# fn: future negative
# fp: future positive

@bundle()
def check_length(text):
    "This is a function that checks the number of lines in a poem"
    return env.check_length(text)


@bundle()
def check_first_line(tup):
    "This is a function that checks the number of syllables in the first line of a poem"
    if False in tup[1]:
        tup[1].append(np.random.randint(0, 2) == 0)
    else:
        tup[1].append(env.check_syllables(0, tup[0]))
    return tup


@bundle()
def check_second_line(tup):
    "This is a function that checks the number of syllables in the second line of a poem"
    if False in tup[1]:
        tup[1].append(np.random.randint(0, 2) == 0)
    else:
        tup[1].append(env.check_syllables(1, tup[0]))
    return tup


@bundle()
def check_third_line(tup):
    "This is a function that checks the number of syllables in the third line of a poem"
    if False in tup[1]:
        tup[1].append(np.random.randint(0, 2) == 0)
    else:
        tup[1].append(env.check_syllables(2, tup[0]))
    return tup


# @bundle()
# def check_line(tup, i):
#     "This is a function that checks the number of syllables in the ith line of a poem"
#     tup[1].append(env.check_syllables(i - 1, tup[0]))
#     return tup


@bundle()
def act(prompt):
    "This is a function that asks the agent to act based on the prompt"
    agent.reset(prompt)
    # TODO: need to fix - reset parameter not passing through the wrappers
    observation, info = env.reset()
    print(observation)
    return agent.act(observation['observation'], observation['feedback'])


@bundle()
def step(tup):
    "This is a function that takes a step in the environment"
    observation, reward, terminated, truncated, info = env.step(tup)
    return observation, reward, terminated, truncated, info


GRAPH.clear()
# The prompt to be optimized
prompt = node("Can you write me a poem?", trainable=True)

optimizer = FunctionOptimizer(
                            [prompt], 
                            config_list=autogen.config_list_from_json("OAI_CONFIG_LIST"),
                            )
optimizer.objective = """You are a helpful assistant that wants to come up with instructions to a student to help
them write a poem that is satisfactory to a teacher's assignment.
The student's poem needs to satisfy the requirement of this assignment. """ + optimizer.default_objective


history = [prompt.data]
info = {}
while not 'success' in info or not info['success']:
    action = act(prompt)
    check = check_length(action)
    check = check_first_line(check)
    check = check_second_line(check)
    check = check_third_line(check)

    observation, reward, terminated, truncated, info = step(check)
    cumulative_reward += reward
    done = terminated or truncated

    optimizer.zero_feedback()
    optimizer.backward(observation, observation['feedback'], visualize=True)
    print(f"prompt: {prompt.data}, output: {observation['observation']}, feedback: {observation['feedback']}")
    optimizer.step(verbose=True)
    history.append(prompt.data)

print(f'Episode reward: {cumulative_reward}')
print(f'Final prompt: {prompt.data}')
print('History')
for i, h in enumerate(history):
    print(f'{i}: {h}')
    