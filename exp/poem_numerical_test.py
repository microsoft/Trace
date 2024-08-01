import autogen
from opto.trace.nodes import node
from opto.trace.bundle import bundle
from opto.optimizers import OptoPrime
from opto.trace.nodes import GRAPH

'''The hierarchical poem generation task'''
def poem_generation(debug: bool = False):

    @bundle()
    def check_poem(text):
        "This is a test function that checks the requirements of a poem"
        return len(text), text.count('\n')

    @bundle()
    def act(prompt):
        "This is a function that asks the agent to act based on the prompt"
        return "Hello"

    GRAPH.clear()
    # The prompt to be optimized
    prompt = node("Write a poem for me.", trainable=True)

    optimizer = OptoPrime(
                            [prompt], 
                            config_list=autogen.config_list_from_json("OAI_CONFIG_LIST"),
                            )
    optimizer.objective = """You are a helpful assistant that wants to come up with instructions to a student to help
    them write a poem that is satisfactory to a teacher's assignment.
    The student's poem needs to satisfy the requirement of this assignment. 
    You should try to incorporate the feedback into your instruction to the student. 
    It should be made clear to the student what to change minimally to satisfy the assignment. """ + optimizer.default_objective

    print(f'Initial prompt: {prompt.data}')

    info = {}
    while not 'success' in info or not info['success']:
        action = act(prompt)
        text_len, text_nl = check_poem(action)
        reward = text_len
        cumulative_reward += reward
        
    print(f'Episode reward: {cumulative_reward}')
    print(f'Final prompt: {prompt.data}')


if __name__ == "__main__":
    poem_generation()