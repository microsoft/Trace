## Setup

First run 

    conda create -n trace python=3.9
    conda activate trace
    pip install -e .

This creates a conda environment with the trace package installed. Next, run

    pip install requirements.txt

## Running MBPP experiments

    python exp/run_exp.py exp_name=mbpp task=mbpp_task optimizer=opto debug=False wandb.enabled=True

**Data**: We use the MBPP dataset. The LEVER paper provided some more buggy code, which we use. The LEVER data is here: https://drive.google.com/file/d/1pxFSnQVZKTJ9uAeZWiMopMbP8pdWK7GI/view.

**Environment**: The coding environment is in `coding_env.py`. Each trajectory is a contextual MDP, where context $c$ contains 1) problem statement, 2) test cases (and any setup code). The initial obs is the buggy code. The action is a code fix. If the code passes all tests, trajectory terminates. Otherwise, the next obs is the updated buggy code.
Feedback is reward (fraction of test cases that passed) and NEXT-traces.

**Tracing code**: NEXT-traces are implemented in `create_repair_dataset.py` and `next_trace.py`. TODO: refactor these files since the organization is not great.

**Experiment #1**: Run poem generation with and without a rubric synthesizer in `poem_numerical.py`

**Experiment #2**: Run code repair for MBPP with and without a test case synthesizer in `mbpp.py`