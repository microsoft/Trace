<p >
    <img src="https://github.com/microsoft/Trace/blob/main/docs/images/Trace_Primary_C.png" alt="drawing" width="500"/>
</p>

# End-to-end Generative Optimization for AI Agents

![Static Badge](https://img.shields.io/badge/build-passing-brightgreen)
![PyPI](https://img.shields.io/pypi/v/trace-opt)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/trace-opt)
![GitHub license](https://img.shields.io/badge/License-MIT-blue.svg)
[![arXiv](https://img.shields.io/badge/arXiv-1234.56789-b31b1b.svg)](https://arxiv.org/abs/2406.16218)

Trace is a new AutoDiff-like tool for training AI systems end-to-end with general feedback (like numerical rewards or
losses, natural language text, compiler errors, etc.). Trace generalizes the back-propagation algorithm by capturing and
propagating an AI system's execution trace. Trace is implemented as a PyTorch-like Python library. Users write Python
code directly and can use Trace primitives to optimize certain parts, just like training neural networks!

[Paper](https://arxiv.org/abs/2406.16218) | [Project website](https://microsoft.github.io/Trace/) | [Documentation](https://microsoft.github.io/Trace/intro.html) | [Blogpost](https://www.microsoft.com/en-us/research/blog/tracing-the-path-to-self-adapting-ai-agents/) | [Discord channel](https://discord.gg/4VeAvwFcWy)

<p >
    <img src="https://github.com/microsoft/Trace/blob/main/docs/images/platform2.png" alt="drawing" width="100%"/>
</p>

## Setup

Simply run

    pip install trace-opt

Or for development, clone the repo and run the following.

    pip install -e .

The library requires Python >= 3.9. By default (starting with v0.1.3.5), we use [LiteLLM](https://github.com/BerriAI/litellm) as the backend of LLMs. For backward compatibility, we provide backend-support with [AutoGen](https://github.com/microsoft/autogen); when installing, users can add `[autogen]` tag to install a compatible AutoGen version (e.g., `pip install trace-opt[autogen]`). You may require [Git Large File Storage](https://git-lfs.com/) if
git is unable to clone the repository.

**For questions or reporting bugs, please use Github Issues or post on our [Discord channel](https://discord.gg/4VeAvwFcWy). We actively check these channels.**


## Updates
- **2025.2.7** Trace was featured in the [G-Research NeurIPS highlight](https://www.gresearch.com/news/neurips-paper-reviews-2024-8/) by the Science Director Hugh Salimbeni.
- **2024.12.10** Trace was demoed in person at NeurIPS 2024 Expo.
- **2024.11.05** Ching-An Cheng gave a talk at UW Robotics Colloquium on Trace: [video](https://www.youtube.com/watch?v=T2g1Vo3u_9g).
- **2024.10.21**    New [paper](https://arxiv.org/abs/2410.15625) by Nvidia, Stanford, Visa, & Intel applies Trace to
  optimize for mapper code of parallel programming (for scientific computing and matrix multiplication). Trace (OptoPrime) learns code achieving 1.3X speed up under 10
  minutes, compared to the code optimized by a system engineer expert.
- **2024.9.30** Ching-An Cheng gave a talk to the AutoGen community: [link](https://twitter.com/qingyun_wu/status/1840093778595721727).
- **2024.9.25** [Trace Paper](https://arxiv.org/abs/2406.16218) is accepted to NeurIPS 2024.
- **2024.9.14** TextGrad is available as an optimizer in Trace.
- **2024.8.18** Allen Nie gave a talk to [Pasteur Labs](https://pasteurlabs.ai/) & Institute for Simulation Intelligence.

We have a mailing list for announcements: [Signup](http://eepurl.com/iSscZ-/)

## QuickStart

Trace has two primitives: `node` and `bundle`. `node` is a primitive to define a node in the computation graph. `bundle`
is a primitive to define a function that can be optimized.

```python
from opto.trace import node

x = node(1, trainable=True)
y = node(3)
z = x / y
z2 = x / 3  # the int 3 would be converted to a node automatically

list_of_nodes = [x, node(2), node(3)]
node_of_list = node([1, 2, 3])

node_of_list.append(3)

# easy built-in computation graph visualization
z.backward("maximize z", visualize=True, print_limit=25)
```

Once a node is declared, all the following operations on the node object will be automatically traced.
We built many magic functions to make a node object act like a normal Python object. By marking `trainable=True`, we
tell our optimizer that this node's content
can be changed by the optimizer.

For functions, Trace uses decorators like @bundle to wrap over Python functions. A bundled function behaves like any
other Python function.

```python
from opto.trace import node, bundle


@bundle(trainable=True)
def strange_sort_list(lst):
    '''
    Given list of integers, return list in strange order.
    Strange sorting, is when you start with the minimum value,
    then maximum of the remaining integers, then minimum and so on.
    '''
    lst = sorted(lst)
    return lst


test_input = [1, 2, 3, 4]
test_output = strange_sort_list(test_input)
print(test_output)
```

Now, after declaring what is trainable and what isn't, and use `node` and `bundle` to define the computation graph, we
can use the optimizer to optimize the computation graph.

```python
from opto.optimizers import OptoPrime


# we first declare a feedback function
# think of this as the reward function (or loss function)
def get_feedback(predict, target):
    if predict == target:
        return "test case passed!"
    else:
        return "test case failed!"


test_ground_truth = [1, 4, 2, 3]
test_input = [1, 2, 3, 4]

epoch = 2

optimizer = OptoPrime(strange_sort_list.parameters())

for i in range(epoch):
    print(f"Training Epoch {i}")
    test_output = strange_sort_list(test_input)
    correctness = test_output.eq(test_ground_truth)
    feedback = get_feedback(test_output, test_ground_truth)

    if correctness:
        break

    optimizer.zero_feedback()
    optimizer.backward(correctness, feedback)
    optimizer.step()
```

Then, we can use the familiar PyTorch-like syntax to conduct the optimization.

Here is another example of a simple sales agent:

```python
from opto import trace

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
```

Imagine we have a feedback function (like a reward function) that tells us how well the agent is doing. We can then optimize this agent online:

```python
from opto.optimizers import OptoPrime

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
        except trace.ExecutionError as e:
            greeting = e.exception_node
            feedback, terminal, reward = greeting.data, False, 0

        optimizer.zero_feedback()
        optimizer.backward(greeting, feedback)
        optimizer.step(verbose=True)

        if feedback == 'Correct':
            break

    return agent

agent = train()
```

Defining and training an agent through Trace will give you more flexibility and control over what the agent learns.

## Tutorials

| **Level** | **Tutorial**                                                                              | **Run in Colab**                                                                                                                                                                                       | **Description**                                                                                                                                                                       |
| --- |-------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Beginner | [Getting Started](https://microsoft.github.io/Trace/quickstart/quick_start.html)          | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/microsoft/Trace/blob/website/docs/quickstart/quick_start.ipynb)       | Introduces basic primitives like `node` and `bundle`. Showcases a code optimization pipeline.                                                                                         |
| Beginner | [Adaptive AI Agent](https://microsoft.github.io/Trace/quickstart/quick_start_2.html)      | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/microsoft/Trace/blob/website/docs/quickstart/quick_start_2.ipynb)      | Introduce primitive `model` that allows anyone to build self-improving agents that react to environment feedback. Shows how an LLM agent learns to place a shot in a Battleship game.
| Intermediate | [Multi-Agent Collaboration](https://microsoft.github.io/Trace/quickstart/virtualhome.html) | N/A                                                                                                                                                                                                    | Demonstrates how Trace can be used for multi-agent collaboration environment in Virtualhome.
| Intermediate | [NLP Prompt Optimization](https://microsoft.github.io/Trace/examples/nlp/bigbench_hard.html) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/microsoft/Trace/blob/website/docs/examples/nlp/bigbench_hard.ipynb) | Shows how Trace can optimizes prompt and code together jointly for BigBench-Hard 23 tasks.
| Advanced | [Robotic Arm Control](https://microsoft.github.io/Trace/examples/robotics/metaworld.html) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/microsoft/Trace/blob/website/docs/examples/robotics/metaworld.ipynb)                                     | Trace can optimize code to control a robotic arm after observing a full trajectory of interactions.                                                                                   |


## Supported Optimizers

Currently, we support three optimizers:

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

You can also easily implement your own optimizer that works directly with `TraceGraph` (more tutorials on how to work
with TraceGraph coming soon).

## LLM API Setup

Currently we rely on [LiteLLM](https://github.com/BerriAI/litellm) or [AutoGen v0.2](https://github.com/microsoft/autogen/tree/0.2) for LLM caching and API-Key management.

By default, LiteLLM is used. To change the default backend, set the environment variable `TRACE_DEFAULT_LLM_BACKEND` on terminal
```bash
export TRACE_DEFAULT_LLM_BACKEND="<your LLM backend here>"  # 'LiteLLM' or 'AutoGen`
```
or in python before importing `opto`
```python
import os
os.environ["TRACE_DEFAULT_LLM_BACKEND"] = "<your LLM backend here>"  # 'LiteLLM' or 'AutoGen`
import opto
```



### Using LiteLLM as Backend

Set the keys as the environment variables, following the [documentation of LiteLLM](https://docs.litellm.ai/docs/providers). For example,

```python
import os
os.environ["OPENAI_API_KEY"] = "<your OpenAI API key here>"
os.environ["ANTHROPIC_API_KEY"] = "<your Anthropic API key here>"
```
In Trace, we add another environment variable `TRACE_LITELLM_MODEL` to set the default model name used by LiteLLM for convenience, e.g.,
```bash
export TRACE_LITELLM_MODEL='gpt-4o'
```
will set all LLM instances in Trace to use `gpt-4o` by default.


### Using AutoGen as Backend
First install Trace with autogen flag, `pip install trace-opt[autogen]`. AutoGen relies on `OAI_CONFIG_LIST`, which is a file you put in your working directory. It has the format of:

```json lines
[
    {
        "model": "gpt-4",
        "api_key": "<your OpenAI API key here>"
    },
      {
        "model": "claude-sonnet-3.5-latest",
        "api_key": "<your Anthropic API key here>"
    }
]
```
You can switch between different LLM models by changing the `model` field in this configuration file.
Note AutoGen by default will use the first model available in this config file.

You can also set an `os.environ` variable `OAI_CONFIG_LIST` to point to the location of this file or directly set a JSON string as the value of this variable.

For convenience, we also provide a method that directly grabs the API key from the environment variable `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`.
However, doing so, we specify the model version you use, which is `gpt-4o` for OpenAI and `claude-sonnet-3.5-latest` for Anthropic.


## Citation

If you use this code in your research please cite the following [publication](https://arxiv.org/abs/2406.16218):

```
@article{cheng2024trace,
  title={Trace is the Next AutoDiff: Generative Optimization with Rich Feedback, Execution Traces, and LLMs},
  author={Cheng, Ching-An and Nie, Allen and Swaminathan, Adith},
  journal={arXiv preprint arXiv:2406.16218},
  year={2024}
}
```

## Papers / Projects that Use Trace

[Improving Parallel Program Performance Through DSL-Driven Code Generation with LLM Optimizers](https://arxiv.org/pdf/2410.15625)
Work from Stanford, NVIDIA, Intel, Visa Research.
```
@article{wei2024improving,
  title={Improving Parallel Program Performance Through DSL-Driven Code Generation with LLM Optimizers},
  author={Wei, Anjiang and Nie, Allen and Teixeira, Thiago SFX and Yadav, Rohan and Lee, Wonchan and Wang, Ke and Aiken, Alex},
  journal={arXiv preprint arXiv:2410.15625},
  year={2024}
}
```

[The Importance of Directional Feedback for LLM-based Optimizers](https://arxiv.org/pdf/2405.16434)
Explains the role of feedback in LLM-based optimizers. An early work that influenced Trace's clean separation between the platform, optimizer, and feedback.
```
@article{nie2024importance,
  title={The Importance of Directional Feedback for LLM-based Optimizers},
  author={Nie, Allen and Cheng, Ching-An and Kolobov, Andrey and Swaminathan, Adith},
  journal={arXiv preprint arXiv:2405.16434},
  year={2024}
}
```

## Contributors Wall
<a href="https://github.com/microsoft/Trace/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=microsoft/Trace" />
</a>

## Evaluation

A previous version of Trace was tested with gpt-4-0125-preview on numerical optimization, simulated traffic control,
big-bench-hard, and llf-metaworld tasks, which demonstrated good optimization performance on multiple random seeds;
please see the paper for details.

**Note**  For gpt-4o, please use the version **gpt-4o-2024-08-06** (onwards),
which [fixes](https://platform.openai.com/docs/models/gpt-4o) the structured output issue of gpt-4o-2024-05-13.
While gpt-4 works reliably most of the time, we've found gpt-4o-2024-05-13 often hallucinates even in very basic
optimization problems and does not follow instructions. This might be due to the current implementation of optimizers
rely on outputing in json format. Issues of gpt-4o with json have been reported in the communities (
see [example](https://community.openai.com/t/gpt-4o-doesnt-consistently-respect-json-schema-on-tool-use/751125)).

## Disclaimers

- Trace is an LLM-based optimization framework for research purpose only.
- The current release is a beta version of the library. Features and more documentation will be added, and some
  functionalities may be changed in the future.
- System performance may vary by workflow, dataset, query, and response, and users are responsible for determining the
  accuracy of generated content.
- System outputs do not represent the opinions of Microsoft.
- All decisions leveraging outputs of the system should be made with human oversight and not be based solely on system
  outputs.
- Use of the system must comply with all applicable laws, regulations, and policies, including those pertaining to
  privacy and security.
- The system should not be used in highly regulated domains where inaccurate outputs could suggest actions that lead to
  injury or negatively impact an individual's legal, financial, or life opportunities.

## Contributing

This project welcomes contributions and suggestions. Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit https://cla.opensource.microsoft.com.

When you submit a pull request, a CLA bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

## Trademarks

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft
trademarks or logos is subject to and must follow
[Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/en-us/legal/intellectualproperty/trademarks/usage/general).
Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft
sponsorship.
Any use of third-party trademarks or logos are subject to those third-party's policies.

## Privacy

See [Microsoft Privacy Statement](https://privacy.microsoft.com/en-us/privacystatement).
