from typing import Any, List, Dict, Union, Tuple, Optional
import json
from textwrap import dedent

from opto.trace.propagators import GraphPropagator
from opto.optimizers.optoprime import OptoPrime


class OptoPrimeMulti(OptoPrime):
    def __init__(
        self,
        *args,
        num_responses: int = 5,
        temperature_range: Optional[List[float]] = None,
        selector: Optional[callable] = None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        if temperature_range is None:
            self.temperature_range = [1.3, 0.0]
        self.candidates = []  # Store all candidate solutions
        self.selected_candidate = None  # Store the selected candidate solution
        self.num_responses = num_responses
        self.selector = selector

    def call_llm(
        self,
        system_prompt: str,
        user_prompt: str,
        verbose: Union[bool, str] = False,
        max_tokens: int = 4096,
        num_responses: int = 1,
        temperature: float = 0.0,
    ) -> List[str]:
        """Call the LLM with a prompt and return multiple responses."""
        if verbose not in (False, "output"):
            print("Prompt\n", system_prompt + user_prompt)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        try:
            response = self.llm.create(
                messages=messages,
                response_format={"type": "json_object"},
                max_tokens=max_tokens,
                n=num_responses,
                temperature=temperature,
            )
        except Exception as e:
            if verbose:
                print(f"ERROR {e}")
            # Default to returning an empty response list if an error occurs # Error handling improvement
            return []

        responses = [choice.message.content for choice in response.choices]

        if verbose:
            print("LLM responses:\n", responses)
        return responses

    def generate_candidates(
        self,
        summary,
        system_prompt: str,
        user_prompt: str,
        verbose: Union[bool, str] = False,
        mask=None,
        max_tokens: int = None,
        num_responses: Optional[int] = None,
        temperature_range: Optional[List[float]] = None,
    ) -> List[str]:
        """
        Generate multiple candidates with progressively decreasing temperatures.
        Args:
            summary: The summarized problem instance.
            system_prompt (str): The system-level prompt.
            user_prompt (str): The user-level prompt.
            verbose (bool): Whether to print debug information.
            mask: Mask for the problem instance.
            max_tokens (int, optional): Maximum token limit for the LLM responses.
            num_responses (int): Number of responses to request.
            temperature_range (List[float]): [max_temperature, min_temperature].
        Returns:
            List[str]: List of LLM responses as strings.
        """
        num_responses = (
            num_responses if num_responses is not None else self.num_responses
        )  # Allow overriding num_responses
        temperature_range = (
            temperature_range
            if temperature_range is not None
            else self.temperature_range
        )

        max_tokens = max_tokens or self.max_tokens  # Allow overriding max_tokens
        max_temp, min_temp = max(temperature_range), min(
            temperature_range
        )  # Ensure max > min
        temperatures = [
            max_temp - i * (max_temp - min_temp) / max(1, num_responses - 1)
            for i in range(num_responses)
        ]

        if verbose:
            print(f"Temperatures for responses: {temperatures}")

        candidates = [
            self.call_llm(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                verbose=verbose,
                max_tokens=max_tokens,
                num_responses=1,
                temperature=temp,
            )[
                0
            ]  # Extract the single response
            for temp in temperatures
        ]

        if self.log is not None:
            self.log.append(
                {
                    "system_prompt": system_prompt,
                    "user_prompt": user_prompt,
                    "response": candidates,
                }
            )
            self.summary_log.append(
                {"problem_instance": self.problem_instance(summary), "summary": summary}
            )

        return candidates

    def select_candidate(self, candidates: List[Dict]) -> Dict:  # Fixed type annotation
        """
        Select the best response based on the responses.
        Args:
            candidates (List[Dict]): List of candidate responses as dictionaries.
        Returns:
            Dict: The selected candidate or an empty dictionary if no candidates exist.
        """
        return candidates[-1] if candidates else {}  # Default to the last candidate

    def _step(
        self,
        verbose=False,
        mask=None,
        num_responses: Optional[int] = None,
        temperature_range: Optional[List[float]] = None,
        selector: callable = None,
        *args,
        **kwargs,
    ) -> Dict:  # Added type annotation for return value
        """
        Perform a single optimization step, storing responses in self.responses and allowing selection.
        Args:
            verbose (bool): Whether to print debug information.
            mask (list, optional): Mask for the problem instance.
            num_responses (int): Number of responses to request from the LLM.
            temperature (float): Sampling temperature for the LLM.
            selector (callable, optional): Function to select the best response.
        Returns:
            Dict: The update dictionary based on the selected response.
        """
        num_responses = (
            num_responses if num_responses is not None else self.num_responses
        )  # Allow overriding num_responses
        temperature_range = (
            temperature_range
            if temperature_range is not None
            else self.temperature_range
        )
        selector = selector if selector is not None else self.selector

        assert isinstance(self.propagator, GraphPropagator)
        summary = self.summarize()
        system_prompt, user_prompt = self.construct_prompt(summary, mask=mask)

        system_prompt = self.replace_symbols(system_prompt, self.prompt_symbols)
        user_prompt = self.replace_symbols(user_prompt, self.prompt_symbols)

        # Generate candidates
        responses = self.generate_candidates(
            summary,
            system_prompt,
            user_prompt,
            verbose=verbose,
            mask=mask,
            num_responses=num_responses,
            temperature_range=temperature_range,
        )

        self.candidates = []  # Clear previous responses
        for response in responses:
            if "TERMINATE" in response:
                self.candidates.append({})
                continue

            suggestion = self.extract_llm_suggestion(response)
            update_dict = self.construct_update_dict(suggestion)

            self.candidates.append(update_dict)

        # Select the response using the selector or the default select_candidate method
        if selector and callable(selector):  # Ensure the selector is callable
            self.selected_candidate = selector(self.candidates)
        else:
            self.selected_candidate = self.select_candidate(candidates=self.candidates)

        return self.selected_candidate
