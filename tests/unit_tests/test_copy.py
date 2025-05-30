from opto import trace
from opto.optimizers import OptoPrime
import copy
from opto.utils.llm import LLM

x = trace.node('x')
copy.deepcopy(x)



@trace.bundle(trainable=True)
def fun(x):
    pass

copy.deepcopy(fun.parameter)


x = trace.node('x', trainable=True)
copy.deepcopy(x)


try:
    optimizer = OptoPrime([x])
    optimizer2 = copy.deepcopy(optimizer)

    llm = LLM()
    copy.deepcopy(llm)
except FileNotFoundError as e:
    print(f'Error: {e}')
    print('Omit the test.')