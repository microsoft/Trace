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
def check_lines(tup):
    "This is a function that checks the correctness of lines of a poem"
    for i in range(5): 
        tup = env.check_syllables(i, tup)
    return tup

@bundle()
def act(prompt):
    "This is a function that asks the agent to act based on the prompt"
    agent.reset(prompt)
    observation, info = env.reset(options={'syllable_thres': [7,7,8], 'context': 0, 'feedback': 0})
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
    lines = check_length(action)
    lines = check_lines(lines)

    observation, reward, terminated, truncated, info = step(lines)
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
    