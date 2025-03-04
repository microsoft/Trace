import time
from opto.trace import bundle, node
from opto.trainer.utils import async_run

def add(x):
    y = node(3)
    return x+y

def sub(x):
    z = node(4)
    return x - z

N=100

inputs = range(100)
def nested_add(i):
    time.sleep(10-i/10)
    return add(inputs[i])

def nested_subtract(x, i):
    time.sleep(i/10)
    return sub(x)

def run(i):
    res1 = nested_add(i)
    res2 = nested_subtract(res1, i)
    return res2

def optional_run_async():
    scores = async_run([run] * N, [(i,) for i in range(N)])

    var_names = []
    for i in range(100):
        var_names.append(scores[i].parents[1].name)

    assert len(var_names) == len(set(var_names)), "Variable names shouldn't overlap in async solution"
