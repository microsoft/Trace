#!/usr/bin/env bash
cd "$(dirname "$0")/.." || exit
rm -r docs/_build docs/api
ORIGINAL_PYTHONPATH=$PYTHONPATH
export PYTHONPATH=$(pwd)/..:$PYTHONPATH

jupyter-book build docs

# clean up sphinx-autosummary generated files
rm -r docs/api

# Restored PYTHONPATH
export PYTHONPATH=$ORIGINAL_PYTHONPATH

# move all files associated with the landing page into the `_build/html` folder
python docs/post_build_script.py