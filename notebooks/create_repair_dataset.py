import multiprocessing
import next_trace
import json
import os
import traceback
import file_utils

# Function to run a given function with arguments and capture output
# Returns (outputs, timeout, exception)
def run_function_with_timeout(func, args=(), kwargs={}, timeout=1):
    def wrapper(pipe_end):
        try:
            result = func(*args, **kwargs)
            pipe_end.send(("result", result))
        except Exception as e:
            formatted_exception = f"{type(e).__name__}: {str(e)}\n"
            formatted_exception += ''.join(traceback.format_tb(e.__traceback__))
            pipe_end.send(("exception", formatted_exception))

    recv_end, send_end = multiprocessing.Pipe(duplex=False)
    process = multiprocessing.Process(target=wrapper, args=(send_end,))
    process.start()

    if process.join(timeout) is None:  # Process is still alive after timeout
        process.terminate()
        process.join()
        return None, True, None

    if recv_end.poll(0.01):  # Short timeout to prevent hanging
        message_type, content = recv_end.recv()
        if message_type == "result":
            return content, False, None
        elif message_type == "exception":
            return None, False, content

    # Unknown error..
    print("UNKNOWN ERROR!!!!!")
    return None, False, "UNKNOWN ERROR"


def obtain_traced_program(program, test_case, test_setup_code, timeout=1):
    if test_setup_code:
        test_case = test_setup_code + '\n' + test_case

    # # For debugging
    # result = next_trace.obtain_traced_program(program, test_case)
    # finished_exec = True
    result, timed_out, caught_exc = run_function_with_timeout(
        next_trace.obtain_traced_program, args=(program, test_case), timeout=timeout)
    assert caught_exc is None, f"Should never catch exception here. Instead got {caught_exc}."
    if timed_out:
        return {'trace': None, 'exc': None, 'timeout': True}

    assert len(result) == 2, f'Expected 2 outputs, got {result}.'
    traced_program, caught_exception = result
    return {
        'trace': traced_program,
        'exc': caught_exception,
        'timeout': False,
    }


def create_repair_dataset_from_mbpp(data, jsonl_path):
    existing_entries = file_utils.load_jsonl(jsonl_path)
    start_at_i = 0
    if existing_entries:
        start_at_i = existing_entries[-1]['task_idx']

    existing_entries = set([(e['task_idx'], e['program_idx']) for e in existing_entries])
    
    for i in range(start_at_i, len(data)):
        d = data[i]

        num_repairs_for_this_task = 0
        for j in range(len(d['generated_programs'])):
            if (i, j) in existing_entries:
                num_repairs_for_this_task += 1
                print(f'skipping ({i}, {j}) since already exists')
                continue

            if num_repairs_for_this_task >= 20:
                break

            print(i, j)
            trace_results = []  # list of trace results
            failed_some_test = False  # filter out those that pass all tests
            program = d['generated_programs'][j]['code']
            test_setup_code = d['metadata']['test_setup_code']
            for test_case in d['metadata']['test_list']:
                output = obtain_traced_program(
                    program, test_case, test_setup_code
                )
                if output['exc']:
                    failed_some_test = True
                trace_results.append(output)

            if failed_some_test:
                current_entry = {
                    'task_idx': i,
                    'program_idx': j,
                    'instruction': d['metadata']['text'],
                    'buggy_code': program,
                    'test_setup_code': test_setup_code,
                    'test_cases': d['metadata']['test_list'],
                    'trace_results': trace_results,
                }
                with open(jsonl_path, 'a') as f:
                    f.write(json.dumps(current_entry) + '\n')
                num_repairs_for_this_task += 1

                                                     


def load_jsonl(path):
    with open(path, 'r') as f:
        data = f.readlines()
    data = [json.loads(d) for d in data]
    return data


if __name__ == "__main__":
    dev_data = load_jsonl('./data/mbpp/mbpp_codex_verification_dev.jsonl')
    train_data = load_jsonl('./data/mbpp/mbpp_codex_verification_train.jsonl')
    test_data = load_jsonl('./data/mbpp/mbpp_codex_verification_test.jsonl')

    train_data = train_data + test_data[:250]
    test_data = test_data[250:]
    print(len(train_data), len(dev_data), len(test_data))

    create_repair_dataset_from_mbpp(train_data[0:2], './data/mbpp/train_repair_dataset.jsonl')
    # create_repair_dataset_from_mbpp(dev_data, './data/mbpp/dev_repair_dataset.jsonl')
    # create_repair_dataset_from_mbpp(test_data, './data/mbpp/test_repair_dataset.jsonl')
