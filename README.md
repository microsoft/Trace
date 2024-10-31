<style>
#logo {background-color: #ffc202}
</style>

<p id="logo" align="center">
    <img src="https://github.com/microsoft/Trace/blob/main/docs/images/Trace_Black_B.png" alt="drawing" width="60%"/>
</p>

# Trace: End-to-end Generative Optimization for AI Systems and Agents

![PyPI](https://img.shields.io/pypi/v/trace-opt)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/trace-opt)
![GitHub license](https://img.shields.io/badge/License-MIT-blue.svg)
[![arXiv](https://img.shields.io/badge/arXiv-1234.56789-b31b1b.svg)](https://arxiv.org/abs/2406.16218)



Trace is a new AutoDiff-like tool for training AI systems end-to-end with general feedback (like numerical rewards or losses, natural language text, compiler errors, etc.). Trace generalizes the back-propagation algorithm by capturing and propagating an AI system's execution trace. Trace is implemented as a PyTorch-like Python library. Users write Python code directly and can use Trace primitives to optimize certain parts, just like training neural networks!

[Paper](https://arxiv.org/abs/2406.16218) | [Project website](https://microsoft.github.io/Trace/) | [Documentation](https://microsoft.github.io/Trace/intro.html) | [Blogpost](https://www.microsoft.com/en-us/research/blog/tracing-the-path-to-self-adapting-ai-agents/)


## Setup

Simply run 

    pip install trace-opt

Or for development, clone the repo and run the following. 
    
    pip install -e .

The library requires Python >= 3.9. The installation script will git clone [AutoGen](https://github.com/microsoft/autogen). You may require [Git Large File Storage](https://git-lfs.com/) if git is unable to clone the repository otherwise.


## Citation
If you use this code in your research please cite the following [publication](https://arxiv.org/abs/2406.16218):
```
@article{cheng2024trace,
  title={Trace is the New AutoDiff--Unlocking Efficient Optimization of Computational Workflows},
  author={Cheng, Ching-An and Nie, Allen and Swaminathan, Adith},
  journal={arXiv preprint arXiv:2406.16218},
  year={2024}
}
```
## Updates

 - **2024.10.21**    New [paper](https://arxiv.org/abs/2410.15625) by Nvidia, Stanford, Visa, & Intel applies Trace to optimize for mapper code of parallel programming. Trace (OptoPrime) learns code achieving 1.3X speed up under 10 minutes, compared with the code optimized by domain expert.
 - **2024.9.25** [Trace Paper](https://arxiv.org/abs/2406.16218) is accepted to NeurIPS 2024.
 - **2024.9.14** TextGrad is available as a Trace optimizer.



## Evaluation
A previous version of Trace was tested with gpt-4-0125-preview on numerical optimization, simulated traffic control, big-bench-hard, and llf-metaworld tasks, which demonstrated good optimization performance on multiple random seeds; please see the paper for details.

**Note**  For gpt-4o, please use the version **gpt-4o-2024-08-06** (onwards), which [fixes](https://platform.openai.com/docs/models/gpt-4o) the structured output issue of gpt-4o-2024-05-13.
While gpt-4 works reliably most of the time, we've found gpt-4o-2024-05-13 often hallucinates even in very basic optimization problems and does not follow instructions. This might be due to the current implementation of optimizers rely on outputing in json format. Issues of gpt-4o with json have been reported in the communities (see [example](https://community.openai.com/t/gpt-4o-doesnt-consistently-respect-json-schema-on-tool-use/751125)).

## Disclaimers
- Trace is an LLM-based optimization framework for research purpose only.
- The current release is a beta version of the library. Features and more documentation will be added, and some functionalities may be changed in the future.
- System performance may vary by workflow, dataset, query, and response, and users are responsible for determining the accuracy of generated content. 
- System outputs do not represent the opinions of Microsoft.
- All decisions leveraging outputs of the system should be made with human oversight and not be based solely on system outputs.
- Use of the system must comply with all applicable laws, regulations, and policies, including those pertaining to privacy and security.
- The system should not be used in highly regulated domains where inaccurate outputs could suggest actions that lead to injury or negatively impact an individual's legal, financial, or life opportunities.


## Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a
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
Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship.
Any use of third-party trademarks or logos are subject to those third-party's policies.


## Privacy

See [Microsoft Privacy Statement](https://privacy.microsoft.com/en-us/privacystatement).
