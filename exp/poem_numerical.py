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
env = gym.make('llf-poem-NumericalPlanningPoem-v0') # alternative: Tanka; more general: LineSyllableConstrainedPoem

done = False
cumulative_reward = 0.0

system_prompt = BasicAIAgent.system_prompt
llm = make_llm("gpt-35-turbo", system_prompt=system_prompt)
agent = BasicAIAgent(llm, verbose=True)

@bundle()
def check_suffix(text):
    "This is a function that checks the ending of a poem"
    return env.check_suffix(text)

@bundle()
def check_paragraphs(text):
    "This is a function that checks the number of paragraphs in a poem"
    return env.check_paragraphs(text)

@bundle()
def check_lines(text, paras):
    "This is a function that checks the number of lines in each paragraph of a poem"
    return env.check_lines(text, paras)

@bundle()
def check_syllables(tup):
    "This is a function that checks the number of syllables in each line of a poem"
    return env.check_syllables(tup)

@bundle()
def step(line_syllables, last_line):
    "This is a function that takes a step in the environment"
    observation, reward, terminated, truncated, info = env.step([line_syllables, last_line])
    return observation, reward, terminated, truncated, info

@bundle()
def act(prompt):
    "This is a function that asks the agent to act based on the prompt"
    # agent.reset(prompt)
    # observation, info = env.reset(options={'syllable_thres': [7,7,8], 'context': 0, 'feedback': 0})
    print(observation)
    return agent.act(observation['observation'], observation['feedback'])

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

agent.reset(prompt)
observation, info = env.reset(options={'syllable_req': [[10,6,5]], 'context': 5, 'feedback': 0, 'starts_with': "Once upon a time"})

" TODO: A single loop attempt for debugging purposes "
# action = act(prompt)
action = "This is a poem with one paragraph.\nThis is a second line.\nThis is a third line.\n"
text = check_suffix(action)
paras = check_paragraphs(action)
lines = check_lines(text, paras)
line_syllables, lines = check_syllables(lines)
observation, reward, terminated, truncated, info = step(line_syllables, lines)
cumulative_reward += reward
done = terminated or truncated

optimizer.zero_feedback()
optimizer.backward(observation, observation['feedback'], visualize=True)
print(f"prompt: {prompt.data}, output: {observation['observation']}, feedback: {observation['feedback']}")
optimizer.step(verbose=True)

print(f'Episode reward: {cumulative_reward}')
print(f'Final prompt: {prompt.data}')
