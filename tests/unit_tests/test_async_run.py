from opto import trace
from opto.trainer.utils import async_run
from opto.trace.nodes import USED_NODES

from opto.trace.bundle import disable_external_dependencies_check

disable_external_dependencies_check(True)


import time
@trace.bundle()
def fun_slow(x):
    print('Running slow function', USED_NODES)
    time.sleep(1)
    print('Finshing slow function', USED_NODES)
    return x + 1

@trace.bundle()
def fun_fast(x):
    print('Running fast function', USED_NODES)
    time.sleep(0.1)
    print('Finshing fast function', USED_NODES)
    return x + 1

def run_slow():
    fun_slow(0)

def run_fast():
    i = trace.node(0)
    i.data
    fun_fast(0)

st = time.time()
async_run([run_slow, run_fast])
ed = time.time()
print("Time taken: ", ed - st)