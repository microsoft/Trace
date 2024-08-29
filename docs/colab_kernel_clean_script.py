import shutil
import os
import json

# Figure out if we are in the `docs` directory or the root directory
if os.path.exists('index.html'):
    print("Found index.html in current directory, assuming we are in the root directory")
else:
    print("In the root directory, changing to docs directory")
    os.chdir('docs')
    if not os.path.exists('_config.yml'):
        raise FileNotFoundError("Could not find _config.yml in the root directory or the docs directory.")

# Clean up Jupyter notebooks (remove kernel-spec)
for root, dirs, files in os.walk('.'):
    for file in files:
        if file.endswith('.ipynb'):
            print(root, file)
            with open(os.path.join(root, file), 'r') as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    print("Could not read JSON, skipping", file)
                    continue
            if 'kernelspec' in data['metadata']:
                print("removed kernel", data['metadata']['kernelspec'])
                del data['metadata']['kernelspec']
                with open(os.path.join(root, file), 'w') as f:
                    json.dump(data, f, indent=4)