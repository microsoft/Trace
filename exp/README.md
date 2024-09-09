## Setup

First run 

    conda create -n trace python=3.9
    conda activate trace

This creates a conda environment. Next, run

    pip install -r requirements.txt

## Running the baseline for MBPP code repair

    PYTHONPATH=$PWD python exp/run_exp.py task=mbpp_task optimizer=opto exp_name=mbpp task.with_mistral=false debug=false wandb.enabled=false

## TODO: A code fix for poem environment (ignore for now)

To properly run the poem task, clone the llf-bench repo. Then, change llf-bench llm.py available_backends to include 'autogen'. And finally, inside llf-bench/, run

    pip install -e .

We can run the poem generation experiments with 
    
    PYTHONPATH=$PWD python exp/poem_exp.py exp_name=poem_dspy optimizer=dspy debug=true

**Data**: We use the MBPP dataset. The LEVER paper provided some more buggy code, which we use. The LEVER data is here: https://drive.google.com/file/d/1pxFSnQVZKTJ9uAeZWiMopMbP8pdWK7GI/view.

**Environment**: The coding environment is in `coding_env.py`. Each trajectory is a contextual MDP, where context $c$ contains 1) problem statement, 2) test cases (and any setup code). The initial obs is the buggy code. The action is a code fix. If the code passes all tests, trajectory terminates. Otherwise, the next obs is the updated buggy code.
Feedback is reward (fraction of test cases that passed) and NEXT-traces.

**Tracing code**: NEXT-traces are implemented in `create_repair_dataset.py` and `next_trace.py`. 

**Experiment #1**: Run poem generation with and without a rubric synthesizer in `poem_numerical.py`

**Experiment #2**: Run code repair for MBPP with and without a test case synthesizer in `mbpp.py`