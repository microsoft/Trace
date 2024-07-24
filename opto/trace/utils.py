from graphviz import Digraph
import builtins
import re
import json

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


def render_opt_step(step_idx, optimizer, no_trace_graph=False, no_improvement=False):
    from IPython.display import display, HTML

    idx = step_idx
    llm_response = json.loads(optimizer.log[idx]['response'])
    r1 = llm_response['reasoning']

    if 'suggestion' in llm_response and llm_response['suggestion'] is not None:
        a1 = ""
        for var_name, var_body in llm_response['suggestion'].items():
            a1 += var_name + ':\n\n'
            a1 += var_body + '\n\n'

    elif 'answer' in llm_response and llm_response['answer'] is not None:
        a1 = llm_response['answer']
    else:
        a1 = "<ERROR> NULL/INVALID RESPONSE"

    pi = optimizer.summary_log[idx]['problem_instance']  # full
    f1 = pi.feedback

    masked = ['#Feedback', '#Others', '#Instruction']
    pi = optimizer.probelm_instance(optimizer.summary_log[idx]['summary'], mask=masked)

    # a hack to remove "#Feedback:" because it has a colon
    pi = str(pi)
    pi = pi.replace("#Feedback:", "#Feedback")

    for m in masked:
        pi = pi.replace(m + '\n', '')

    # a quick processing to reduce multiple empty lines to one
    pi = re.sub(r'\n\s*\n', '\n\n', pi)
    g1 = pi

    html_template = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin-bottom: 10px;">
            <!-- First set of blocks -->
    """

    if not no_trace_graph:
        html_template += f"""
            <div style="display: flex; align-items: stretch; margin-bottom: 10px;">
                <div style="flex-grow: 1; background-color: #E0E0E0; border: 2px solid #9E9E9E; padding: 10px; border-radius: 5px; width: 550px;">
                    <p><b>Trace Graph</b></p><pre style="margin: 0; white-space: pre-wrap; word-wrap: break-word;">{g1}</pre>
                </div>
                <div style="width: 40px; display: flex; align-items: center; justify-content: center; font-size: 24px; color: #9E9E9E;">
                    g<sub>{idx}</sub>
                </div>
            </div>
        """
    html_template += f"""
            <div style="display: flex; align-items: stretch; margin-bottom: 10px;">
                <div style="flex-grow: 1; background-color: #FFB3BA; border: 2px solid #FF6B6B; padding: 10px; border-radius: 5px;">
                    <p style="margin: 0;"><b>Feedback: </b>{f1}</p>
                </div>
                <div style="width: 40px; display: flex; align-items: center; justify-content: center; font-size: 24px; color: #FF6B6B;">
                    f<sub>{idx}</sub>
                </div>
            </div>

            <div style="display: flex; align-items: stretch; margin-bottom: 10px;">
                <div style="flex-grow: 1; background-color: #BAFFC9; border: 2px solid #4CAF50; padding: 10px; border-radius: 5px; width: 550px;">
                    <p style="margin: 0;"><b>Reasoning: </b>{r1}</p>
                </div>
                <div style="width: 40px; display: flex; align-items: center; justify-content: center; font-size: 24px; color: #4CAF50;">
                    r<sub>{idx + 1}</sub>
                </div>
            </div>
        """

    if not no_improvement:
        html_template += f"""
                <div style="display: flex; align-items: stretch; margin-bottom: 20px;">
                <div style="flex-grow: 1; background-color: 'white'; border: 2px solid #4D9DE0; padding: 10px; border-radius: 5px;">
                    <p><b>Improvement</b></p>
                    <pre style="margin: 0; white-space: pre-wrap; word-wrap: break-word; font-family: monospace; background-color: 'white';">{a1}</pre>
                </div>
                <div style="width: 40px; display: flex; align-items: center; justify-content: center; font-size: 24px; color: #4D9DE0;">
                    a<sub>{idx + 1}</sub>
                </div>
            </div>
        """

    html_template += "</div>"

    display(HTML(html_template))