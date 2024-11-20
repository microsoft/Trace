from opto.utils.llm import AutoGenLLM
from opto.optimizers.utils import print_color

try:
    llm = AutoGenLLM()
    system_prompt = 'You are a helpful assistant.'
    user_prompt = "Hello world."


    messages = [{"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_prompt}]

    output = llm(messages=messages)
    # Alternatively, you can use the following code:
    # output = llm.create(messages=messages)

    response = output.choices[0].message.content


    print_color(f'System: {system_prompt}', 'red')
    print_color(f'User: {user_prompt}', 'blue')
    print_color(f'LLM: {response}', 'green')
except FileNotFoundError as e:
    print_color(f'Error: {e}', 'red')
    print_color('Omit the test.', 'yellow')