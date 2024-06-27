# inspired by COLLIE: https://arxiv.org/pdf/2307.08689.pdf
# pip install collie-bench

"""
The goal here is similar to number synthetic
There is a series of transformation performed on an input string
LLMs need to reason about the transformation to choose the input string carefully

As a blackbox function, it's hard to "guess" the transformation, thus requiring many trials
But with trace, we can see into the transformation, therefore, much much much easier

(This is also why it's a toy task)

We have a target string, which is revealed to the LLM

Easy Goal: target string must be in the output of the transformation
Med/High Goal: position/count of character

Flow: decide and input string, run through program, get output
use output as target.
"""

from opto.trace.nodes import node
import string
import random
import numpy as np
from textwrap import dedent

from typing import List
import copy
from opto.trace.operators import *

from functools import reduce


def reformat(program_str: str):
    # remove empty lines and leading/trailing spaces
    return dedent(program_str).strip()


unary_string_ops = ["capitalize", "lower", "upper", "swapcase", "title"]
unary_string_ops_programs = {
    "capitalize": reformat("""lambda s: s.capitalize()"""),
    "lower": reformat("""lambda s: s.lower()"""),
    "upper": reformat("""lambda s: s.upper()"""),
    "swapcase": reformat("""lambda s: s.swapcase()"""),
    "title": reformat("""lambda s: s.title()"""),
}

# split, replace, concat
string_mutation_ops = ["split", "replace", "concat"]
string_mutation_ops_programs = {
    "split": reformat("""lambda s, t: s.split(t)"""),  # 2 inputs
    "concat": reformat("""lambda s, t: s + t"""),  # 2 inputs
    "replace": reformat("""lambda s, a, b: s.replace(a, b)"""),  # 3 inputs
}

variable_name_collide_list = set()
characters = string.ascii_letters + string.digits + " "


def create_input_var(length=5):
    # sample and return a random 5 letter name
    retry = 10
    cnt = 0

    name = "node_" + "".join(random.choices(string.ascii_lowercase, k=5))

    while name in variable_name_collide_list and cnt < retry:
        cnt += 1
        name = "node_" + "".join(random.choices(string.ascii_lowercase, k=5))

    value = "".join(random.choice(characters) for _ in range(length))
    return node(value, name)


def create_var():
    value = random.choice(characters)
    return value


