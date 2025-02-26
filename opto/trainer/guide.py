from typing import List, Dict, Any, Union, Tuple, Optional, Callable
import json
import re
from opto.utils.llm import LLM, AbstractModel


class VerbalGuide:
    """
    Base class for all guides that provide feedback on content.
    
    Guides evaluate generated content and provide feedback to help improve it.
    Different implementations may use different strategies for evaluation,
    such as LLM-based comparison, keyword matching, or custom verification.
    """

    def get_feedback(self, content: str, **kwargs) -> str:
        """
        Generate feedback for the provided content.
        
        Args:
            content: The content to evaluate (e.g., student answer, generated code)
            **kwargs: Optional reference information (e.g., expected answer, execution logs), 
                     Additional context or parameters for specialized guide implementations
            
        Returns:
            A string containing feedback on the content
        """
        raise NotImplementedError("Subclasses must implement get_feedback method")


class ReferenceGuide(VerbalGuide):
    """
    A guide that uses an LLM to generate feedback by comparing content with expected information.
    
    This guide sends prompts to an LLM asking it to evaluate content and provide feedback.
    Users can customize the prompt template to fit different feedback scenarios.
    
    Example usage:
    ```python
    # Create a guide with default settings
    guide = ReferenceGuide(model="gpt-4o")
    
    # Get feedback on student answer
    feedback = guide.get_feedback(content="The derivative of x^2 is 2x", 
                                 reference="The derivative of x^2 is 2x")
    
    # Create a guide with custom prompt template
    custom_guide = ReferenceGuide(
        model="gpt-4o",
        prompt_template="Review this code: {content}. Expected behavior: {reference}. Provide specific feedback."
    )
    ```
    """

    DEFAULT_PROMPT_TEMPLATE = (
        "The student answered: {content}. The correct answer is {reference}. "
        "If the student answer is correct, please say 'Correct'. "
        "Otherwise, if the student answer is incorrect, please provide feedback to the student. "
        "The feedback should be specific and actionable."
    )

    DEFAULT_SYSTEM_PROMPT = "You're a helpful teacher who provides clear and constructive feedback."
    DEFAULT_CORRECTNESS_TEMPLATE = "Correct [TERMINATE]"

    def __init__(self,
                 model: Optional[str] = None,
                 llm: Optional[AbstractModel] = None,
                 prompt_template: Optional[str] = None,
                 system_prompt: Optional[str] = None,
                 correctness_template: Optional[str] = None):
        """
        Initialize the VerbalGuide with an LLM and prompt templates.
        
        Args:
            model: The name of the LLM model to use (if llm is not provided)
            llm: An instance of AbstractModel to use for generating feedback
            prompt_template: Custom prompt template with {content} and {reference} placeholders
            system_prompt: Custom system prompt for the LLM
            correctness_template: Template to use when content is deemed correct by metric
        """
        self.model = model
        self.llm = llm or LLM(model=model)
        self.prompt_template = prompt_template or self.DEFAULT_PROMPT_TEMPLATE
        self.system_prompt = system_prompt or self.DEFAULT_SYSTEM_PROMPT
        self.correctness_template = correctness_template or self.DEFAULT_CORRECTNESS_TEMPLATE

    def get_feedback(self, content: str, reference: Optional[str] = None, metric: Optional[Callable[[str, str], float]] = None, **kwargs) -> str:
        """
        Get LLM-generated feedback by comparing content with reference information.
        
        Args:
            content: The content to evaluate (e.g., student answer, code, etc.)
            reference: The expected information or correct answer
            metric: Optional function that compares content and reference, returning a value between 0 and 1
            **kwargs: Additional parameters (unused in this implementation)
            
        Returns:
            A string containing the LLM-generated feedback
        """
        if reference is None:
            raise ValueError("ReferenceGuide requires reference information to generate feedback")

        # Check if metric function indicates perfect match
        if metric is not None and metric(content, reference) == 1:
            response = self.correctness_template
        else:
            user_prompt = self.prompt_template.format(content=content, reference=reference)

            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_prompt}
            ]

            response = self.llm(messages=messages)

            # Extract the content from the response based on the LLM's response format
            if hasattr(response, 'choices') and hasattr(response.choices[0], 'message'):
                # For OpenAI-like response format
                response = response.choices[0].message.content
            # else: response is already the content

        # Format the output
        deliminator = "\n-------------------------------------\n"
        formatted_response = (
            "The generated content:\n" + content + deliminator +
            "Expert feedback for generating the net content (if exists, please pay most attention to it):\n" +
            response
        )

        return formatted_response


