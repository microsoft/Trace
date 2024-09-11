from typing import Any, List, Dict, Union, Tuple
from opto.optimizers.optimizer import Optimizer
from opto.trace.nodes import ParameterNode, Node, MessageNode
from opto.trace.propagators import TraceGraph, GraphPropagator, Propagator

from textwrap import dedent, indent
from collections import defaultdict

"""
Prompts are taken verbatim from:
https://github.com/zou-group/textgrad/blob/main/textgrad/optimizer/optimizer_prompts.py
"""

GLOSSARY_TEXT = """
### Glossary of tags that will be sent to you:
# - <LM_SYSTEM_PROMPT>: The system prompt for the language model.
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

TGD_MULTIPART_PROMPT_PREFIX = (
    "Improve the variable ({variable_desc}) using the feedback provided in <FEEDBACK> tags.\n"
)

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


def construct_tgd_prompt(do_momentum: bool = False,
                         do_constrained: bool = False,
                         do_in_context_examples: bool = False,
                         **optimizer_kwargs):
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
        gradient_context = [TGD_MULTIPART_PROMPT_INIT.format(**optimizer_kwargs)] + gradient_context
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
Implementation loosely adapted from
https://github.com/zou-group/textgrad/blob/main/textgrad/optimizer/optimizer.py

Because Trace Graph is heterogeneous -- we do not treat LLM operations differently from other operations,
we don't implement specialized backward operators for LLM operations.

TextGrad does treat LLM operations differently, and has specialized backward operators for LLM operations.
See:
https://github.com/zou-group/textgrad/blob/main/textgrad/autograd/llm_ops.py
https://github.com/zou-group/textgrad/blob/main/textgrad/autograd/llm_backward_prompts.py

These two parts are not re-implemented here.
"""

# def get_gradient_and_context_text(variable) -> Union[str, List[Union[str, bytes]]]:
#     """For the variable, aggregates and returns
#     i. the gradients
#     ii. the context for which the gradients are computed.
#
#     This is used by the optimizer.
#     :return: A string containing the aggregated gradients and their corresponding context.
#     :rtype: str
#     """
#
#     gradient_content = []
#     for g in variable.gradients:
#         if variable.gradients_context[g] is None:
#             gradient_content.append(g.value)
#         else:
#             # If context is a list, we handle it differently.
#             context = variable.gradients_context[g]
#             if isinstance(context["context"], str):
#                 # The context could be all string.
#                 criticism_and_context = GRADIENT_TEMPLATE.format(
#                     feedback=g.value, **context)
#                 gradient_content.append(criticism_and_context)
#             elif isinstance(context["context"], list):
#                 # The context may have a list of images / strings. In this case, we need to handle it differently.
#                 context_prompt = GRADIENT_MULTIPART_TEMPLATE.format(**context, feedback=g.value)
#                 criticism_and_context = context["context"] + [context_prompt]
#                 gradient_content.extend(criticism_and_context)
#             else:
#                 raise ValueError("Context must be either a string or a list.")
#
#     # Check if all instances are string
#     if all(isinstance(i, str) for i in gradient_content):
#         return "\n".join(gradient_content)
#     else:
#         return gradient_content

def get_gradient_context():
    pass

class TextGrad(Optimizer):

    def __init__(self, parameters: List[ParameterNode],
                 config_list: List = None,
                 *args,
                 propagator: Propagator = None,
                 objective: Union[None, str] = None,
                 ignore_extraction_error: bool = True,
                 # ignore the type conversion error when extracting updated values from LLM's suggestion
                 include_example=False,
                 memory_size=0,  # Memory size to store the past feedback
                 max_tokens=4096,
                 log=True,
                 **kwargs, ):
        super().__init__(parameters, *args, **kwargs)

    def _step(self):
        trace_graph = self.trace_graph  # aggregate the trace graphes into one.

        # this is the same as gradient memory
        grads = defaultdict(str)  # accumulated gradient (same as variable.get_gradient_text())

        # trace_graph.graph is a list of nodes sorted according to the topological order
        for i, (_, x) in enumerate(reversed(trace_graph.graph)):  # back-propagation starts from the last node
            if len(x.parents) == 0:
                continue
            # we take the gradient step-by-step
            g = trace_graph.user_feedback if i == 0 else grads[x]

            # TODO: compute gradient
            # outputs, inputs, grad_outputs=None
            propagated_grads = torch.autograd.grad(x.data, [p.data for p in x.parents], g)  # propagate the gradient

            for p, pg in zip(x.parents, propagated_grads):
                # TODO: accumulate gradient
                grads[p] += pg  # accumulate gradient

        # TODO: apply gradient
        return {p: p.data - self.stepsize * grads[p] for p in self.parameters}  # propose new update

    def call_llm(
        self, system_prompt: str, user_prompt: str, verbose: Union[bool, str] = False, max_tokens: int = 4096
    ):
        """Call the LLM with a prompt and return the response."""
        if verbose not in (False, "output"):
            print("Prompt\n", system_prompt + user_prompt)

        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]

        try:  # Try tp force it to be a json object
            response = self.llm.create(
                messages=messages,
                response_format={"type": "json_object"},
                max_tokens=max_tokens,
            )
        except Exception:
            response = self.llm.create(messages=messages, max_tokens=max_tokens)
        response = response.choices[0].message.content

        if verbose:
            print("LLM response:\n", response)
        return response

    def get_label(self, x):
        """Construct a label for a node based on its name, description, and content.

        Parameters
        ----------
        x: The node for which the label is to be constructed.

        Note
        ----------
        Using a colon in the name can cause problems in graph visualization tools like Graphviz.
        To avoid issues, the label is constructed by combining the node's Python name, truncated description, and content.
        If the description or content exceeds the print limit, it is truncated and appended with an ellipsis.
        """
        # using colon in the name causes problems in graphviz
        description = x.description
        if len(x.description) > self.print_limit:
            description = x.description[:self.print_limit] + "..."

        text = x.py_name + "\n" + description + "\n"
        content = str(x.data)
        if isinstance(x.data, dict):
            if "content" in x.data:
                content = str(x.data["content"])

        if len(content) > self.print_limit:
            content = content[:self.print_limit] + "..."
        return text + content

    def _update_prompt(self, node: Node, input_nodes, gradient_memory):
        # gradient_memory: just accumulated gradient from the previous calculation
        optimizer_information = {
            "variable_desc": node.description,
            "variable_value": node.data,
            "variable_grad": get_gradient_and_context_text(variable),
            "variable_short": node.py_name,
            "constraint_text": self.constraint_text,
            "new_variable_start_tag": self.new_variable_tags[0],
            "new_variable_end_tag": self.new_variable_tags[1],
            "in_context_examples": "\n".join(self.in_context_examples),
            "gradient_memory": gradient_memory
        }

        prompt = construct_tgd_prompt(do_constrained=self.do_constrained,
                                      do_in_context_examples=(
                                                  self.do_in_context_examples and (len(self.in_context_examples) > 0)),
                                      do_gradient_memory=(self.do_gradient_memory and (grad_memory != "")),
                                      **optimizer_information)