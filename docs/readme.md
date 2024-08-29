Steps of deployment:

IMPORTANT: checkout the `website` branch.

1. Run `jupyter-book build docs` under the root directory to build the book. This will create a folder `_build/html` that has the static webpages.
2. Run `python docs/post_build_script.py` to move all files associated with the landing page into the `_build/html` folder.
3. Run `ghp-import -n -p -f docs/_build/html` to deploy the book to GitHub Pages (it creates a branch in the repo)

Or simply run `docs/publish.sh` to run all the above commands.

References:

https://jupyterbook.org/en/stable/start/publish.html 

A few notes:
1. There is no direct way to add an HTML page to Jupyter book.
2. Run `pip install ghp-import` before step 3.
3. Do not manually modify `gh-pages` branch.


Workflow for **adding new documentation**
1. Documents are currently hosted under the `main` branch. You should checkout the `main` branch first and commit your edits here.
2. After you are done with the edits, checkout the `website` branch.
3. Run `git pull origin main` to merge the changes from the `main` branch to the `website` branch.
    - **important**: Do not merge `website` branch into `main` branch, because it contains a lot of web-related files that are not part of the main library.
4. Run the three steps above to deploy the book to GitHub Pages.

Workflow for **adding new jupyter notebooks**
1. Jupyter notebooks will have a `kernelspec` in the metadata. This is usually set to your machine's jupyter kernel and will report an error in CoLab. 
2. We use `colab_kernel_clean_script.py` to clean the `kernelspec` from the notebook. This script will remove the `kernelspec` from the notebook and save it as a new file.
3. If you update a notebook (after running it) or add a new notebook, please run the script on the notebook before committing it to the repo.
4. Run `python docs/colab_kernel_clean_script.py` to clean the notebook.