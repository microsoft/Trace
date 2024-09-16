

from opto import trace

@trace.bundle(trainable=True)
def fun(x):
    """ Some docstring. """
    return len(x), x.count('\n')


x = 'hello\nworld\n'
a, b = fun(x)
print(a, b)

print(fun.parameters()[0].data)

fun.parameters()[0]._data =fun.parameters()[0]._data.replace('len(x)', '"Hello"')

a, b = fun(x)
print(a, b)
fun.save('fun.pkl')

fun.load('fun.pkl')



a, b = fun(x)
print(a, b)