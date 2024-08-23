"""
This module specifies the prompt specification. We use this specification to load prompt files and convert them
into engineered prompt objects.
"""

from typing import Annotated, Dict, Literal, Optional, Union

import frontmatter
from pydantic import BaseModel, Field, model_validator, validator


class Limits(BaseModel):
    """
    Limits are used to specify the minimum and maximum values for a property test.
    You can either specify a min value, max value, or both. If you specify both, the value must be within the range.
    """

    min: Optional[int] = None
    max: Optional[int] = None

    @model_validator(mode="after")
    def ensure_correct_limits(self):
        if self.min is None and self.max is None:
            raise ValueError("You must specify at least one of min or max values.")

        if self.min is not None and self.max is not None and self.min > self.max:
            raise ValueError("The min value must be less than the max value.")

        return self


class PreciseLimits(BaseModel):
    """
    Limits are used to specify the minimum and maximum values for a score test.
    You can either specify a min value, max value, or both. If you specify both, the value must be within the range.
    """

    min: Optional[float] = None
    max: Optional[float] = None

    @model_validator(mode="after")
    def ensure_correct_limits(self):
        if self.min is None and self.max is None:
            raise ValueError("You must specify at least one of min or max values.")

        if self.min is not None and self.max is not None and self.min > self.max:
            raise ValueError("The min value must be less than the max value.")

        return self


class QuestionTestSpecification(BaseModel):
    """
    This type of test validates that the prompt output answers a specific question.

    The prompt is considered correct if the question in the prompt property of this test is answered with
    an affirmative.

    Attributes
    ----------
    prompt: str
        The question to ask about the prompt output. The question should result in a yes or no answer.

        When the question doesn't specify that the model must answer with yes or no, we'll automatically add this
        instruction to it so the answer can be validated correctly.
    """

    type: Literal["question"] = "question"
    prompt: str


class FormatTestSpecification(BaseModel):
    """
    This type of tests validates that the prompt output is in a specific format.

    Attributes
    ----------
    format: Literal["html", "json", "markdown"]
        The expected format of the prompt output.
    """

    type: Literal["format"] = "format"
    format: Literal["html", "json", "markdown"]


class PropertyTestSpecification(BaseModel):
    """
    This type of test validates that the output by checking if it has a specific property.

    For example, does the prompt output a text that has a specific number of words, sentences, or lines.
    The configured limits must have a min or max value, or both.

    Attributes
    ----------
    unit: Literal["words", "sentences", "lines"]
        The unit of the property to check.
    limit: Limits
        The limits for the property.
    """

    type: Literal["property"] = "property"
    unit: Literal["words", "sentences", "lines"]
    limit: Limits


class ScoreTestSpecification(BaseModel):
    """
    This type of test scores the output of the prompt against a named metric and validates that the score
    is within the configured limits.

    Attributes
    ----------
    metric: str
        The name of the metric to score the prompt output against.
    input: Dict[str, str]
        The mapping of input/output fields in the test samples to the fields required for metric.

        The keys in the input dictionary are the fields required by the metric, and the values are the fields
        in the test context data dictionary.

        The test context data dictionary will always contain the prompt output under the key "output".
        It also contains the input fields specified in the test samples. Finally, it contains the body of the
        test sample under the key "input".
    limit: PreciseLimits
        The limits for the score.
    """

    type: Literal["score"] = "score"
    metric: str
    input: Dict[str, str]
    limit: PreciseLimits


TestSpecificationTypes = Union[
    ScoreTestSpecification,
    PropertyTestSpecification,
    FormatTestSpecification,
    QuestionTestSpecification,
]


class EngineeredPromptMetadata(BaseModel):
    """
    Defines the structure of the front-matter portion of a prompt file.

    Attributes
    ----------
    provider : str
        The provider of the model.
    model : str
        The model identifier or alias.
    test_path: str
        The path where the test samples for the prompt are stored.
    tests : dict
        A dictionary of test specifications.
    """

    provider: str
    model: str
    prompt_version: Optional[str] = None
    input: Optional[str] = None
    output: Optional[str] = None
    output_format: Optional[str] = None
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    presence_penalty: Optional[float] = None
    test_path: Optional[str] = None
    tests: Optional[
        Dict[str, Annotated[TestSpecificationTypes, Field(discriminator="type")]]
    ] = None
    system_role: Optional[str] = None
    system_role_text: str = "You are a helpfull assistant."

    @validator("prompt_version", pre=True)
    def convert_float_to_string(cls, v):
        if isinstance(v, float):
            return str(v)
        return v


class EngineeredPromptSpecification(BaseModel):
    """
    EngineeredPromptSpecification is the specification for a prompt file. It contains the prompt text and metadata.

    From this specification, we can create an EngineeredPrompt object, and test cases.

    Attributes
    ----------
    metadata : EngineeredPromptMetadata
        The metadata for the prompt.
    prompt : str
        The prompt text.
    filename: str
        The filename where the prompt specification is stored.
    """

    metadata: EngineeredPromptMetadata
    prompt: str
    filename: str

    @staticmethod
    def from_file(filename: str) -> "EngineeredPromptSpecification":
        """
        Load a engineered prompt specification from file, and validate it.
        """

        with open(filename, "r") as f:
            file_content = frontmatter.load(f)

            metadata = EngineeredPromptMetadata.model_validate(file_content.metadata)
            prompt = file_content.content.strip()

            return EngineeredPromptSpecification(
                metadata=metadata, prompt=prompt, filename=filename
            )

    def save(self, filename: str) -> None:
        """
        Save the specification to a file.

        Parameters
        ----------
        filename : str
            The path to the file.
        """

        self.filename = filename

        file_content = frontmatter.Post(self.prompt, **self.metadata.model_dump())
        frontmatter.dump(file_content, filename)


class PromptInput(BaseModel):
    """
    Represents an input sample for an engineered prompt.

    You can load the prompt input from a markdown file using the `from_file` method.
    Alternatively, you can create a `PromptInput` object directly.

    Attributes
    ----------
    input : str
        The input text to the prompt.
    properties : Dict[str, object]
        Additional properties for the prompt input.
    """

    input: str
    properties: Dict[str, object] = {}

    @staticmethod
    def from_file(input_file: str) -> "PromptInput":
        """
        Load prompt input from a data file.

        Parameters
        ----------
        input_file : str
            The path to the input file.

        Returns
        -------
        PromptInput
            The prompt input.
        """
        with open(input_file, "r") as f:
            input_data = frontmatter.load(f)

        return PromptInput(input=input_data.content, **input_data.metadata)

    def save(self, filename: str) -> None:
        """
        Save the specification to a file.

        Parameters
        ----------
        filename : str
            The path to the file.
        """

        file_content = frontmatter.Post(self.prompt, **self.properties)
        frontmatter.dump(file_content, filename)
