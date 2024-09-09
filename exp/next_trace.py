import copy
import sys
from collections import defaultdict

def infer_function_names(program):
    globals_dict = {}
    try:
        exec(program, globals_dict)
    except Exception as e:
        pass

    # Get all the top-level function names
    function_names = []
    lines = program.splitlines()
    for line in lines:
        if 'def ' not in line:
            continue

        function_name = line.split('def ')[1].split('(')[0]
        if function_name in globals_dict:
            function_names.append(function_name)
    return function_names

def copy_state(s):
    out = {}
    for k, v in s.items():
        if type(v) == list:
            out[k] = [e for e in v]
        elif type(v) == tuple:
            out[k] = tuple([e for e in v])
        elif type(v) == dict:
            out[k] = {kk: vv for kk, vv in v.items()}
        else:
            out[k] = v
    return out

# TODO: maybe can make handle pointers?
def check_equality(a, b):   return a == b

def robust_deepcopy(v):
    """Deepcopy can fail is v is not pickleable.
    In that case, just return a string representation."""
    try:
        return copy.deepcopy(v)
    except Exception as e:
        return str(v)

def get_changes(prev, curr):
    """Both prev and curr are mappings of variable names to values."""
    changes = {}
    for var, val in curr.items():
        if var not in prev:
            changes[var] = robust_deepcopy(val)
            continue

        if not check_equality(prev[var], val):
            changes[var] = robust_deepcopy(val)
    return changes

def to_string(val):
    if type(val) == str:
        return f'"{val}"'
    if type(val) == list:
        return f'[{", ".join([to_string(e) for e in val])}]'
    if type(val) == tuple:
        return f'({", ".join([to_string(e) for e in val])})'
    if type(val) == dict:
        return f'{{{", ".join([f"{to_string(k)}: {to_string(v)}" for k, v in val.items()])}}}'
    try:
        return repr(val)  # use repr for richer and more Pythonic info
    except Exception as e:
        return "???"  # the provided repr can also fail...

def obtain_traced_program(program, test_case):
    """Inputs: a program and test_case.
    Will run the program against test_case.
    Return the program with trace information, as well as any exception.
    """
    function_names = infer_function_names(program)
    program_to_run = program + '\n' + test_case

    list_of_states = []

    # Dictionary to keep track of the previous state of local variables for each frame
    previous_state_map = {}

    def trace_function(frame, event, arg):
        nonlocal function_names, previous_state_map, list_of_states

        if frame.f_code.co_name not in function_names:
            return trace_function

        if event == 'line':
            cur_lineno = frame.f_lineno
            code = frame.f_code
            filename = code.co_filename
            function_name = code.co_name

            # Get the current state of local variables
            local_variables = frame.f_locals

            # Create a unique identifier for the current frame
            frame_id = (filename, function_name)

            # Get the previous state of local variables
            previous_state = previous_state_map.get(frame_id, {})
            previous_local_vars = previous_state.get('local_vars', {})
            lineno = previous_state.get('lineno', cur_lineno-1)

            # Determine what has changed
            changes = get_changes(previous_local_vars, local_variables)
            list_of_states.append({'changes': changes, 'lineno': lineno, 'event': event})

            # Update the previous state
            previous_state_map[frame_id] = {
                'lineno': cur_lineno,
                'local_vars': copy_state(local_variables),
            }

        elif event == 'return':
            list_of_states.append({'OUTPUT': arg, 'lineno': frame.f_lineno, 'event': event})

        elif event == 'exception':
            list_of_states.append({'OUTPUT': arg, 'lineno': frame.f_lineno, 'event': event})

        return trace_function

    caught_exception = None
    try:
        sys.settrace(trace_function)  # Set the trace function
        exec(program_to_run, {})  # Execute with no globals. Do not override locals or it cannot import.
        sys.settrace(None)  # Reset the trace function
    except Exception as e:
        caught_exception = repr(e)
        sys.settrace(None)  # Reset the trace function
    except SystemExit as e:
        caught_exception = repr(e)  # catch exit(0)
        sys.settrace(None)

    # mapping from lineno -> states
    states_from_lineno = defaultdict(list)
    exec_counter = 0
    for state in list_of_states:
        lineno = state['lineno']
        idx = lineno-1  # minus 1 offset
        state['exec_counter'] = exec_counter

        # ignore 'line' events with no changes
        if state['event'] == 'line' and not state['changes']:
            continue

        states_from_lineno[idx].append(state)
        exec_counter += 1
            # TODO: how to deal with pass "NO CHANGE"?

    program_with_trace = []
    for lineno, line in enumerate(program_to_run.splitlines()):
        states = states_from_lineno[lineno]
        s = ""
        for state in states:
            if state['event'] == 'line':
                changes_str_list = []
                for k, v in state['changes'].items():
                    changes_str_list.append(f'{k}={to_string(v)}')
                changes_str = ', '.join(changes_str_list)
                s += f'({state["exec_counter"]}) {changes_str}; '
            elif state['event'] == 'return':
                ret_val = state["OUTPUT"]
                s += f'({state["exec_counter"]}) RETURN: {to_string(ret_val)}. '
            elif state['event'] == 'exception':
                exc_cls, exc_val, exc_traceback = state["OUTPUT"]
                s += f'({state["exec_counter"]}) EXCEPTION: {to_string(exc_val)}. '

        if s:
            line = line + '\t# ' + s
        line = line.rstrip()
        program_with_trace.append(line)

    program_with_trace = '\n'.join(program_with_trace)
    return program_with_trace, caught_exception

