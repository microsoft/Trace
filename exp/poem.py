import llfbench as gym
import autogen
from opto.trace.nodes import node, Node
from opto.trace.bundle import bundle
from opto.optimizers import FunctionOptimizer
from opto.trace.nodes import GRAPH
from llfbench.agents.llm import make_llm
from llfbench.agents.basic_ai_agent import BasicAIAgent
from llfbench.envs.poem.formal_poems import PoemUtil
import numpy as np
from textwrap import dedent
from typing import List

def reformat(program_str: str):
    # remove empty lines and leading/trailing whitespaces
    return dedent(program_str).strip()

# Environments in the benchmark are registered following
# the naming convention of llf-*

env = gym.make('llf-poem-HierarchicalLineSyllableConstrainedPoem-v0') # alternative: Tanka; more general: LineSyllableConstrainedPoem

done = False
cumulative_reward = 0.0

system_prompt = BasicAIAgent.system_prompt
llm = make_llm("gpt-35-turbo", system_prompt=system_prompt)
agent = BasicAIAgent(llm, verbose=True)

# The prompt to be optimized
prompt = node("Can you write me a poem?", trainable=True)
optimizer = FunctionOptimizer(
                            [prompt], 
                            config_list=autogen.config_list_from_json("OAI_CONFIG_LIST"),
                            )
optimizer.objective = """
                        You are a helpful assistant that wants to come up with instructions to a student to help
                        them write a poem that is satisfactory to a teacher's assignment.
                        The student's poem needs to satisfy the requirement of this assignment. 
                      """ + optimizer.default_objective

# First observation is acquired by resetting the environment
observation, info = env.reset()


@bundle(traceable_code=True, trainable=False)
def count_lines(text):
    lines = []
    for line in text.strip().split('\n'):
        if line == '':
            continue
        lines.append(line)
    return len(lines)


@bundle(trainable=False, traceable_code=True)
def count_line_syllables(text):
    util = PoemUtil()
    counts = []
    for i, line in enumerate(text.strip().split('\n')):
        if line == '':
            # this means it's just a segment break
            continue
        count = util.count_syllables(line)
        counts.append(count)
    return counts

@bundle(allow_external_dependencies=True, trainable=False, traceable_code=True)
def generate_poem(prompt, observation):

    agent.reset(prompt)
    
    # Observation is dict having 'observation', 'instruction', 'feedback'
    # Here we print the observation and ask the user for an action
    action = agent.act(observation['observation'], observation['feedback'])

    # Poem has a text action space, so TextWrapper is not needed
    # to parse a valid action from the input string

    # show the decision trace to the agent
    length = count_lines(action)
    syllables = count_line_syllables(action)

    # check each criterion separately
    checks = [0 for _ in range(len(syllables) + 1)]
    checks[0] = env.check_length(length)
    for i, s in enumerate(syllables):
        checks[i + 1] = env.check_syllables(i, s)

    observation, reward, terminated, truncated, info = env.step([checks, length, syllables])

    return observation, reward, terminated, truncated, info

history = [prompt.data]
info = {}
while not 'success' in info or not info['success']:
    observation, reward, terminated, truncated, info = generate_poem(prompt, observation)
    # reward is never revealed to the agent; only used for evaluation

    cumulative_reward += reward

    # terminated and truncated follow the same semantics as in Gymnasium

    done = terminated or truncated

    optimizer.zero_feedback()
    optimizer.backward(prompt, observation['feedback'], visualize=True)
    print(f"prompt: {prompt.data}, output: {observation['observation']}, feedback: {observation['feedback']}")
    optimizer.step(verbose=True)
    history.append(prompt.data)

    if 'success' in info and info['success']:
        print('SUCCESS!')
        break

print(f'Episode reward: {cumulative_reward}')
print(f'Final prompt: {prompt.data}')
print('History')
for i, h in enumerate(history):
    print(f'{i}: {h}')

