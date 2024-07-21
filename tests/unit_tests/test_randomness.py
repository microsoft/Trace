import opto.trace as trace
import random

seed = 0
random.seed(seed)
x = random.random()


def test():
    x = random.random()
    return x


random.seed(seed)
x1 = test()
random.seed(seed)
x2 = test()
assert x1 == x2


obj = 1
print("outside obj id", id(obj))


@trace.bundle(trainable=True)
def test():
    return 1
    # x = random.random()
    # x = obj + x
    # print("inside obj id", id(obj))
    # return x


random.seed(seed)
x1 = test()
random.seed(seed)
x2 = test()
assert x1 == x2
