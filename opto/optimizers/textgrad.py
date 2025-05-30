import json
from dataclasses import dataclass
from typing import Any, List, Dict, Union, Tuple, Optional
from opto.optimizers.optimizer import Optimizer
from opto.trace.nodes import ParameterNode, Node, MessageNode
from opto.trace.propagators import TraceGraph, GraphPropagator, Propagator
from opto.trace.utils import escape_json_nested_quotes, remove_non_ascii
from opto.utils.llm import LLM, AbstractModel

from copy import copy
import re

from textwrap import dedent, indent
from collections import defaultdict

"""
Prompts are taken verbatim from:
https://github.com/zou-group/textgrad/blob/main/textgrad/optimizer/optimizer_prompts.py

Optimizer implementation loosely adapted from
https://github.com/zou-group/textgrad/blob/main/textgrad/optimizer/optimizer.py
"""

GLOSSARY_TEXT = """
### Glossary of tags that will be sent to you:
# - <LM_INPUT>: The input to the language model.
# - <LM_OUTPUT>: The output of the language model.
# - <FEEDBACK>: The feedback to the variable.
# - <CONVERSATION>: The conversation history.
# - <FOCUS>: The focus of the optimization.
# - <ROLE>: The role description of the variable."""

### Optimize Prompts

# System prompt to TGD
OPTIMIZER_SYSTEM_PROMPT = (
    "You are part of an optimization system that improves text (i.e., variable). "
    "You will be asked to creatively and critically improve prompts, solutions to problems, code, or any other text-based variable. "
    "You will receive some feedback, and use the feedback to improve the variable. "
    "The feedback may be noisy, identify what is important and what is correct. "
    "Pay attention to the role description of the variable, and the context in which it is used. "
    "This is very important: You MUST give your response by sending the improved variable between {new_variable_start_tag} {{improved variable}} {new_variable_end_tag} tags. "
    "The text you send between the tags will directly replace the variable.\n\n"
    f"{GLOSSARY_TEXT}"
)

# TGD update instruction
TGD_PROMPT_PREFIX = (
    "Here is the role of the variable you will improve: <ROLE>{variable_desc}</ROLE>.\n\n"
    "The variable is the text within the following span: <VARIABLE> {variable_short} </VARIABLE>\n\n"
    "Here is the context and feedback we got for the variable:\n\n"
    "<CONTEXT>{variable_grad}</CONTEXT>\n\n"
    "Improve the variable ({variable_desc}) using the feedback provided in <FEEDBACK> tags.\n"
)

# If the gradients are in a multi-part container
TGD_MULTIPART_PROMPT_INIT = (
    "Here is the role of the variable you will improve: <ROLE>{variable_desc}</ROLE>.\n\n"
    "The variable is the text within the following span: <VARIABLE> {variable_short} </VARIABLE>\n\n"
    "Here is the context and feedback we got for the variable:\n\n"
)

TGD_MULTIPART_PROMPT_PREFIX = "Improve the variable ({variable_desc}) using the feedback provided in <FEEDBACK> tags.\n"

TGD_PROMPT_SUFFIX = (
    "Send the improved variable "
    "in the following format:\n\n{new_variable_start_tag}{{the improved variable}}{new_variable_end_tag}\n\n"
    "Send ONLY the improved variable between the <IMPROVED_VARIABLE> tags, and nothing else."
)

MOMENTUM_PROMPT_ADDITION = (
    "Here are the past iterations of this variable:\n\n"
    "<PAST_ITERATIONS>{past_values}</PAST_ITERATIONS>\n\n"
    "Similar feedbacks across different steps suggests that the modifications to the variable are insufficient."
    "If this is the case, please make more significant changes to the variable.\n\n"
)

CONSTRAINT_PROMPT_ADDITION = (
    "You must follow the following constraints:\n\n"
    "<CONSTRAINTS>{constraint_text}</CONSTRAINTS>\n\n"
)

IN_CONTEXT_EXAMPLE_PROMPT_ADDITION = (
    "You must base on the following examples when modifying the {variable_desc}:\n\n"
    "<EXAMPLES>{in_context_examples}</EXAMPLES>\n\n"
)


