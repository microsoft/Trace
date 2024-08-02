'''A script to change problem parameters and logging in command line'''

import os
import hydra
from omegaconf import OmegaConf, DictConfig
from typing import Set
import numpy as np
import wandb
from utils import get_local_dir, get_local_run_dir
from poem_numerical import PoemConfig, trace_poem_generation, textgrad_poem_generation

OmegaConf.register_new_resolver("get_local_run_dir", lambda exp_name, local_dirs: get_local_run_dir(exp_name, local_dirs))

# Define and parse arguments.
@hydra.main(version_base=None, config_path="config", config_name="config")
def main(config: DictConfig):
    '''Main entry point for optimization'''

    # Resolve hydra references, e.g. so we don't re-compute the run directory
    OmegaConf.resolve(config)

    missing_keys: Set[str] = OmegaConf.missing_keys(config)
    if missing_keys:
        raise ValueError(f"Got missing keys in config:\n{missing_keys}")

    print(OmegaConf.to_yaml(config))
    config_path = os.path.join(config.local_run_dir, 'poem.yaml')
    with open(config_path, 'w') as f:
        OmegaConf.save(config, f)

    print('=' * 80)
    print(f'Writing to {config.local_run_dir}')
    print('=' * 80)

    exp_name = config.exp_name + '_' + config.task.name + '_' + config.optimizer

    if not config.debug and config.wandb.enabled:
        os.environ['WANDB_CACHE_DIR'] = get_local_dir(config.local_dirs)
        wandb.init(
            entity=config.wandb.entity,
            project=config.wandb.project,
            config=OmegaConf.to_container(config),
            dir=get_local_dir(config.local_dirs),
            name=exp_name,
        )

    # Poem config
    poem_config = PoemConfig(
        student_model=config.task.student_model,
        initial_prompt=config.task.initial_prompt,
        feedback_type=config.task.feedback_type,
        syllable_req=config.task.syllable_req,
        ends_with=config.task.ends_with,
        context=config.task.context,
    )

    # Optimization
    if config.optimizer == 'opto' or config.optimizer == 'opro':
        trace_poem_generation(poem_config, debug=config.debug, wandb_enabled=config.wandb.enabled, optimizer=config.optimizer)
    elif config.optimizer == 'textgrad':
        textgrad_poem_generation(poem_config, debug=config.debug, wandb_enabled=config.wandb.enabled)
    else:
        raise ValueError(f'Unknown optimizer: {config.optimizer}')

    # End Logging (to enable sweeps with Hydra)
    if config.wandb.enabled: wandb.finish()
    

if __name__ == '__main__':
    main()