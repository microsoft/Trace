# 🎯 Trace

**Trace is a Python library for tracing and optimizing workflows end-to-end by using LLM-powered generative optimizers.**
**It can record *traces* of operations on any Python objects and functions, and automatically construct an execution graph that is useful when LLMs are used as optimizers.**


<a href="https://colab.research.google.com/github/microsoft/Trace/blob/experimental/docs/examples/basic/greeting.ipynb" rel="nofollow" target="_blank"><img src="https://camo.githubusercontent.com/96889048f8a9014fdeba2a891f97150c6aac6e723f5190236b10215a97ed41f3/68747470733a2f2f636f6c61622e72657365617263682e676f6f676c652e636f6d2f6173736574732f636f6c61622d62616467652e737667" alt="Open In Colab" data-canonical-src="https://colab.research.google.com/assets/colab-badge.svg" style="width: 120px;"></a>

Our implementation is minimal and purely based on Python. It does not involve any API calls or library-specific dependencies, so it is composable with other libraries and tools. 
Trace features an API design inspired by PyTorch Autograd's gradient tape mechanism, which we adopted to reduce the learning curve of using Trace. 
These features make Trace an intuitive and flexible framework for building self-adapting AI agents.

```{image} images/agent_workflow.png
:alt: overview
:class: bg-primary mb-1
:align: center
```

A typical LLM agent workflow is defined by a sequence of operations, which usually involve user-written Python **programs**, **instructions** to LLMs (e.g.,
prompts, few-shot examples, etc.), and LLM-generated programs to use external tools (e.g., Wikipedia, databases, Wolfram Alpha). Popular LLM libraries often focus on optimizing the instructions.
For example, libraries like LangChain focus on optimizing the LLM instructions by representing the instructions as special objects
and construct pre/post-processing functions to help users get the most out of LLM calls. In the example figure, this approach updates
and changes the brown squares of the agent workflow.

Trace takes a different approach.
The user writes the Python program as usual, and then uses primitives like `node` and `@bundle` to wrap over their Python objects and functions and to designate which objects are trainable parameters.
This step is the **declare** phase where a user chooses how to represent the agent workflow as a graph.
After the user has declared the inputs and operations, Trace captures the execution flow of the program as a graph. This step is the **forward** phase.
Finally, the user can optimize the entire program, such as by updating the LLM instructions, using Trace. This step is the **optimize** phase.

```python
@trace.model
class Agent:

    def __init__(self, system_prompt):
        self.system_prompt = system_prompt
        self.instruct1 = trace.node("Decide the language", trainable=True)
        self.instruct2 = trace.node("Extract name",  trainable=True)

    def __call__(self, user_query):
        # First LLM 
        response = call_llm(self.system_prompt, self.instruct1, user_query)
        en_or_es = self.decide_lang(response)
        # Second LLM 
        user_name = call_llm(self.system_prompt, self.instruct2, user_query)
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
```

Each application of Trace is defined by an **agent**, a source of **feedback**, and an **optimizer**.
Enabling traces of operations on Python objects allows us to capture the execution flow of an agent, including AI systems that involve LLMs.
In the example below, we show how Trace can optimize an entire AI system end-to-end.

```python
agent = Agent("You are a sales assistant.")
optimizer = OptoPrime(agent.parameters())

try:
    greeting = agent("Hola, soy Juan.")
    feedback = feedback_fn(greeting.data, 'es')
    # feedback = "Correct" or "Incorrect"
except ExecutionError as e:
    greeting = e.exception_node
    feedback = greeting.data, 

optimizer.zero_feedback()
optimizer.backward(greeting, feedback)
optimizer.step()
```

----


<!-- ```{tableofcontents}
``` -->