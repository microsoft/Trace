
from opto import trace
bundle = trace.bundle
# Test different decorator usages

def dec(fun):
    # print('dec')
    return fun
def dec2(fun):
    # print('dec')
    return fun


code_str = '@dec\ndef my_fun():  # some comment with bundle\n    """ Some def """  # bundle comments\n    print(\'run\')  # bundle comments'

@trace.bundle(\
        )   # random comments
@dec
def my_fun():  # some comment with bundle
    """ Some def """  # bundle comments
    print('run')  # bundle comments

my_fun()
assert my_fun.info['source'] == code_str
assert my_fun.info['line_number'] == 18


@bundle()
@dec
def my_fun():  # some comment with bundle
    """ Some def """  # bundle comments
    print('run')  # bundle comments

my_fun()
assert my_fun.info['source'] == code_str
assert my_fun.info['line_number'] == 29


@dec2
@bundle()
@dec
def my_fun():  # some comment with bundle
    """ Some def """  # bundle comments
    print('run')  # bundle comments

my_fun()
assert my_fun.info['source'] == code_str
assert my_fun.info['line_number'] == 41


@dec2
@trace.bundle()
@dec
def my_fun():  # some comment with bundle
    """ Some def """  # bundle comments
    print('run')  # bundle comments

my_fun()
assert my_fun.info['source'] == code_str
assert my_fun.info['line_number'] == 53