class StringProgramSampler:
    def __init__(
        self,
        chain_length,
        param_num=1,
        # one_var_mixture=[0.8, 0.2],
        two_var_mixture=[0.8, 0.2],
        three_var_mixture=[0.5, 0.4, 0.1],
        op_mixture=[0.7, 0.3],
        max_gen_var=10,
        seed=1234,
        verbose=False,
    ):
        """
        Args:
            op_mixture: [0.7, 0.3]: probability to sample from case-switch operations, and sample from mutation operations
        """
        assert chain_length > 0, "Chain length should be positive"
        assert type(chain_length) == int
        assert type(max_gen_var) == int

        # self.mixture_assertion_check(one_var_mixture, 2)
        self.mixture_assertion_check(two_var_mixture, 2)
        self.mixture_assertion_check(three_var_mixture, 3)

        self.set_seed(seed)

        self.chain_length = chain_length
        self.max_gen_var = max_gen_var
        self.param_num = param_num

        self.op_mixture = op_mixture

        self.one_var_mixture = [1.0]
        self.two_var_mixture = two_var_mixture
        self.three_var_mixture = three_var_mixture

        self.one_input_dec_space = [(1, 0)]
        self.two_input_dec_space = [(1, 1), (2, 0)]  # , (0, 2)
        self.three_input_dec_space = [(2, 1), (1, 2), (3, 0)]  # , (0, 3)
        # (num1, num2): sample {num1} vars in input_var_space, sample {num2} in gen_var_space

        self.input_var_space = []
        self.gen_var_space = []

        self._goal_input = [create_input_var()] * param_num
        self._goal_output = self.__call__(self._goal_input, seed=seed, verbose=verbose)

        self.execution_exception = None

    @property
    def goal_input(self):
        return [i.data for i in self._goal_input]

    @property
    def goal_output(self):
        return self._goal_output.data

    def display_computation_graph(self):
        return self._goal_output.backward(visualize="True", feedback="fine")

    def feedback(self, y_hat):
        if self.execution_exception is not None:
            return "The input throws an error and is invalid. Please try another input."

        if y_hat == self._goal_output.data:
            return "Success."
        else:
            return f"The target string is {self.goal_output}, and the current output from your chosen input is {y_hat}"

    def mixture_assertion_check(self, mixture, num_elements=2):
        assert np.abs(np.sum(mixture) - 1) < 1e-6, "The mixture should sum to 1"
        assert len(mixture) == num_elements, f"The mixture should have {num_elements} elements"

    def reset(self):
        self.input_var_space = []
        self.gen_var_space = []

    def set_seed(self, seed=None):
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)

    def get_current_input(self):
        return self.input_var_space[: self.param_num]

    def sample_vars_from_space(self, var_space, num_sample, is_gen=False):
        is_gen_vars = [is_gen] * num_sample

        if num_sample == 0:
            return [], is_gen_vars

        # sampled_vars = []
        if is_gen:
            for _ in range(num_sample):
                max_curr_len = min(len(var_space), self.max_gen_var)
                prob_new_var = 1 - max_curr_len / self.max_gen_var
                if np.random.rand() < prob_new_var:
                    sampled_var = create_var()
                    var_space.append(sampled_var)
            sampled_var_idx = np.random.choice(list(range(len(var_space))), num_sample, replace=False)
            sampled_vars = [var_space[i] for i in sampled_var_idx]
        else:
            # for input_var
            # we do a probability curve that favors later items (to increase computational complexity)
            # once all input_vars have been used
            if len(self.input_var_space) > self.param_num:
                weights = np.exp(np.arange(len(self.input_var_space)))
                p = weights / np.sum(weights)
            else:
                p = [1 / len(self.input_var_space)] * len(self.input_var_space)
            sampled_var_idx = np.random.choice(list(range(len(self.input_var_space))), num_sample, p=p, replace=False)
            sampled_vars = [var_space[i] for i in sampled_var_idx]

        return sampled_vars, is_gen_vars

    def sample_vars(self, mixture_dec_space, var_mixture):
        """
        Need to decide how many vars to sample from
        """
        # need to check for legality of sampling
        # for example, we can sample from input_var_space if they don't have enough variables
        filtered_mixture_dec_space = []
        fitlered_var_mixture = []
        for i, tup in enumerate(mixture_dec_space):
            if tup[0] > len(self.input_var_space):
                continue
            filtered_mixture_dec_space.append(tup)
            fitlered_var_mixture.append(var_mixture[i])

        fitlered_var_mixture = [i / sum(fitlered_var_mixture) for i in fitlered_var_mixture]

        idx = np.random.choice(range(len(filtered_mixture_dec_space)), p=fitlered_var_mixture)
        sample_nums = filtered_mixture_dec_space[idx]

        sampled_vars, is_gen_vars = self.sample_vars_from_space(self.input_var_space, sample_nums[0], is_gen=False)
        sampled_vars2, is_gen_vars2 = self.sample_vars_from_space(self.gen_var_space, sample_nums[1], is_gen=True)

        sampled_vars += sampled_vars2
        is_gen_vars += is_gen_vars2

        # because split and replace are class methods
        # if it's a raw string "a".split(node_str), then it's a bit weird
        # so we do an additional check and conversion
        if len(sampled_vars) > 1 and is_gen_vars[0] is True:
            sampled_vars = [node(sampled_vars[0])] + sampled_vars[1:]

        return sampled_vars, is_gen_vars

    def sample_op(self, verbose):
        """
        We have caseswitch or mutation ops

        We decide which group to sample
        Then we sample the op
        Then we sample vars that meet the requirement of op

        Returns: op, (vars), is_gen_var
        """
        type_of_ops = ["unary_string_ops", "string_mutation_ops"]
        op_type = np.random.choice(type_of_ops, p=self.op_mixture)
        op_name = np.random.choice(eval(str(op_type)))
        op = eval(str(op_type) + "_programs")[op_name]

        if op_type == "unary_string_ops":
            sampled_vars, is_gen_vars = self.sample_vars(self.one_input_dec_space, self.one_var_mixture)
        elif op_name in ["split", "concat"]:
            sampled_vars, is_gen_vars = self.sample_vars(self.two_input_dec_space, self.two_var_mixture)
        elif op_name == "replace":
            sampled_vars, is_gen_vars = self.sample_vars(self.three_input_dec_space, self.three_var_mixture)
        else:
            raise ValueError("Invalid op_type")

        if verbose:
            print("Op:", op_name, "Vars from: ", is_gen_vars)

        return op, sampled_vars, is_gen_vars

    def step(self, verbose=False):
        """
        We don't have a sample_step yet, unless we want to includer logic comparators
        """
        op, vars, is_gen_vars = self.sample_op(verbose=verbose)

        out_var = eval(op)(*vars)
        out_var_is_gen = reduce(lambda x, y: x * y, is_gen_vars)

        if out_var_is_gen:
            self.gen_var_space.append(out_var)
        else:
            self.input_var_space.append(out_var)

        # we still return the value, just in case this is the final step
        return out_var

    def __call__(self, input_params: List[str], seed=1234, verbose=False):
        """
        Args:
            input_params: a list of input parameters

        Returns: the final value of the program
        """
        self.reset()

        if type(input_params) != list:
            input_params = [input_params]

        assert len(input_params) == self.param_num, "The number of input params should be the same as param_num"
        self.input_var_space += input_params

        # so we get the same computation graph actually
        # by choosing a seed
        self.set_seed(seed)

        try:
            for _ in range(self.chain_length):
                out_var = self.step(verbose)
        except Exception as e:
            self.execution_exception = repr(e)
            out_var = throws_exception(node(repr(e)), *input_params)

        return out_var