def construct_tgd_prompt(
    do_momentum: bool = False,
    do_constrained: bool = False,
    do_in_context_examples: bool = False,
    **optimizer_kwargs,
):
    """
    Construct the textual gradient descent prompt.

    :param do_momentum: Whether to include momentum in the prompt.
    :type do_momentum: bool, optional
    :param do_constrained: Whether to include constraints in the prompt.
    :type do_constrained: bool, optional
    :param do_in_context_examples: Whether to include in-context examples in the prompt.
    :type do_in_context_examples: bool, optional
    :param optimizer_kwargs: Additional keyword arguments for formatting the prompt. These will be things like the variable description, gradient, past values, constraints, and in-context examples.
    :return: The TGD update prompt.
    :rtype: str
    """

    if isinstance(optimizer_kwargs["variable_grad"], str):
        multipart = False
        prompt = TGD_PROMPT_PREFIX.format(**optimizer_kwargs)

    else:
        gradient_context = optimizer_kwargs["variable_grad"]
        gradient_context = [
            TGD_MULTIPART_PROMPT_INIT.format(**optimizer_kwargs)
        ] + gradient_context
        multipart = True
        prompt = TGD_MULTIPART_PROMPT_PREFIX.format(**optimizer_kwargs)

    if do_momentum:
        prompt += MOMENTUM_PROMPT_ADDITION.format(**optimizer_kwargs)

    if do_constrained:
        prompt += CONSTRAINT_PROMPT_ADDITION.format(**optimizer_kwargs)

    if do_in_context_examples:
        prompt += IN_CONTEXT_EXAMPLE_PROMPT_ADDITION.format(**optimizer_kwargs)

    prompt += TGD_PROMPT_SUFFIX.format(**optimizer_kwargs)

    if not multipart:
        return prompt

    else:
        return gradient_context + [prompt]


GRADIENT_TEMPLATE = (
    "Here is a conversation:\n\n<CONVERSATION>{context}</CONVERSATION>\n\n"
    "This conversation is potentially part of a larger system. The output is used as {response_desc}\n\n"
    "Here is the feedback we got for {variable_desc} in the conversation:\n\n<FEEDBACK>{feedback}</FEEDBACK>\n\n"
)
GRADIENT_MULTIPART_TEMPLATE = (
    "Above is a conversation with a language model.\n"
    "This conversation is potentially part of a larger system. The output is used as {response_desc}\n\n"
    "Here is the feedback we got for {variable_desc} in the conversation:\n\n<FEEDBACK>{feedback}</FEEDBACK>\n\n"
)

"""
https://github.com/zou-group/textgrad/blob/main/textgrad/autograd/llm_ops.py
https://github.com/zou-group/textgrad/blob/main/textgrad/autograd/llm_backward_prompts.py
"""

GLOSSARY_TEXT_BACKWARD = """
### Glossary of tags that will be sent to you:
# - <LM_INPUT>: The input to the language model.
# - <LM_OUTPUT>: The output of the language model.
# - <OBJECTIVE_FUNCTION>: The objective of the optimization task.
# - <VARIABLE>: Specifies the span of the variable.
# - <ROLE>: The role description of the variable."""

### Backward engine prompts

# System prompt to the backward engine.
BACKWARD_SYSTEM_PROMPT = (
    "You are part of an optimization system that improves a given text (i.e. the variable). You are the gradient (feedback) engine. "
    "Your only responsibility is to give intelligent and creative feedback and constructive criticism to variables, given an objective specified in <OBJECTIVE_FUNCTION> </OBJECTIVE_FUNCTION> tags. "
    "The variables may be solutions to problems, prompts to language models, code, or any other text-based variable. "
    "Pay attention to the role description of the variable, and the context in which it is used. You should assume that the variable will be used in a similar context in the future. "
    "Only provide strategies, explanations, and methods to change in the variable. DO NOT propose a new version of the variable, that will be the job of the optimizer. Your only job is to send feedback and criticism (compute 'gradients'). "
    "For instance, feedback can be in the form of 'Since language models have the X failure mode...', 'Adding X can fix this error because...', 'Removing X can improve the objective function because...', 'Changing X to Y would fix the mistake ...', that gets at the downstream objective.\n"
    "If a variable is already working well (e.g. the objective function is perfect, an evaluation shows the response is accurate), you should not give feedback.\n"
    f"{GLOSSARY_TEXT_BACKWARD}"
)

