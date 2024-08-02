import llfbench as gym
import autogen
from opto.trace.nodes import node
from opto.trace.bundle import bundle
from opto.optimizers import OptoPrime, OPRO
from opto.trace.nodes import GRAPH
from llfbench.agents.llm import make_llm
from llfbench.agents.basic_ai_agent import BasicAIAgent
from textwrap import dedent
from dataclasses import dataclass, field
import wandb
import textgrad as tg
from textgrad.autograd.function import BackwardContext
import os

# Feedback type:
    # r: reward
    # hn: hindsight negative
    # hp: hindsight positive
    # fn: future negative
    # fp: future positive
@dataclass
class PoemConfig:
    teacher_model: str = "gpt-4-turbo"
    student_model: str = "gpt-4"
    initial_prompt: str = "Can you write me a poem?"
    feedback_type: list = field(default_factory=list)
    syllable_req: list = field(default_factory=list)
    ends_with: str = None
    context: int = 4

OAI_CONFIG_LIST = {
    'gpt-4': "OAI_CONFIG_LIST_4",
    'gpt-4-turbo': "OAI_CONFIG_LIST_4T",
}

def reformat(program_str: str):
    # remove empty lines and leading/trailing whitespaces
    return dedent(program_str).strip()

'''The hierarchical poem generation task'''
def trace_poem_generation(config: PoemConfig, debug: bool = False, wandb_enabled: bool = False, optimizer: str = 'opto'):
    
    env = gym.make('llf-poem-NumericalPlanningPoem-v0') 

    done = False
    cumulative_reward = 0.0

    system_prompt = BasicAIAgent.system_prompt
    llm = make_llm(config.student_model, system_prompt=system_prompt)
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
        agent.reset(prompt)
        observation, info = env.reset(options={'syllable_req': config.syllable_req, 'ends_with': config.ends_with, 'context': config.context})
        if debug: print(observation)
        return agent.act(observation['observation'], observation['feedback'])

    GRAPH.clear()
    # The prompt to be optimized
    prompt = node(config.initial_prompt, trainable=True)

    if optimizer == 'opto':
        optimizer = OptoPrime(
                                [prompt], 
                                config_list=autogen.config_list_from_json(OAI_CONFIG_LIST[config.teacher_model]),
                                memory_size=0,
                                )
        optimizer.objective = """You are a helpful assistant that wants to come up with instructions to a student to help
        them write a poem that is satisfactory to a teacher's assignment.
        The student's poem needs to satisfy the requirement of this assignment. 
        You should try to incorporate the feedback into your instruction to the student. 
        It should be made clear to the student what to change minimally to satisfy the assignment. """ + optimizer.default_objective
    elif optimizer == 'opro':
        optimizer = OPRO(
                            [prompt], 
                            config_list=autogen.config_list_from_json(OAI_CONFIG_LIST[config.teacher_model]),
                            )
        optimizer.objective = """You are a helpful assistant that wants to come up with instructions to a student to help
        them write a poem that is satisfactory to a teacher's assignment.
        The student's poem needs to satisfy the requirement of this assignment. 
        You should try to incorporate the feedback into your instruction to the student. 
        It should be made clear to the student what to change minimally to satisfy the assignment. """ + optimizer.default_objective

    if debug: print(f'Initial prompt: {prompt.data}')

    history = [[prompt.data]]
    info = {}
    while not 'success' in info or not info['success']:
        action = act(prompt)
        text = check_suffix(action)
        paras = check_paragraphs(action)
        lines = check_lines(text, paras)
        line_syllables = check_syllables(lines)
        observation, reward, terminated, truncated, info = step(line_syllables, lines)
        cumulative_reward += reward
        done = terminated or truncated
        feedback = observation['feedback'].data
        
        optimizer.zero_feedback()
        optimizer.backward(observation, feedback, visualize=True)
        history[-1].extend([action.data, feedback])

        if debug: print(f"prompt: {prompt.data}, output: {observation['observation'].data}, feedback: {feedback}")
        if not debug and wandb_enabled:
            wandb.log({'step': len(history), 'reward': float(reward.data), 'cumulative_reward': float(cumulative_reward.data), 'iterations': wandb.Table(data=history, columns=["prompt", "output", "feedback"])})
        optimizer.step(verbose=debug)
        history.append([prompt.data])

        
    print(f'Episode reward: {cumulative_reward}')
    print(f'Final prompt: {prompt.data}')
    print('History')
    for i, h in enumerate(history):
        print(f'{i}: {h}')


def textgrad_poem_generation(config: PoemConfig, debug: bool = False, wandb_enabled: bool = False):

    # set environment variable to use the correct config list
    config_list = autogen.config_list_from_json(OAI_CONFIG_LIST[config.teacher_model])[0]
    os.environ['OPENAI_API_KEY'] = config_list['api_key']
    os.environ['AZURE_OPENAI_API_KEY'] = config_list['api_key']
    os.environ['AZURE_OPENAI_API_BASE'] = config_list['base_url']
    os.environ['AZURE_OPENAI_API_VERSION'] = config_list['api_version']

    env = gym.make('llf-poem-NumericalPlanningPoem-v0') 

    done = False
    cumulative_reward = 0.0

    system_prompt = BasicAIAgent.system_prompt
    llm = make_llm(config.student_model, system_prompt=system_prompt)
    agent = BasicAIAgent(llm, verbose=True)

    tg.set_backward_engine('azure-' + config.teacher_model, override=True)

    # Step 1: Get an initial response from an LLM.
    prompt = tg.Variable(config.initial_prompt,
                        role_description="question to the LLM",
                        requires_grad=True)

    # Step 2: Define the loss function and the optimizer, just like in PyTorch!
    # Here, we don't have SGD, but we have TGD (Textual Gradient Descent)
    # that works with "textual gradients".
    optimizer = tg.TGD(parameters=[prompt])

    def loss_fn(observation):
        # Create the response variable
        response = tg.Variable(
            value=observation['feedback'],
            role_description="this is a feedback to the generated poem",
        )
        return response

    if debug: print(f'Initial prompt: {prompt}')

    history = [[prompt.value]]
    info = {}
    while not 'success' in info or not info['success']:
        agent.reset(prompt)
        observation, info = env.reset(options={'syllable_req': config.syllable_req, 'ends_with': config.ends_with, 'context': config.context})
        if debug: print(observation)
        action = agent.act(observation['observation'], observation['feedback'])
        text = env.check_suffix(action)
        paras = env.check_paragraphs(action)
        lines = env.check_lines(text, paras)
        line_syllables = env.check_syllables(lines)
        observation, reward, terminated, truncated, info = env.step([line_syllables, lines])
        cumulative_reward += reward
        done = terminated or truncated

        # Step 3: Do the loss computation, backward pass, and update the punchline.
        # Exact same syntax as PyTorch!
        loss = loss_fn(observation)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        history[-1].extend([action, observation['feedback']])

        if debug: print(f"prompt: {prompt.value}, output: {observation['observation']}, feedback: {observation['feedback']}")
        if not debug and wandb_enabled:
            wandb.log({'step': len(history), 'reward': float(reward), 'cumulative_reward': float(cumulative_reward), 'iterations': wandb.Table(data=history, columns=["prompt", "output", "feedback"])})
        history.append([prompt.value])
        
    print(f'Episode reward: {cumulative_reward}')
    print(f'Final prompt: {prompt.value}')
    print('History')
    for i, h in enumerate(history):
        print(f'{i}: {h}')