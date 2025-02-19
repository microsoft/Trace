from opto.utils.llm import LLM
from opto.optimizers.utils import print_color
import os

if os.path.exists("OAI_CONFIG_LIST") or os.environ.get("DEFAULT_LITELLM_MODEL") or os.environ.get("OPENAI_API_KEY"):
    llm = LLM()
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
