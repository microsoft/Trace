"""
Lisp Interpreter
The ablation part: we specify how complete the 21 functions are. The more complete, the less LLM needs to do.

This requires us to override and implement all the functions required by the Lisp Interpreter.

https://arxiv.org/pdf/2212.10561.pdf

Backup task: Robotic planning

Think about how you can "ablate" this...ok, we write two versions of the function, both are traced
and we just load whichever one we decide.

Original Parsel needs to backtrack and do error trace, and few-shot demonstration
We are making this task harder
"""

from opto.trace.nodes import node, GRAPH
from opto.trace.bundle import FunModule, bundle
from opto.trace.nodes import Node

import math
import random


def get_math():
    d = {}
    for name in dir(math):
        if name[:2] != "__":
            d[name] = getattr(math, name)
    return d


def get_ops():
    return {
        "+": (lambda x, y: x + y),
        "-": (lambda x, y: x - y),
        "*": (lambda x, y: x * y),
        "/": (lambda x, y: x / y),
        ">": (lambda x, y: x > y),
        "<": (lambda x, y: x < y),
        ">=": (lambda x, y: x >= y),
        "<=": (lambda x, y: x <= y),
        "=": (lambda x, y: x == y),
    }


def get_simple_math():
    return {"abs": abs, "min": min, "max": max, "not": lambda x: not x, "round": round}


def standard_env(includes=["math", "ops", "simple_math"]):
    env = {"_outer": None}
    if "math" in includes:
        env.update(get_math())
    if "ops" in includes:
        env.update(get_ops())
    if "simple_math" in includes:
        env.update(get_simple_math())
    return env


class Environment(dict):
    "An environment: a dict of {'var': val} pairs, with an outer Env."

    def __init__(self, parms=(), args=(), outer=None):
        for p, a in zip(parms, args):
            if isinstance(a, Node):
                a = a.data
            if isinstance(p, Node):
                p = p.data
            self[p] = a

        if isinstance(outer, Node):
            outer = outer.data

        self.outer = outer

    def find(self, var):
        "Find the innermost Env where var appears."
        if isinstance(var, Node):
            var = var.data
        return self if (var in self) else self.outer.find(var)

    def __setitem__(self, key, value):
        if isinstance(value, Node):
            value = value.data
        if isinstance(key, Node):
            key = key.data
        super().__setitem__(key, value)


global_env = Environment()
global_env.update(standard_env())


@bundle(description="[tokenize] Convert a string of characters into a list of tokens.")
def tokenize(chars):
    "Convert a string of characters into a list of tokens."
    return chars.replace("(", " ( ").replace(")", " ) ").split()


@bundle(description="[parse] Read a Scheme expression from a string.")
def parse(program):
    return read_from_tokens(tokenize(program))


@bundle(description="[read_from_tokens] Read an expression from a sequence of tokens.")
def read_from_tokens(tokens):
    if len(tokens) == 0:
        raise SyntaxError("unexpected EOF while reading")

    stack = []
    current_list = []

    for token in tokens:
        if token == "(":
            # Start a new sublist and push it onto the stack
            stack.append(current_list)
            current_list = []
        elif token == ")":
            # End the current sublist
            if not stack:
                raise SyntaxError("unexpected )")
            last_list = current_list
            current_list = stack.pop()
            current_list.append(last_list)
        else:
            # Normal token, add to the current sublist
            current_list.append(atom(token))

    if stack:
        raise SyntaxError("unexpected EOF while reading: missing )")

    return current_list[0]  # Return the fully parsed expression


@bundle(description="[atom] Numbers become numbers; every other token is a symbol.")
def atom(token):
    try:
        return int(token)
    except ValueError:
        try:
            return float(token)
        except ValueError:
            return token


def eval_expression(x, env=global_env):
    "Evaluate an expression in an environment."
    # we first unpack

    if isinstance(x, str):
        return env.find(x)[x]
    elif not isinstance(x, list):
        return x

    op, *args = x
    if op == "quote":
        return args[0]
    elif op == "define":
        (name, exp) = args
        env[name] = eval_expression(exp, env)
    elif op == 'lambda':
        (parms, body) = args
        return lambda *args: eval_expression(body, Environment(parms, args, env))
    elif op == 'if':
        (test, conseq, alt) = args
        exp = conseq if eval_expression(test, env) else alt
        return eval_expression(exp, env)
    else:
        proc = eval_expression(op, env)
        vals = [eval_expression(arg, env) for arg in args]
        return proc(*vals)


test_program = [
    "(define r 10)",
    "(define circle-area (lambda (r) (* pi (* r r))))",
    "(circle-area 3)",
    "(quote (1 2 3))",
    "(if (> 10 20) (quote true) (quote false))",
]

# global_env = node(global_env)
def recursive_unpack(parsed_exp):
    # can be of structure Node([Node(), Node()]) or Node(Node())
    # but can go very deep
    if isinstance(parsed_exp, Node):
        parsed_exp = parsed_exp.data
    if not isinstance(parsed_exp, list):
        return parsed_exp
    return [recursive_unpack(exp) for exp in parsed_exp]

for expr in test_program:
    parsed_exp = parse(expr)
    unpacked_exp = recursive_unpack(parsed_exp)  # Outputs for each expression
    print(unpacked_exp)
    result = eval_expression(unpacked_exp, global_env)
    print(result)  # Outputs for each expression
