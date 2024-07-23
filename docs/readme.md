Steps of deployment:

IMPORTANT: checkout the `website` branch.

1. Run `jupyter-book build docs` under the root directory to build the book. This will create a folder `_build/html` that has the static webpages.
2. Run `python docs/post_build_script.py` to move all files associated with the landing page into the `_build/html` folder.
3. Run `ghp-import -n -p -f docs/_build/html` to deploy the book to GitHub Pages (it creates a branch in the repo)


References:

https://jupyterbook.org/en/stable/start/publish.html 

A few notes:
1. There is no direct way to add an HTML page to Jupyter book.
2. Run `pip install ghp-import` before step 3.
3. Do not manually modify `gh-pages` branch.