import re
from difflib import SequenceMatcher

import autogen

class LLMCallable:
    def __init__(self, config_list=None, max_tokens=1024, verbose=False):
        if config_list is None:
            config_list = autogen.config_list_from_json("OAI_CONFIG_LIST")
        self.llm = autogen.OpenAIWrapper(config_list=config_list)
        self.max_tokens = max_tokens
        self.verbose = verbose

    def call_llm(self, user_prompt):
        """
        Sends the constructed prompt (along with specified request) to an LLM.
        """
        system_prompt = "You are a helpful assistant.\n"
        if self.verbose not in (False, "output"):
            print("Prompt\n", system_prompt + user_prompt)

        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]

        try:
            response = self.llm.create(
                messages=messages,
                response_format={"type": "json_object"},
            )
        except Exception:
            response = self.llm.create(messages=messages, max_tokens=self.max_tokens)
        response = response.choices[0].message.content

        if self.verbose:
            print("LLM response:\n", response)
        return response

class BaseUtil:

    def extract_actions(self, text):
        pattern = re.compile(r'([A-Z])\. (\[.*?\](?: <.*?> \(\d+\))?(?:: .*?)?)')
        matches = pattern.findall(text)
        actions = {letter: action for letter, action in matches}
        return actions

    def unify_and_match_action(self, action_str, available_actions):
        # Remove trailing periods and leading action letters if present
        action_str = action_str.strip('.')

        # Check if action_str is just a letter
        if len(action_str) == 1 and action_str in available_actions:
            return available_actions[action_str]

        # Extract the actual action part from complex strings
        match = re.search(r'\[(.*?)\] <(.*?)> \((.*?)\)', action_str)
        if match:
            action_type, action_object, action_id = match.groups()
            action = f"[{action_type}] <{action_object}> ({action_id})"

            # Check for an exact match in available actions
            if action in available_actions.values():
                return action

            # Fuzzy match if exact match is not found
            return self.fuzzy_match_action(action, available_actions)

        return action_str  # Return the cleaned up action string if no complex format is detected

    def fuzzy_match_action(self, returned_action, available_actions):
        # Extract the action and object id from the returned action
        returned_match = re.search(r'\[(.*?)\] <(.*?)> \((.*?)\)', returned_action)
        if not returned_match:
            return None

        returned_action_type, returned_object, returned_id = returned_match.groups()

        # Initialize best match variables
        best_match = None
        highest_ratio = 0

        # Iterate over available actions to find the closest match
        for action in available_actions.values():
            match = re.search(r'\[(.*?)\] <(.*?)> \((.*?)\)', action)
            if match:
                action_type, action_object, action_id = match.groups()
                if action_id == returned_id and action_object == returned_object:
                    ratio = SequenceMatcher(None, returned_action_type, action_type).ratio()
                    if ratio > highest_ratio:
                        highest_ratio = ratio
                        best_match = action

        return best_match