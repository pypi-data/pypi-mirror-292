import json
import re
from abc import ABC, abstractmethod
from enum import Enum
from functools import cache
from typing import Optional

from bs4 import BeautifulSoup
from pydantic import BaseModel

from promptarchitect.prompting import EngineeredPrompt
from promptarchitect.specification import (
    FormatTestSpecification,
    PromptInput,
    PromptOutputFormat,
    PropertyTestSpecification,
    PropertyUnit,
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

    @cache
    def _run_prompt(self, prompt: EngineeredPrompt, input_sample: PromptInput):
        return self.prompt.run(
            input_text=input_sample.input, properties=input_sample.properties
        )


class PropertyTestCase(TestCase):
    """
    Implementation of a test case for a property based test.

    This test case validates that the text exhibits a particular property
    like a number of words, sentences, or lines.

    Attributes
    ----------
    specification: PropertyTestSpecification
        The specification for the property test.
    """

    def __init__(
        self,
        id: str,
        prompt: EngineeredPrompt,
        input_sample: PromptInput,
        specification: PropertyTestSpecification,
    ):
        """
        Initialize the property test case.

        Parameters
        ----------
        id: str
            The unique identifier for the test case.
        prompt: EngineeredPrompt
            The engineered prompt to be used in the test case.
        input_sample: PromptInput
            The input sample to be used in the test case.
        specification: PropertyTestSpecification
            The specification for the property test.
        """
        super().__init__(id, prompt, input_sample)
        self.specification = specification

    def run(self) -> TestCaseOutcome:
        """
        Run the test case.

        Returns
        -------
        """

        response = self._run_prompt(self.prompt, self.input_sample)

        items = []

        if self.specification.unit == PropertyUnit.WORDS:
            items = response.split()
        elif self.specification.unit == PropertyUnit.SENTENCES:
            items = re.split(r"[.!?]", response)
        elif self.specification.unit == PropertyUnit.LINES:
            items = response.split("\n")
        elif self.specification.unit == PropertyUnit.PARAGRAPHS:
            items = response.split("\n\n")
        elif self.specification.unit == PropertyUnit.CHARACTERS:
            items = list(response)
        else:
            raise ValueError(f"Unknown unit {self.specification.unit}.")

        # We strip out empty lines, words, sentences, etc.
        # People sometimes have extra characters like line endings in the output of the prompt.

        if not self.specification.unit == PropertyUnit.CHARACTERS:
            items = [item for item in items if item.strip()]

        error_message = None

        if self.specification.equals is not None:
            status = (
                TestCaseStatus.PASSED
                if len(items) == self.specification.equals
                else TestCaseStatus.FAILED
            )

            error_message = (
                f"Expected {self.specification.equals} {self.specification.unit}, but got {len(items)}."
                if status == TestCaseStatus.FAILED
                else None
            )
        else:
            status = (
                TestCaseStatus.PASSED
                if self.specification.limit.between(len(items))
                else TestCaseStatus.FAILED
            )

            error_message = (
                f"Expected between {self.specification.limit.min} and {self.specification.limit.max} {self.specification.unit}, but got {len(items)}."
                if status == TestCaseStatus.FAILED
                else None
            )

        return TestCaseOutcome(
            test_id=self.test_id,
            status=status,
            error_message=error_message,
            duration=0,
            costs=ModelCosts(input_tokens=0, output_tokens=0, costs=0.0),
        )


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
        response = self._run_prompt(self.prompt, self.input_sample)

        if self.specification.format == PromptOutputFormat.HTML:
            status = (
                TestCaseStatus.PASSED
                if self._is_valid_html(response)
                else TestCaseStatus.FAILED
            )

            error_message = (
                "The output is not valid HTML."
                if status == TestCaseStatus.FAILED
                else None
            )
        elif self.specification.format == PromptOutputFormat.JSON:
            status = (
                TestCaseStatus.PASSED
                if self._is_valid_json(response)
                else TestCaseStatus.FAILED
            )

            error_message = (
                "The output is not valid JSON."
                if status == TestCaseStatus.FAILED
                else None
            )
        elif self.specification.format == PromptOutputFormat.MARKDOWN:
            status = (
                TestCaseStatus.PASSED
                if self._is_valid_markdown(response)
                else TestCaseStatus.FAILED
            )

            error_message = (
                "The output is not valid Markdown."
                if status == TestCaseStatus.FAILED
                else None
            )
        else:
            status = TestCaseStatus.PASSED
            error_message = None

        return TestCaseOutcome(
            test_id=self.test_id,
            status=status,
            error_message=error_message,
            duration=0,
            costs=ModelCosts(input_tokens=0, output_tokens=0, costs=0.0),
        )

    def _is_valid_html(self, data: str) -> bool:
        soup = BeautifulSoup(data, "html.parser")
        return data.startswith("<") and bool(soup.find())

    def _is_valid_json(self, data: str) -> bool:
        try:
            json.loads(data)
            return True
        except json.JSONDecodeError:
            return False

    def _is_valid_markdown(self, data: str) -> bool:
        # Everything that's HTML or plain-text is also valid markdown.
        # If this ever changes, we'll add a proper check here.
        return True


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
