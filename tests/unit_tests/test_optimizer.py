import os
import autogen
from opto.trace import bundle, node, GRAPH
from opto.optimizers import OptoPrime


# Test the optimizer with an example of number

GRAPH.clear()


def blackbox(x):
    return -x * 2


@bundle()
def bar(x):
    "This is a test function, which does negative scaling."
    return blackbox(x)


def foo(x):
    y = x + 1
    return x * y


# foobar is a composition of custom function and built-in functions
def foobar(x):
    return foo(bar(x))


def user(x):
    if x < 50:
        return "The number needs to be larger."
    else:
        return "Success."

if os.path.exists("OAI_CONFIG_LIST"):
    # One-step optimization example
    x = node(-1.0, trainable=True)
    optimizer = OptoPrime([x], config_list=autogen.config_list_from_json("OAI_CONFIG_LIST"))
    output = foobar(x)
    feedback = user(output.data)
    optimizer.zero_feedback()
    optimizer.backward(output, feedback, visualize=True)  # this is equivalent to the below line
    optimizer.step(verbose=True)


## Test the optimizer with an example of str
GRAPH.clear()


@bundle()
def convert_english_to_numbers(x):
    """This is a function that converts English to numbers. This function has limited ability."""
    # remove special characters, like, ", &, etc.
    x = x.replace('"', "")
    try:  # Convert string to integer
        return int(x)
    except ValueError:
        pass
    # Convert integers written in Engligsh in [-10, 10] to numbers
    if x == "negative ten":
        return -10
    if x == "negative nine":
        return -9
    if x == "negative eight":
        return -8
    if x == "negative seven":
        return -7
    if x == "negative six":
        return -6
    if x == "negative five":
        return -5
    if x == "negative four":
        return -4
    if x == "negative three":
        return -3
    if x == "negative two":
        return -2
    if x == "negative one":
        return -1
    if x == "zero":
        return 0
    if x == "one":
        return 1
    if x == "two":
        return 2
    if x == "three":
        return 3
    if x == "four":
        return 4
    if x == "five":
        return 5
    if x == "six":
        return 6
    if x == "seven":
        return 7
    if x == "eight":
        return 8
    if x == "nine":
        return 9
    if x == "ten":
        return 10
    return "FAIL"


def user(x):
    if x == "FAIL":
        return "The text cannot be converted to a number."
    if x < 50:
        return "The number needs to be larger."
    else:
        return "Success."


def foobar_text(x):
    output = convert_english_to_numbers(x)
    if output.data == "FAIL":  # This is not traced
        return output
    else:
        return foo(bar(output))


GRAPH.clear()
x = node("negative point one", trainable=True)

if os.path.exists("OAI_CONFIG_LIST"):
    optimizer = OptoPrime([x], config_list=autogen.config_list_from_json("OAI_CONFIG_LIST"))
    output = foobar_text(x)
    feedback = user(output.data)
    optimizer.zero_feedback()
    optimizer.backward(output, feedback)
    print(f"variable={x.data}, output={output.data}, feedback={feedback}")  # logging
    optimizer.step(verbose=True)

    ## Test the optimizer with an example of code
    GRAPH.clear()


    def user(output):
        if output < 0:
            return "Success."
        else:
            return "Try again. The output should be negative"


    # We make this function as a parameter that can be optimized.
    @bundle(trainable=True)
    def my_fun(x):
        """Test function"""
        return x**2 + 1


    x = node(-1, trainable=False)
    optimizer = OptoPrime([my_fun.parameter], config_list=autogen.config_list_from_json("OAI_CONFIG_LIST"))
    output = my_fun(x)
    feedback = user(output.data)
    optimizer.zero_feedback()
    optimizer.backward(output, feedback)

    print(f"output={output.data}, feedback={feedback}, variables=\n")  # logging
    for p in optimizer.parameters:
        print(p.name, p.data)
    optimizer.step(verbose=True)


    # Test directly providing feedback to parameters
    GRAPH.clear()
    x = node(-1, trainable=True)
    optimizer = OptoPrime([x])
    feedback = "test"
    optimizer.zero_feedback()
    optimizer.backward(x, feedback)
    optimizer.step(verbose=True)


    # Test if we can save log in both pickle and json
    import json, pickle
    json.dump(optimizer.log, open("log.json", "w"))
    pickle.dump(optimizer.log, open("log.pik", "wb"))
    # remove these files
    import os
    os.remove("log.json")
    os.remove("log.pik")