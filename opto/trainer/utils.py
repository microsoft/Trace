import asyncio
from tqdm.asyncio import tqdm_asyncio

def async_run(runs, args_list = None, kwargs_list = None):
    """Run multiple functions in asynchronously.

    Args:
        runs (list): list of functions to run
        args_list (list): list of arguments for each function
        kwargs_list (list): list of keyword arguments for each function

    """

    if args_list is None:
        args_list = [[]] * len(runs)
    if kwargs_list is None:
        kwargs_list = [{}] * len(runs)

    async def _run():
        loop = asyncio.get_event_loop()
        tasks = [loop.run_in_executor(None, run, *args, **kwargs) for run, args, kwargs, in zip(runs, args_list, kwargs_list)]
        return await tqdm_asyncio.gather(*tasks)

    return asyncio.run(_run())


if __name__ == "__main__":

    def tester(t):  # regular time-consuming function
        import time
        print(t)
        time.sleep(t)
        return t, 2

    runs = [tester] * 5
    args_list = [(3,), (3,), (2,), (3,), (3,)]
    kwargs_list = [{}] * 5
    import time
    start = time.time()
    output = async_run(runs, args_list, kwargs_list)
    print(time.time()-start)
