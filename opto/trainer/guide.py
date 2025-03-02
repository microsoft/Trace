from typing import List, Dict, Any, Union, Tuple, Optional, Callable
import json
import re
from opto.utils.llm import LLM, AbstractModel
from opto.trainer.suggest import Suggest

class Guide:
    """
    Base class for all guides that provide feedback on content.

    Guide evaluates generated content and provide feedback to help improve it.
    Different implementations may use different strategies for evaluation,
    such as LLM-based comparison, keyword matching, or custom verification.
    """

    def __call__(self, task: str, content: str, info: Any, **kwargs) -> Tuple[float, str]:
        """
        Generate feedback for the provided content.

        Args:
            task: The task to analyze (e.g., user query, task, etc.)
            content: The content to evaluate (e.g., student answer, generated code)
            info: additional information (used by some suggest but not others)
            **kwargs: Optional reference information (e.g., expected answer, execution logs),
                     Additional context or parameters for specialized guide implementations

        Returns:
            score: score from the teacher
            feedback: feedback from the teacher
        """
        return self.forward(task, content, info, **kwargs)

    def forward(self, task: str, content: str, info: Any, **kwargs) -> Tuple[float, str]:
        # score = self.metric(task, content, info, **kwargs)
        # feedback = self.suggest.get_feedback(task, content, info, **kwargs)
        # return score, feedback
        raise NotImplementedError

    def metric(self, task: str, content: str, info: Any, **kwargs) -> float:
        raise NotImplementedError

def exact_match_metric(question, student_answer, info):
    """ Exact match metric """
    return float(student_answer == info)


class VerbalBinaryJudgeGuide(Guide):
    """
    This is a combined metric + feedback guide that asks LLM to provide a binary judgment (True/False)
    and then if False, provide feedback.
    """

    DEFAULT_PROMPT_TEMPLATE = (
        "The query is: {query}. The student answered: {content}. The correct answer is: {reference}. "
        "If the student answer is correct, please say 'Correct [TERMINATE]'. "
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

    def get_feedback(self, query: str, content: str, reference: Optional[str] = None, **kwargs) -> Tuple[float, str]:
        """
        Get LLM-generated feedback by comparing content with reference information.

        Args:
            query: The query to analyze (e.g., user query, task, etc.)
            content: The content to evaluate (e.g., student answer, code, etc.)
            reference: The expected information or correct answer
            **kwargs: Additional parameters (unused in this implementation)

        Returns:
            A string containing the LLM-generated feedback
        """
        if reference is None:
            raise ValueError("ReferenceGuide requires reference information to generate feedback")

        # Check if metric function indicates perfect match
        user_prompt = self.prompt_template.format(query=query, content=content, reference=reference)

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
                "The query is: {query}. The student answered: {content}. The correct answer is: {reference}. " + deliminator +
                "Expert feedback for generating the net content (if exists, please pay most attention to it):\n" +
                response
        ).format(query=query, content=content, reference=reference)

        score = 1 if 'Correct [TERMINATE]' in response else 0

        return score, formatted_response

    def metric(self, query: str, content: str, reference: Optional[str] = None, **kwargs) -> float:
        """ Exact match metric """
        return self.get_feedback(query, content, reference)[0]

    def forward(self, task: str, content: str, info: Any, **kwargs) -> Tuple[float, str]:
        score, feedback = self.get_feedback(task, content, info, **kwargs)
        return score, feedback
