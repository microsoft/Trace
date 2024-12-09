# 🎯 Trace

**Trace is a Python library for tracing and optimizing workflows end-to-end by using LLM-powered generative optimizers.**
**It can record *traces* of operations on any Python objects and functions, and automatically construct an execution graph that is useful when LLMs are used as optimizers.**

Our implementation is minimal and purely based on Python. It does not involve any API calls or library-specific dependencies, so it is composable with other libraries and tools. 
Trace features an API design inspired by PyTorch Autograd's gradient tape mechanism, which we adopted to reduce the learning curve of using Trace. 
These features make Trace an intuitive and flexible framework for building self-adapting AI agents.

Each application of Trace is defined by an **agent**, a source of **feedback**, and an **optimizer**.
Enabling traces of operations on Python objects allows us to capture the execution flow of an agent, including AI systems that involve LLMs.
In the example below, we show how Trace can optimize an entire AI system end-to-end.

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


::::{grid}
::class-container: text-center :gutter: 3

:::{grid-item-card} Native Python Support

Write Python programs as usual and use Trace to capture the execution flow of the program as a graph.
:::

:::{grid-item-card} Trace Graph as Protocol

Trace graph represents the execution flow of the program, a universal representation protocol for AI systems.
:::

:::{grid-item-card} End-to-End Optimization

Optimize the entire AI system end-to-end with Trace-graph-compatible optimizers.
:::

::::



----


<!-- ```{tableofcontents}
``` -->
