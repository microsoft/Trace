# Trace

**Trace is a framework for automatically tracing through LLM-based agentic workflows, constructing the underlying graph of how an agentic flow transforms any input to the output.**

Automatic differentiation (Auto-Diff) is enabled by constructing a computational graph (Tensorflow) or a gradient tape (PyTorch). Without tracing through tensor operations specified by a Python program that transform an numerical input (images, text, numbers) to an output (classification label, prediction target), we would not have started the era of deep learning, and now the era of large language model enabled general intelligence.

Trace uses a technique similar to the gradient tape used in PyTorch. We construct a node to wrap about Python operations that are frequently used in Agentic workflows and record these operations and represent them as an underlying graph (Trace Graph). This graph allows us to design any type of optimization over the agentic workflow itself. 

::::{grid}
::class-container: text-center :gutter: 3

:::{grid-item-card} End-to-End Optimization via LLM
 
An AI system has many modules. Trace captures the system's underlying execution flow and represents it as a graph (Trace Graph). Trace can then optimize the entire system with general feedback using LLM-based optimizers.
:::

:::{grid-item-card} Native Python Support

Trace gives users full flexibility in programming AI systems. Two primitives node and bundle wrap over Python objects and functions, making Trace compatible with any Python program and capable of optimizing any mixture of code, string, numbers, and objects, etc.
:::

:::{grid-item-card} Platform for Developing New Optimizers

Instead of propagating gradients, Trace propagates Minimal Subgraphs which contains the sufficient information for general computation. This common abstraction allows researchers to develop new optimizers for diverse AI systems.
:::
::::

----




<!-- ```{tableofcontents}
``` -->
