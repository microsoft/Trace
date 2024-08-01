#!/usr/bin/env bash
cd "$(dirname "$0")/.." || exit
rm -r docs/_build
jupyter-book build docs
python docs/post_build_script.py
ghp-import -n -p -f docs/_build/html