# First part of the prompt for the llm backward function
CONVERSATION_TEMPLATE = (
    "<LM_INPUT> {prompt} </LM_INPUT>\n\n"
    "<LM_OUTPUT> {response_value} </LM_OUTPUT>\n\n"
)

# Has the gradient on the output.
CONVERSATION_START_INSTRUCTION_CHAIN = (
    "You will give feedback to a variable with the following role: <ROLE> {variable_desc} </ROLE>. "
    "Here is a conversation with a language model (LM):\n\n"
    "{conversation}"
)
OBJECTIVE_INSTRUCTION_CHAIN = (
    "This conversation is part of a larger system. The <OP_OUTPUT> was later used as {response_desc}.\n\n"
    "<OBJECTIVE_FUNCTION>Your goal is to give feedback to the variable to address the following feedback on the LM_OUTPUT: {response_gradient} </OBJECTIVE_FUNCTION>\n\n"
)

# Does not have gradient on the output
CONVERSATION_START_INSTRUCTION_BASE = (
    "You will give feedback to a variable with the following role: <ROLE> {variable_desc} </ROLE>. "
    "Here is an evaluation of the variable using a language model:\n\n"
    "{conversation}"
)

OBJECTIVE_INSTRUCTION_BASE = (
    "<OBJECTIVE_FUNCTION>Your goal is to give feedback and criticism to the variable given the above evaluation output. "
    "Our only goal is to improve the above metric, and nothing else. </OBJECTIVE_FUNCTION>\n\n"
)

# Third part of the prompt for the llm backward function.
# Asks the user to evaluate a variable in the conversation.
EVALUATE_VARIABLE_INSTRUCTION = (
    "We are interested in giving feedback to the {variable_desc} "
    "for this conversation. Specifically, give feedback to the following span "
    "of text:\n\n<VARIABLE> "
    "{variable_short} </VARIABLE>\n\n"
    "Given the above history, describe how the {variable_desc} "
    "could be improved to improve the <OBJECTIVE_FUNCTION>. Be very creative, critical, and intelligent.\n\n"
)

SEARCH_QUERY_BACKWARD_INSTRUCTION = (
    "Here is a query and a response from searching with {engine_name}:\n"
    "<QUERY> {query} </QUERY>\n"
    "<RESULTS> {results} </RESULTS>\n\n"
)

GRADIENT_OF_RESULTS_INSTRUCTION = (
    "For the search results from {engine_name} we got the following feedback:\n\n"
    "<FEEDBACK>{results_gradient}</FEEDBACK>\n\n"
)


"""
Gradient accumulation: reduce / sum
"""

REDUCE_MEAN_SYSTEM_PROMPT = (
    "You are part of an optimization system that improves a given text (i.e. the variable). "
    "Your only responsibility is to critically aggregate and summarize the feedback from sources. "
    "The variables may be solutions to problems, prompts to language models, code, or any other text-based variable. "
    "The multiple sources of feedback will be given to you in <FEEDBACK> </FEEDBACK> tags. "
    "When giving a response, only provide the core summary of the feedback. Do not recommend a new version for the variable -- only summarize the feedback critically. "
)


@dataclass
class GradientInfo:
    gradient: str  # feedback
    gradient_context: Optional[Dict[str, str]]

    def __len__(self):
        if self.gradient_context is None:
            return 1
        else:
            return 2

    def __getitem__(self, key):
        if key == 0:
            return self.gradient
        elif key == 1:
            return self.gradient_context
        else:
            raise IndexError


def construct_reduce_prompt(gradients: List[GradientInfo]):
    """
    Construct a prompt that reduces the gradients.
    """
    gradient_texts = []
    for i, gradient in enumerate(gradients):
        gradient_texts.append(f"<FEEDBACK>{gradient}</FEEDBACK>")
    gradient_texts = "\n".join(gradient_texts)

    return gradient_texts


def rm_node_attrs(text: str) -> str:
    """
    Removes trace node attributes (text inside square brackets) from a string.

    Args:
        text: Input string that may contain trace node attributes like [ParameterNode]

    Returns:
        String with trace node attributes removed
    """
    return re.sub(r"\[.*?\]", "", text).strip()


