import asyncio
import functools
import warnings
from concurrent.futures import ThreadPoolExecutor
from tqdm.asyncio import tqdm_asyncio
from opto.trace.bundle import ALLOW_EXTERNAL_DEPENDENCIES

def async_run(runs, args_list = None, kwargs_list = None, max_workers = None):
    """Run multiple functions in asynchronously.

    Args:
        runs (list): list of functions to run
        args_list (list): list of arguments for each function
        kwargs_list (list): list of keyword arguments for each function
        max_workers (int, optional): maximum number of worker threads to use.
            If None, the default ThreadPoolExecutor behavior is used.

    """
    # if ALLOW_EXTERNAL_DEPENDENCIES is not False:
    #     warnings.warn(
    #         "Running async_run with external dependencies check enabled. "
    #         "This may lead to false positive errors. "
    #         "If such error happens, call disable_external_dependencies_check(True) before running async_run.",
    #         UserWarning,
    #     )


    if args_list is None:
        args_list = [[]] * len(runs)
    if kwargs_list is None:
        kwargs_list = [{}] * len(runs)

    async def _run():
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            tasks = [loop.run_in_executor(executor, functools.partial(run, *args, **kwargs)) 
                    for run, args, kwargs, in zip(runs, args_list, kwargs_list)]
            return await tqdm_asyncio.gather(*tasks)

    return asyncio.run(_run())


if __name__ == "__main__":

    def tester(t):  # regular time-consuming function
        import time
        print(t)
        time.sleep(t)
        return t, 2

    runs = [tester] * 10  # 10 tasks to demonstrate threading
    args_list = [(3,), (3,), (2,), (3,), (3,), (2,), (2,), (3,), (2,), (3,)]
    kwargs_list = [{}] * 10
    import time
    
    # Example with 1 thread (runs sequentially)
    print("Running with 1 thread (sequential):")
    start = time.time()
    output = async_run(runs, args_list, kwargs_list, max_workers=1)
    print(f"Time with 1 thread: {time.time()-start:.2f} seconds")
    
    # Example with limited workers (2 threads)
    print("\nRunning with 2 threads (parallel):")
    start = time.time()
    output = async_run(runs, args_list, kwargs_list, max_workers=2)
    print(f"Time with 2 threads: {time.time()-start:.2f} seconds")
    
    # Example with limited workers (4 threads)
    print("\nRunning with 4 threads (parallel):")
    start = time.time()
    output = async_run(runs, args_list, kwargs_list, max_workers=4)
    print(f"Time with 4 threads: {time.time()-start:.2f} seconds")
    
    # Example with default number of workers
    print("\nRunning with default number of threads:")
    start = time.time()
    output = async_run(runs, args_list, kwargs_list)
    print(f"Time with default threads: {time.time()-start:.2f} seconds")
