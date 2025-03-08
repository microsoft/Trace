import re
import copy
import json
import numpy as np
from textwrap import dedent
from typing import Dict, List, Any, Union
from opto import trace
from opto.trace.nodes import ParameterNode
from opto.optimizers.utils import print_color
from opto.trainer.algorithms import MinibatchAlg
from opto.trainer.algorithms.basic_algorithm import standard_optimization_step
from opto.utils.llm import LLM, AbstractModel


class AggregatedUpdate(MinibatchAlg):
    """ The algorithm applies the optimizer to propose updates for each instance in the minibatch independently.
        The updates are then aggregated using an LLM and applied to the agent.
    """

    aggregator_system_prompt = f"""You are an expert in aggregating suggestions. You will see a list of suggestions of parameters from different people (denoted as #SuggestedValue_i). A parameter is represented as a dict, where the key is the name of a parameter component, and the value is the component value.

        Your task is to aggregate the suggestions and provide a new value for the parameter. Please consider the following:
        1. Make sure the new values in the dict is in the same format as the values in the dict of the suggested parameters.
        2. Provide a new value to consolidate the suggestions considering on their confidence scores. The suggestions can be wrong (especially the ones with low confidence).
        3. When aggregating, try to find the common ground between the suggestions.


        Output_format: Your output should be in the following json format, satisfying the json syntax:

            {{
            "reasoning_<component_1>": <Your reasoning>,
            "reasoning_<component_2>": <Your reasoning>,
            "suggestion": {{
                <component_1>: <suggested_value_1>,
                <component_2>: <suggested_value_2>,
            }}
            }}

            In "reasoning", explain the problem your thought process and how you arrive at the new value.

            In "suggestion", write down the suggested values. For each key in #CurrentValue, you should write the new value in the format of python code without syntax errors. If you don't want to change a variable, just write down its current value.

            If no changes or answer are needed, just output TERMINATE.
        """

    def __init__(self,
                agent,
                optimizer,
                use_asyncio: bool = True,  # whether to use asyncio to evaluate the agent
                logger = None,
                llm: AbstractModel = None,
                max_tokens: int = 4096,
                *args,
                **kwargs,
                ):
        super().__init__(agent, optimizer, logger=logger, use_asyncio=use_asyncio, *args, **kwargs)
        self.llm = llm or LLM()  # for the aggregator
        self.max_tokens = max_tokens  # for the aggregator


    def train(self,
              guide,
              train_dataset,
              *,
              stepsize = 0.5, # the stepsize for the update (used by the aggregator)
              num_epochs: int = 1,  # number of training epochs
              batch_size: int = 1,  # batch size for updating the agent
              test_dataset = None,  # dataset of (x, info) pairs to evaluate the agent
              eval_frequency: int = 1,  # frequency of evaluation
              log_frequency: Union[int, None] = None,  # frequency of logging
              min_score: Union[int, None] = None,  # minimum score to update the agent
              verbose: Union[bool, str] = False,  # whether to print the output of the agent
              **kwargs
              ):

        assert stepsize >= 0 and stepsize <= 1
        self.stepsize = stepsize  # used in self.aggregate

        super().train(guide, train_dataset, num_epochs=num_epochs, batch_size=batch_size,
                      test_dataset=test_dataset, eval_frequency=eval_frequency,
                      log_frequency=log_frequency, min_score=min_score,
                      verbose=verbose, **kwargs)


    def forward(self, agent, x, guide, info, verbose=False):
        """ Run the agent, compute feedback and return the new parameters for an instance in the minibatch. """
        target, score, feedback = standard_optimization_step(self.agent, x, guide, info, min_score=None)
        self.optimizer.zero_feedback()
        self.optimizer.backward(target, feedback)
        update_dict = self.optimizer.step(verbose=verbose, bypassing=True)
        return self.to_param_dict(update_dict), score

    def to_param_dict(self, update_dict):
        """ Convert the update the dict {ParameterNode:Any} to a dict {str:Any}. """
        return {k.py_name: v for k, v in update_dict.items()}

    def update(self, outputs, verbose=False):
        """ Ask LLM to aggregate the new parameter suggestions. """

        # Prepare the new parameters and scores
        new_parameters = []
        scores = []
        for update_dict, score in outputs:
            new_parameters.append(update_dict)
            scores.append(score)

        average_score = np.mean(scores) if all([s is not None for s in scores]) else None

        # Construct user prompt
        p0 = {n.py_name: n.data for n in self.optimizer.parameters}  # the current parameters
        user_prompt = f'#SuggestedValue_0 (confidence {1-self.stepsize}):\n{p0}\n\n'
        for i, p in enumerate(new_parameters):
            # Fill in the missing keys
            for k, v in p0.items():
                if k not in p:
                    p[k] = v
            user_prompt += f"#SuggestedValue_{i+1} (confidence {self.stepsize}):\n{p}\n\n\n"

        messages = [
            {"role": "system", "content": self.aggregator_system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        response = self.llm(
                messages=messages,
                response_format={"type": "json_object"},
                max_tokens=self.max_tokens,
            )
        response = response.choices[0].message.content

        if verbose:
            if verbose is True:
                print("Aggregator User Prompt:")
                print(user_prompt)
            print("Aggregator Response:")
            print_color(response, 'blue')

        update_dict = construct_update_dict(self.optimizer.parameters, extract_llm_suggestion(response))
        self.optimizer.update(update_dict)

        return average_score



# These two helper functions are extracted from OptoPrime
def construct_update_dict(
        parameters: List[ParameterNode], suggestion: Dict[str, Any], ignore_extraction_error: bool = True
    ) -> Dict[ParameterNode, Any]:
    """Convert the suggestion in text into the right data type."""
    # TODO: might need some automatic type conversion
    update_dict = {}
    for node in parameters:
        if node.trainable and node.py_name in suggestion:
            try:
                update_dict[node] = type(node.data)(suggestion[node.py_name])
            except (ValueError, KeyError) as e:
                # catch error due to suggestion missing the key or wrong data type
                if ignore_extraction_error:
                    warnings.warn(
                        f"Cannot convert the suggestion '{suggestion[node.py_name]}' for {node.py_name} to the right data type"
                    )
                else:
                    raise e
    return update_dict


def extract_llm_suggestion(response: str, ignore_extraction_error: bool = True) -> Dict[str, Any]:
    """Extract the suggestion from the response."""
    suggestion = {}
    attempt_n = 0
    while attempt_n < 2:
        try:
            suggestion = json.loads(response)["suggestion"]
            break
        except json.JSONDecodeError:
            # Remove things outside the brackets
            response = re.findall(r"{.*}", response, re.DOTALL)
            if len(response) > 0:
                response = response[0]
            attempt_n += 1
        except Exception:
            attempt_n += 1

    if not isinstance(suggestion, dict):
        suggestion = {}

    if len(suggestion) == 0:
        # we try to extract key/value separately and return it as a dictionary
        pattern = r'"suggestion"\s*:\s*\{(.*?)\}'
        suggestion_match = re.search(pattern, str(response), re.DOTALL)
        if suggestion_match:
            suggestion = {}
            # Extract the entire content of the suggestion dictionary
            suggestion_content = suggestion_match.group(1)
            # Regex to extract each key-value pair;
            # This scheme assumes double quotes but is robust to missing commas at the end of the line
            pair_pattern = r'"([a-zA-Z0-9_]+)"\s*:\s*"(.*)"'
            # Find all matches of key-value pairs
            pairs = re.findall(pair_pattern, suggestion_content, re.DOTALL)
            for key, value in pairs:
                suggestion[key] = value

    if len(suggestion) == 0:
        if not ignore_extraction_error:
            print("Cannot extract suggestion from LLM's response:")
            print(response)

    # if the suggested value is a code, and the entire code body is empty (i.e., not even function signature is present)
    # then we remove such suggestion
    keys_to_remove = []
    for key, value in suggestion.items():
        if "__code" in key and value == "":
            keys_to_remove.append(key)
    for key in keys_to_remove:
        del suggestion[key]

    return suggestion