def get_short_value(text, n_words_offset: int = 10) -> str:
    """
    Returns a short version of the value of the variable. We sometimes use it during optimization, when we want to see the value of the variable, but don't want to see the entire value.
    This is sometimes to save tokens, sometimes to reduce repeating very long variables, such as code or solutions to hard problems.
    :param n_words_offset: The number of words to show from the beginning and the end of the value.
    :type n_words_offset: int
    """
    if type(text) != str:
        text = str(text)

    words = text.split(" ")
    if len(words) <= 2 * n_words_offset:
        return text
    short_value = (
        " ".join(words[:n_words_offset]) + " (...) " + " ".join(words[-n_words_offset:])
    )
    return short_value


class TextGrad(Optimizer):

    def __init__(
        self,
        parameters: List[ParameterNode],
        llm: AbstractModel = None,
        *args,
        propagator: Propagator = None,
        objective: Union[None, str] = None,
        max_tokens=4096,
        log=False,
        **kwargs,
    ):
        super().__init__(parameters, *args, **kwargs)
        self.llm = llm or LLM()
        self.print_limit = 100
        self.max_tokens = max_tokens
        self.new_variable_tags = ["<IMPROVED_VARIABLE>", "</IMPROVED_VARIABLE>"]
        self.optimizer_system_prompt = OPTIMIZER_SYSTEM_PROMPT.format(
            new_variable_start_tag=self.new_variable_tags[0],
            new_variable_end_tag=self.new_variable_tags[1],
        )
        self.log = [] if log else None

    def _construct_backward_prompt(self, backward_info):
        conversation = CONVERSATION_TEMPLATE.format(**backward_info)
        backward_prompt = CONVERSATION_START_INSTRUCTION_BASE.format(
            conversation=conversation, **backward_info
        )
        backward_prompt += OBJECTIVE_INSTRUCTION_BASE.format(**backward_info)
        backward_prompt += EVALUATE_VARIABLE_INSTRUCTION.format(**backward_info)
        return backward_prompt

    def _construct_chain_backward_prompt(self, backward_info) -> str:
        conversation = CONVERSATION_TEMPLATE.format(**backward_info)
        backward_prompt = CONVERSATION_START_INSTRUCTION_CHAIN.format(
            conversation=conversation, **backward_info
        )
        backward_prompt += OBJECTIVE_INSTRUCTION_CHAIN.format(**backward_info)
        backward_prompt += EVALUATE_VARIABLE_INSTRUCTION.format(**backward_info)
        return backward_prompt

    def _grad(
        self, input_node: Node, parent_nodes, gradient_text, verbose=False
    ) -> List[GradientInfo]:
        """
        https://github.com/zou-group/textgrad/blob/main/textgrad/autograd/llm_ops.py#L174

        input_node is the response node
        parent_nodes are the children_variables (predecessors)

        :param gradient_text: previous feedback
        """
        propagated_grads = []
        for var_node in parent_nodes:
            backward_info = {
                "response_desc": rm_node_attrs(input_node.description),
                "response_value": input_node.data,
                "response_gradient": gradient_text,
                "prompt": var_node.data,  # prompt = input to the operation
                "variable_desc": rm_node_attrs(var_node.description),
                "variable_short": get_short_value(var_node.data),
            }
            backward_prompt = self._construct_chain_backward_prompt(backward_info)
            gradient_value = self.call_llm(
                user_prompt=backward_prompt,
                system_prompt=BACKWARD_SYSTEM_PROMPT,
                verbose=verbose,
            )
            conversation = CONVERSATION_TEMPLATE.format(**backward_info)
            gradients_context = {
                "context": conversation,
                "response_desc": rm_node_attrs(input_node.description),
                "variable_desc": rm_node_attrs(var_node.description),
            }
            propagated_grads.append(GradientInfo(gradient_value, gradients_context))

        return propagated_grads

    def _reduce_gradient_mean(self, gradients: List[GradientInfo], verbose=False):
        if len(gradients) == 1:
            return gradients[0]
        else:
            gradient_reduce_prompt = construct_reduce_prompt(gradients)
            reduced_gradient = self.call_llm(
                user_prompt=gradient_reduce_prompt,
                system_prompt=REDUCE_MEAN_SYSTEM_PROMPT,
                verbose=verbose,
            )
            return reduced_gradient

    def _get_gradient_and_context_text(self, gradients: List[GradientInfo]):
        gradient_content = []
        for g in gradients:
            if g.gradient_context is None:
                gradient_content.append(g.gradient)
            else:
                criticism_and_context = GRADIENT_TEMPLATE.format(
                    feedback=g.gradient, **g.gradient_context
                )
                gradient_content.append(criticism_and_context)
        return "\n".join(gradient_content)

    def _update_prompt(self, node: Node, gradients: List[GradientInfo]):
        # gradient_memory: just accumulated gradient from the previous calculation
        optimizer_information = {
            "variable_desc": rm_node_attrs(node.description),
            "variable_value": node.data,
            "variable_grad": self._get_gradient_and_context_text(gradients),
            "variable_short": get_short_value(node.data),
            "constraint_text": node._constraint,
            "new_variable_start_tag": self.new_variable_tags[0],
            "new_variable_end_tag": self.new_variable_tags[1],
            # "in_context_examples": "\n".join(self.in_context_examples),
            # "gradient_memory": gradient_memory
        }

        prompt = construct_tgd_prompt(
            do_constrained=True,
            do_in_context_examples=False,
            do_gradient_memory=False,
            **optimizer_information,
        )

        return prompt

    def _step(self, verbose=False):
        # aggregate the trace graphes into one.
        trace_graph = copy(self.trace_graph)

        # this is the same as gradient memory
        grads = defaultdict(
            list
        )  # accumulated gradient (same as variable.get_gradient_text())

        # trace_graph.graph is a list of nodes sorted according to the topological order
        for i, (_, x) in enumerate(
            reversed(trace_graph.graph)
        ):  # back-propagation starts from the last node
            if len(x.parents) == 0:
                continue
            # we take the gradient step-by-step
            g = GradientInfo(trace_graph.user_feedback, None) if i == 0 else grads[x]
            if len(g) > 1:
                # reduce step
                g = self._reduce_gradient_mean(g, verbose=verbose)
                if verbose not in (False, "output"):
                    print(f"Reduced gradient for {x.py_name}: {g}")
                grads[x] = [g]

            # compute gradient
            propagated_grads = self._grad(x, x.parents, g)
            if verbose not in (False, "output"):
                print(f"Propagated gradients for {x.py_name}: {propagated_grads}")

            for p, pg in zip(x.parents, propagated_grads):
                # accumulate gradient (append to list)
                grads[p].append(pg)  # accumulate gradient

        # apply gradient
        update_dict = {}
        for p in self.parameters:
            gradients = grads[p]
            prompt_update_parameter = self._update_prompt(p, gradients)
            response = self.call_llm(
                user_prompt=prompt_update_parameter,
                system_prompt=self.optimizer_system_prompt,
                verbose=verbose,
            )
            try:
                var_json = (
                    response.split(self.new_variable_tags[0])[1]
                    .split(self.new_variable_tags[1])[0]
                    .strip()
                )
                # processing to fix JSON
                # var_json = remove_non_ascii(escape_json_nested_quotes(var_json).replace("\n", "\\n"))
                # new_proposal = json.loads(var_json)
                # update_dict[p] = type(p.data)(new_proposal['value'])
                update_dict[p] = type(p.data)(var_json)
                if verbose not in (False, "output"):
                    # old value to new value
                    print(f"Updated {p.py_name} from {p.data} to {update_dict[p]}")
            except Exception as e:
                print(f"Error in updating {p.py_name}: {e}, raw response: {response}")

        if self.log is not None:
            self.log.append(
                {"user_prompt": prompt_update_parameter, "response": response}
            )

        return update_dict  # propose new update

    def call_llm(
        self, system_prompt: str, user_prompt: str, verbose: Union[bool, str] = False
    ):
        """Call the LLM with a prompt and return the response."""
        if verbose not in (False, "output"):
            print("Prompt\n", system_prompt + "\n\n" + user_prompt)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        try:
            response = self.llm.create(
                messages=messages,
                max_tokens=self.max_tokens,
            )
        except Exception:
            response = self.llm.create(messages=messages, max_tokens=self.max_tokens)
        response = response.choices[0].message.content

        if verbose:
            print("LLM response:\n", response)
        return response
