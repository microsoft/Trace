import os
import glob
import subprocess


RED = "\033[31m"
GREEN = "\033[32m"
RESET = "\033[0m"


def print_colored(text, color):
    print(f"{color}{text}{RESET}")


# Get the directory where the current module is located
current_dir = os.path.dirname(os.path.abspath(__file__))

# Get a list of all .py files in that directory
py_files = glob.glob(os.path.join(current_dir, "*.py"))

at_least_one_error = False
# Print the list of .py files
for file in py_files:
    filename = os.path.basename(file)
    if filename.startswith("test_"):
        print_colored(f"Running {filename} ...", GREEN)

        result = subprocess.run(["python", file], capture_output=True, text=True)
        if result.returncode == 0:
            print_colored("PASSED", GREEN)
            # print(result.stdout)
        else:
            print_colored("FAILED", RED)
            print(result.stderr)
            at_least_one_error = True

if at_least_one_error:
    exit(1)
