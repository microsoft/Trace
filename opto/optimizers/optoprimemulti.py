from typing import Any, List, Dict, Union, Tuple, Optional
import json
from textwrap import dedent

from opto.trace.propagators import GraphPropagator
from opto.optimizers.optoprime import OptoPrime


class OptoPrimeMulti(OptoPrime):
    def __init__(self, *args,
                 num_responses: int = 5,
                 temperature_range: Optional[List[float]] = None,
                 selector: Optional[callable] = None,
                 **kwargs):
        super().__init__(*args, **kwargs)
        if temperature_range is None:
            self.temperature_range = [1.3, 0.]
        self.candidates = []  # Store all candidate solutions
        self.selected_candidate = None  # Store the selected candidate solution
        self.num_responses = num_responses
        self.selector = selector
        self.use_synthesis = False

    def call_llm(
            self, system_prompt: str, user_prompt: str, verbose: Union[bool, str] = False,
            max_tokens: int = 4096, num_responses: int = 1, temperature: float = 0.
    ) -> List[str]:
        """Call the LLM with a prompt and return multiple responses."""
        if verbose not in (False, "output"):
            print("Prompt\n", system_prompt + user_prompt)

        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]

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
            self, summary, system_prompt: str, user_prompt: str, verbose: Union[bool, str] = False,
            mask=None, max_tokens: int = None, num_responses: Optional[int] = None, temperature_range: Optional[List[float]] = None, generation_technique: str = "temperature_variation"
    ) -> List[str]:
        """
        Generate multiple candidates using configurable techniques.
        Args:
            summary: The summarized problem instance.
            system_prompt (str): The system-level prompt.
            user_prompt (str): The user-level prompt.
            verbose (bool): Whether to print debug information.
            mask: Mask for the problem instance.
            max_tokens (int, optional): Maximum token limit for the LLM responses.
            num_responses (int): Number of responses to request.
            temperature_range (List[float]): [max_temperature, min_temperature].
            generation_technique (str): Technique for generating candidates. Options:
                - "temperature_variation": Use temperature range for diversity (default).
                - "self_refinement": Iteratively refine candidates using self-feedback.
                - "iterative_alternatives": Find new alternative optimal solutions given previous candidates.
        Returns:
            List[str]: List of LLM responses as strings.
        """
        num_responses = num_responses if num_responses is not None else self.num_responses  # Allow overriding num_responses
        temperature_range = temperature_range if temperature_range is not None else self.temperature_range
        max_tokens = max_tokens or self.max_tokens  # Allow overriding max_tokens

        candidates = []

        # Temperature Variation (Original Logic)
        if generation_technique == "temperature_variation":
            self.use_synthesis = True  # Enable synthesis for the final selection
            max_temp, min_temp = max(temperature_range), min(temperature_range)
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
                    temperature=temp
                )[0]  # Extract the single response
                for temp in temperatures
            ]

        # Self-Refinement
        elif generation_technique == "self_refinement":
            for _ in range(num_responses):
                if not candidates:  # First candidate, no refinement needed
                    current_prompt = system_prompt
                else:  # Refine the last candidate
                    current_prompt = f"{system_prompt}\nRefine the following solution: {candidates[-1]}"

                candidate = self.call_llm(
                    system_prompt=current_prompt,
                    user_prompt=user_prompt,
                    verbose=verbose,
                    max_tokens=max_tokens,
                    num_responses=1,
                    temperature=0.  # Deterministic output
                )[0]
                candidates.append(candidate)

        # Iterative Alternatives
        elif generation_technique == "iterative_alternatives":
            self.use_synthesis = True  # Enable synthesis for the final selection
            for i in range(num_responses):
                if not candidates:  # First candidate, no alternatives yet
                    current_prompt = system_prompt
                else:  # Generate a new alternative based on previous candidates
                    previous_solutions = "\n".join(
                        f"SOLUTION {idx + 1}: <<<{candidate}>>>"
                        for idx, candidate in enumerate(candidates)
                    )
                    current_prompt = (
                        f"{system_prompt}\nGiven the following solutions, propose a new alternative optimal solution:\n"
                        f"{previous_solutions}\n{user_prompt}"
                    )

                candidate = self.call_llm(
                    system_prompt=current_prompt,
                    user_prompt=user_prompt,
                    verbose=verbose,
                    max_tokens=max_tokens,
                    num_responses=1,
                    temperature=0.  # Deterministic output
                )[0]
                candidates.append(candidate)

        else:
            raise ValueError(f"Invalid generation_technique: {generation_technique}. "
                            "Supported options: 'temperature_variation', 'self_refinement', "
                            "'iterative_alternatives'.")

        # Log the generated candidates
        if self.log is not None:
            self.log.append({"system_prompt": system_prompt, "user_prompt": user_prompt, "response": candidates})
            self.summary_log.append({'problem_instance': self.problem_instance(summary), 'summary': summary})

        return candidates

    def select_candidate(self, candidates: List[Dict], use_synthesis: bool = False) -> Dict:
        """
        Select the best response based on the responses.
        Args:
            candidates (List[Dict]): List of candidate responses as dictionaries.
            use_synthesis (bool): If True, synthesize an optimal solution from all candidates.
        Returns:
            Dict: The selected candidate or an empty dictionary if no candidates exist.
        """
        if not candidates:
            return {}

        # Default behavior: return the last candidate
        if not use_synthesis:
            return candidates[-1]

        # Synthesize an optimal solution from all candidates
        candidate_texts = [f"SOLUTION {i + 1}: <<<{json.dumps(candidate, indent=2)}>>>" for i, candidate in enumerate(candidates)]
        synthesis_prompt = (
            "Given the following solutions and the initial question, provide an optimal solution by combining the best elements of each. Follow the same output structure as the candidates.\n\n"
            "Candidates:\n" + "\n".join(candidate_texts) + "\n\n"
            "Optimal Solution:\n"
        )

        # Call the LLM to synthesize the optimal solution
        synthesized_response = self.call_llm(
            system_prompt="You are an expert optimizer. Synthesize the best solution from the given candidates.",
            user_prompt=synthesis_prompt,
            verbose=False,
            #max_tokens=??,
            num_responses=1,
            temperature=0.3  # Low temperature for deterministic synthesis
        )

        if synthesized_response:
            try:
                return json.loads(synthesized_response[0])
            except json.JSONDecodeError:
                # Fallback to the last candidate if synthesis fails
                return candidates[-1]
        else:
            # Fallback to the last candidate if synthesis fails
            return candidates[-1]

    def _step(
            self, verbose=False, mask=None, num_responses: Optional[int] = None, temperature_range: Optional[List[float]] = None,
            selector: callable = None, *args, **kwargs
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
        num_responses = num_responses if num_responses is not None else self.num_responses  # Allow overriding num_responses
        temperature_range = temperature_range if temperature_range is not None else self.temperature_range
        selector = selector if selector is not None else self.selector

        assert isinstance(self.propagator, GraphPropagator)
        summary = self.summarize()
        system_prompt, user_prompt = self.construct_prompt(summary, mask=mask)

        system_prompt = self.replace_symbols(system_prompt, self.prompt_symbols)
        user_prompt = self.replace_symbols(user_prompt, self.prompt_symbols)

        # Generate candidates
        responses = self.generate_candidates(
            summary, system_prompt, user_prompt, verbose=verbose, mask=mask,
            num_responses=num_responses, temperature_range=temperature_range
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
            self.selected_candidate = self.select_candidate(candidates=self.candidates, use_synthesis=self.use_synthesis)

        return self.selected_candidate
