# FAQ

### Difference to Libraries like TextGrad

TextGrad is both a library and an optimizer algorithm. Currently, we support three optimizers:

- OPRO: [Large Language Models as Optimizers](https://arxiv.org/abs/2309.03409)
- TextGrad: [TextGrad: Automatic "Differentiation" via Text](https://arxiv.org/abs/2406.07496)
- OptoPrime: [Our proposed algorithm](https://arxiv.org/abs/2406.16218) -- using the entire computational graph to perform parameter update. It is 2-3x
  faster than TextGrad.

Using our framework, you can seamlessly switch between different optimizers:

```python
optimizer1 = OptoPrime(strange_sort_list.parameters())
optimizer2 = OPRO(strange_sort_list.parameters())
optimizer3 = TextGrad(strange_sort_list.parameters())
```

Here is a summary of the optimizers:

|                                   | Computation Graph | Code as Functions | Library Support | Supported Optimizers      | Speed       | Large Graph |
|-----------------------------------|-------------------|-------------------|------------------|---------------------------|-------------|-------------|
| OPRO                              | ❌                 | ❌                 | ❌            | OPRO                      | ⚡️          | ✅      |
| TextGrad                          | ✅                 | ❌                 | ✅            | TextGrad                  | 🐌          | ✅      |
| Trace  | ✅                 | ✅                 | ✅            | OPRO, OptoPrime, TextGrad | ⚡  | ✅      |

The table evaluates the frameworks in the following aspects:

- Computation Graph: Whether the optimizer leverages the computation graph of the workflow.
- Code as Functions: Whether the framework allows users to write actual executable Python functions and not require
  users to wrap them in strings.
- Library Support: Whether the framework has a library to support the optimizer.
- Speed: TextGrad is about 2-3x slower than OptoPrime (Trace). OPRO has no concept of computational graph, therefore is very fast.
- Large Graph: OptoPrime (Trace) represents the entire computation graph in context, therefore, might have issue with graphs that have more than hundreds of operations. TextGrad does not have the context-length issue, however, might be very slow on large graphs.

We provide a comparison to validate our implementation of TextGrad in Trace:

<p align="center">
    <img src="https://github.com/microsoft/Trace/blob/main/docs/images/compare_to_textgrad3.png?raw=True" alt="drawing" width="100%"/>
</p>

To produce this table, we ran the TextGrad pip-installed repo on 2024-10-30, and we also include the numbers reported in the TextGrad paper.
The LLM APIs are called around the same time to ensure a fair comparison. TextGrad paper's result was reported in 2024-06.

### Difference to Libraries like AutoGen, AG2, OpenAI Swarm, Llama Stack

