from graphviz import Digraph
import builtins
import re

# Get a list of all names in the builtins module
builtins_list = dir(builtins)
# Filter for function names; this includes exceptions, so you might want to refine this
global_functions_list = [name for name in builtins_list if callable(getattr(builtins, name))]


def contain(container_of_nodes, node):
    # check for identity instead of value
    return any([node is n for n in container_of_nodes])


def parse_eqs_to_dict(text):
    """
    Parse the text of equations into a didctionary

        x0 = 1
        x1=2
        x2=`2`
        x3= def fun():\n    print('hello')\n
        abc_test1=test

    would be parsed into

    {'x0': '1', 'x1': '2', 'x2': '2', 'x3': "def fun():\nprint('hello')", 'abc_test1': 'test'}
    """
    lines = text.split("\n")
    result_dict = {}
    last_key = None
    for line in lines:
        if line == "":
            continue
        if "=" in line:
            key, value = line.split("=", 1)
            last_key = key.strip()
            result_dict[last_key] = value.replace("`", "")
        elif last_key:
            result_dict[last_key] += "\n" + line.replace("`", "")
    return result_dict



def for_all_methods(decorator):
    """Applying a decorator to all methods of a class."""

    def decorate(cls):
        for name, attr in cls.__dict__.items():
            if callable(attr) and not name.startswith("__"):
                setattr(cls, name, decorator(attr))
        return cls

    return decorate
