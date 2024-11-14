
import asyncio
import time
from opto import trace

@trace.bundle()
async def basic(a=0):
    await asyncio.sleep(1)
    return 'basic'

async def main():
    a = trace.node('a')
    st = time.time()
    x = await basic(a)
    ed = time.time()
    print("Time taken: ", ed - st)
    print(type(x), x)
    assert type(x) == trace.nodes.MessageNode
    assert x == 'basic'
    assert a in x.parents
    assert len(x.parents) == 1


asyncio.run(main())


async def main2():
    a = trace.node('a')
    st = time.time()
    x, y, z = await asyncio.gather(basic(a), basic(a), basic(a))  # run in parallel
    ed = time.time()
    print("Time taken: ", ed - st)

    assert type(x) == trace.nodes.MessageNode
    assert x == 'basic'
    assert a in x.parents
    assert len(x.parents) == 1
    assert type(y) == trace.nodes.MessageNode
    assert y == 'basic'
    assert a in y.parents
    assert len(y.parents) == 1
    assert type(z) == trace.nodes.MessageNode
    assert z == 'basic'
    assert a in z.parents
    assert len(z.parents) == 1


asyncio.run(main2())
