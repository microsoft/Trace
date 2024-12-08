from opto import trace
from opto.trace import node, bundle, model, ExecutionError
from opto.optimizers import OptoPrime


@trace.model
class Agent:

    def __init__(self, system_prompt):
        self.system_prompt = system_prompt
        self.instruct1 = trace.node("Decide the language", trainable=True)
        self.instruct2 = trace.node("Extract name if it's there", trainable=True)

    def __call__(self, user_query):
        response = trace.operators.call_llm(self.system_prompt,
                                            self.instruct1, user_query)
        en_or_es = self.decide_lang(response)

        user_name = trace.operators.call_llm(self.system_prompt,
                                             self.instruct2, user_query)
        greeting = self.greet(en_or_es, user_name)

        return greeting

    @trace.bundle(trainable=True)
    def decide_lang(self, response):
        """Map the language into a variable"""
        return

    @trace.bundle(trainable=True)
    def greet(self, lang, user_name):
        """Produce a greeting based on the language"""
        greeting = "Hola"
        return f"{greeting}, {user_name}!"


def feedback_fn(generated_response, gold_label='en'):
    if  gold_label == 'en' and 'Hello' in generated_response:
        return "Correct"
    elif gold_label == 'es' and 'Hola' in generated_response:
        return "Correct"
    else:
        return "Incorrect"


def train():
    epoch = 3
    agent = Agent("You are a sales assistant.")
    optimizer = OptoPrime(agent.parameters())

    for i in range(epoch):
        print(f"Training Epoch {i}")
        try:
            greeting = agent("Hola, soy Juan.")
            feedback = feedback_fn(greeting.data, 'es')
        except ExecutionError as e:
            greeting = e.exception_node
            feedback, terminal, reward = greeting.data, False, 0

        optimizer.zero_feedback()
        optimizer.backward(greeting, feedback)
        optimizer.step(verbose=True)

        if feedback == 'Correct':
            break

    return agent


class CorrectAgent:

    def __init__(self, system_prompt):
        self.system_prompt = system_prompt
        self.instruct1 = node("Decide the language: es or en?", trainable=True)
        self.instruct2 = node("Extract name if it's there", trainable=True)

    def __call__(self, user_query):
        response = trace.operators.call_llm(self.system_prompt, self.instruct1, user_query)
        en_or_es = self.decide_lang(response)

        user_name = trace.operators.call_llm(self.system_prompt, self.instruct2, user_query)
        greeting = self.greet(en_or_es, user_name)

        return greeting

    @bundle(trainable=True)
    def decide_lang(self, response):
        """Map the language into a variable"""
        return 'es' if 'es' or 'spanish' in response.lower() else 'en'

    @bundle(trainable=True)
    def greet(self, lang, user_name):
        """Produce a greeting based on the language"""
        greeting = "Hola" if lang.lower() == "es" else "Hello"
        return f"{greeting}, {user_name}!"
