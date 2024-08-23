from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional

from pydantic import BaseModel

from promptarchitect.prompting import EngineeredPrompt
from promptarchitect.specification import (
    FormatTestSpecification,
    PromptInput,
    QuestionTestSpecification,
    ScoreTestSpecification,
    TestSpecificationTypes,
)


class ModelCosts(BaseModel):
    """
    Model to represent the costs of a model.

    Attributes
    ----------
    input_tokens: int
        The number of tokens in the input.
    output_tokens: int
        The number of tokens in the output.
    costs: float
        The costs of the model in dollars.
    """

    input_tokens: int
    output_tokens: int
    costs: float


class TestCaseStatus(str, Enum):
    """Enum to represent the various states of a test case."""

    PASSED = "PASSED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"
    ERROR = "ERROR"


class TestCaseOutcome(BaseModel):
    """
    Models the outcome of a test case.

    Attributes
    ----------
    status: TestCaseStatus
        The status of the test case.
    error_message: Optional[str]
        The error message if the test case failed or errored.
    duration: int
        The duration of the test case in milliseconds.
    """

    test_id: str
    status: TestCaseStatus
    error_message: Optional[str] = None
    duration: int
    costs: ModelCosts


class TestCase(ABC):
    """
    Represents a test case.

    A test case is a concrete implementation of a test specification for a single prompt and input sample combination.
    When you have a single prompt file, with 2 input samples, and 2 tests, you'll have a total of 4 test cases for
    the prompt file.

    Attributes
    ----------
    test_id: str
        The unique identifier for the test case.
    prompt: EngineeredPrompt
        The engineered prompt that the test case is for.
    """

    test_id: str
    prompt: EngineeredPrompt
    input_sample: PromptInput

    def __init__(self, id: str, prompt: EngineeredPrompt, input_sample: PromptInput):
        self.test_id = id
        self.prompt = prompt
        self.input_sample = input_sample

    @abstractmethod
    def run() -> TestCaseOutcome:
        """
        Run the test case.

        Returns
        -------
        TestCaseOutcome
            The outcome of the test case.
        """
        raise NotImplementedError()


class ScoreTestCase(TestCase):
    """Implementation of a test case for a score based test."""

    specification: ScoreTestSpecification

    def __init__(
        self,
        id: str,
        prompt: EngineeredPrompt,
        input_sample: PromptInput,
        specification: ScoreTestSpecification,
    ):
        super().__init__(id, prompt, input_sample)

        self.specification = specification

    def run(self) -> TestCaseOutcome:
        raise NotImplementedError()


class QuestionTestCase(TestCase):
    """Implementation of a test case for a question based test."""

    specification: QuestionTestSpecification

    def __init__(
        self,
        id: str,
        prompt: EngineeredPrompt,
        input_sample: PromptInput,
        specification: QuestionTestSpecification,
    ):
        super().__init__(id, prompt, input_sample)
        self.specification = specification

    def run(self) -> TestCaseOutcome:
        raise NotImplementedError()


class FormatTestCase(TestCase):
    """Implementation of a test case for a format based test."""

    specification: FormatTestSpecification

    def __init__(
        self,
        id: str,
        prompt: EngineeredPrompt,
        input_sample: PromptInput,
        specification: FormatTestSpecification,
    ):
        super().__init__(id, prompt, input_sample)
        self.specification = specification

    def run(self) -> TestCaseOutcome:
        raise NotImplementedError()


def create_test_case(
    test_id: str,
    prompt: EngineeredPrompt,
    spec: TestSpecificationTypes,
    input_sample: PromptInput,
) -> TestCase:
    """
    Create a test case based on the provided specification type.

    Parameters
    ----------
    test_id : str
        The unique identifier for the test case.
    prompt: EngineeredPrompt
        The engineered prompt to be used in the test case.
    spec: TestSpecificationTypes
        The specification type for the test case.
    input_sample: PromptInput
        The input sample to be used in the test case.

    Returns
    -------
    TestCase
        An instance of a test case based on the specification type.
    """
    if isinstance(spec, QuestionTestSpecification):
        return QuestionTestCase(test_id, prompt, input_sample, spec)
    elif isinstance(spec, ScoreTestSpecification):
        return ScoreTestCase(test_id, prompt, input_sample, spec)
    elif isinstance(spec, FormatTestSpecification):
        return FormatTestCase(test_id, prompt, input_sample, spec)
    else:
        raise ValueError("Unknown test specification type.")
