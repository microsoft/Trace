# 🎯 Trace

Trace is a Python library that mimics the PyTorch Autograd's gradient tape mechanism, that records *traces* of operations on any Python objects,
including code itself. It enables an automatic construction of execution graph of any Python program.

Our implementation is minimal and purely based in Python. It does not involve any API calls or library-specific dependencies.
Enabling traces of operations on Python objects allows us to capture the execution flow of a program, including AI systems that involve LLMs.
In the example below, we show how Trace, combined with an LLM-based optimizer, can optimize the entire AI system end-to-end.

```{image} images/agent_workflow.png
:alt: overview
:class: bg-primary mb-1
:align: center
```

A typical LLM agent workflow is defined by a sequence of operations, which usually involve user-written Python **programs**, **instructions** to LLMs (e.g.,
prompts, few-shot examples, etc.), and LLM-generated programs to use external tools (e.g., Wikipedia, databases, Wolfram Alpha). Popular LLM libraries often focus on optimizing the instructions to improve the performance of the entire workflow.

Popular libraries like LangChain focus on optimizing the LLM instructions by representing the instructions as special objects
and construct pre/post-processing functions to help users get the most out of LLM calls. In the example figure, this approach updates
and changes the brown square of the agent workflow.

Trace takes a different approach. 
The user writes the Python program as usual, and then uses primitives like `node` and `@bundle` to wrap over their Python objects and functions.
This step is the **declare** phase where a user chooses how to represent the agent workflow as a graph.
After the user has declared the graph, Trace captures the execution flow of the program as a graph. This step is the **forward** phase.
Finally, the user can optimize the entire program, including the LLM instructions, using Trace. This step is the **optimize** phase.


::::{grid}
::class-container: text-center :gutter: 3

:::{grid-item-card} Native Python Support

Write Python programs as usual and use Trace to capture the execution flow of the program as a graph.
:::

:::{grid-item-card} Trace Graph as Protocol

Trace graph represents the execution flow of the program, a universal representation protocol for AI systems.
:::

:::{grid-item-card} End-to-End Optimization
 
Optimize the entire AI system end-to-end with Trace Graph-compatible Optimizers.
:::

::::



----


<!-- ```{tableofcontents}
``` -->