class KeywordGuide(VerbalGuide):
    """
    A guide that matches keywords in execution log and returns corresponding responses.
    
    The guide can be initialized with either a JSON file path or a dictionary mapping
    keywords to responses. When provided with content, it will return all responses
    for keywords that appear in the content.
    
    Expected format for keyword-response dictionary:
    {
        "keyword1": "Response message for when keyword1 is found in content",
        "keyword2": "Response message for when keyword2 is found in content",
        ...
    }
    
    Example:
    {
        "stride does not match": "The layout constraints are not satisfied. Please try to adjust the layout constraints...",
        "Execution time": "Now the mapping is valid. Please try to reduce the execution time...",
        "syntax error": "Typically the syntax happens in how you define functions. Reminder about syntax: generally code comments start with #..."
    }
    
    When analyzing content, all keywords that appear in the content will have their
    corresponding responses included in the output, joined by newlines.
    
    The guide can also be extended with custom analysis functions to provide more
    detailed feedback beyond simple keyword matching.
    """

    def __init__(self,
                 json_file: Optional[str] = None,
                 keyword_response: Optional[Dict[str, str]] = None,
                 custom_analyzers: Optional[List[Callable[[str, str], str]]] = None,
                 **kwargs):
        """
        Initialize the KeywordGuide with either a JSON file or a keyword-response dictionary.
        
        Args:
            json_file: Path to a JSON file containing keyword-response mappings
            keyword_response: Dictionary mapping keywords to responses
            custom_analyzers: List of custom analysis functions that take (content, reference_log)
                              as input and return a string with additional feedback
        """
        if json_file and keyword_response:
            raise ValueError("Cannot provide both json_file and keyword_response")

        self.keyword_response = {}

        if json_file:
            with open(json_file, 'r') as f:
                self.keyword_response = json.load(f)
        elif keyword_response:
            self.keyword_response = keyword_response

        self.custom_analyzers = custom_analyzers or []

    def add_analyzer(self, analyzer_func: Callable[[str, str], str]) -> None:
        """
        Add a custom analyzer function to the guide.
        
        Args:
            analyzer_func: A function that takes (content, reference_log) as input
                          and returns a string with feedback
        """
        self.custom_analyzers.append(analyzer_func)

    def match(self, log_content: str) -> str:
        """
        Match keywords in the log content and return concatenated responses.
        
        Args:
            log_content: The content to search for keywords
            
        Returns:
            A string containing all matched responses, joined by newlines
        """
        matched_responses = []

        for keyword, response in self.keyword_response.items():
            if keyword in log_content:
                matched_responses.append(response)

        return "\n".join(matched_responses)

    def run_custom_analyzers(self, content: str, reference_log: str) -> List[str]:
        """
        Run all custom analyzers on the content.
        
        Args:
            content: The content to analyze (e.g., generated code)
            reference_log: The log content to analyze
            
        Returns:
            A list of feedback strings from custom analyzers
        """
        results = []
        for analyzer in self.custom_analyzers:
            result = analyzer(content, reference_log)
            if result:
                results.append(result)
        return results

    def get_feedback(self, content: str, info: Optional[str] = None, reward: Optional[float] = None, **kwargs) -> str:
        """
        Get feedback based on content and reference log.
        
        Args:
            content: The content to analyze (e.g., generated code)
            info: The reference log containing execution information
            reward: The reward score for the content
            **kwargs: Additional parameters (unused in this implementation)
            
        Returns:
            A string containing feedback based on keyword matches and all analyzers
        """
        if info is None:
            raise ValueError(
                "KeywordGuide requires reference information (such as execution or profiling info) to generate feedback")

        feedback_parts = []

        # Get keyword matches
        matched_responses = self.match(info)
        if matched_responses:
            feedback_parts.append(matched_responses)

        # Run custom analyzers
        custom_feedback = self.run_custom_analyzers(content, info)
        feedback_parts.extend(custom_feedback)

        # Format the output
        deliminator = "\n-------------------------------------\n"
        formatted_response = (
            "The generated content:\n" + content + deliminator +
            "Expert feedback for generating the net content (if exists, please pay most attention to it):\n" +
            "\n".join(feedback_parts)
        )

        return formatted_response


class AutoGuide:
    """
    Master entry point that constructs specialized guides automatically based on provided parameters.
    """

    def build(self,
              model: Optional[str] = None,
              llm: Optional[AbstractModel] = None,
              prompt_template: Optional[str] = None,
              system_prompt: Optional[str] = None,
              json_file: Optional[str] = None,
              keyword_response: Optional[Dict[str, str]] = None,
              custom_analyzers: Optional[List[Callable[[str, str], str]]] = None,
              **kwargs) -> VerbalGuide:
        """
        Build and return an appropriate guide based on the provided parameters.
        
        The method infers which guide type to create based on the parameters provided:
        - If json_file or keyword_response is provided, creates a KeywordGuide
        - Otherwise, creates a ReferenceGuide
        
        Args:
            model: The name of the LLM model to use (for ReferenceGuide)
            llm: An instance of AbstractModel to use (for ReferenceGuide)
            prompt_template: Custom prompt template (for ReferenceGuide)
            system_prompt: Custom system prompt (for ReferenceGuide)
            json_file: Path to a JSON file containing keyword-response mappings (for KeywordGuide)
            keyword_response: Dictionary mapping keywords to responses (for KeywordGuide)
            custom_analyzers: List of custom analysis functions (for KeywordGuide)
            **kwargs: Additional parameters for specific guide implementations
            
        Returns:
            An instance of a Guide subclass
            
        Raises:
            ValueError: If insufficient parameters are provided to create any guide type
        """
        # Determine guide type based on provided parameters
        if json_file is not None or keyword_response is not None:
            # KeywordGuide parameters
            return KeywordGuide(
                json_file=json_file,
                keyword_response=keyword_response,
                custom_analyzers=custom_analyzers,
                **kwargs
            )
        elif model is not None or llm is not None:
            # ReferenceGuide parameters
            return ReferenceGuide(
                model=model,
                llm=llm,
                prompt_template=prompt_template,
                system_prompt=system_prompt,
                **kwargs
            )
        else:
            raise ValueError(
                "Insufficient parameters to create a guide. "
                "For ReferenceGuide, provide 'model' or 'llm'. "
                "For KeywordGuide, provide 'json_file' or 'keyword_response'."
            )