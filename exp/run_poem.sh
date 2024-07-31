#!/bin/bash
#SBATCH --job-name=poem
#SBATCH --partition=a4-cpu
#SBATCH --cpus-per-task=4
#SBATCH --nodes=1
#SBATCH --mem=16G
#SBATCH --time=00:30:00
#SBATCH --output=outputs/poem_%j.out
#SBATCH --error=outputs/poem_%j.err

# source ~/miniconda3/etc/profile.d/conda.sh
eval "$(conda shell.bash hook)"
conda activate trace
export PYTHONPATH=$PWD

python poem_exp.py exp_name=poem 