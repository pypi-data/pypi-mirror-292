"""
This module specifies the prompt specification. We use this specification to load prompt files and convert them
into engineered prompt objects.
"""

import json
from enum import Enum
from typing import Annotated, Dict, Literal, Optional, Union
from uuid import uuid4

import frontmatter
from pydantic import BaseModel, Field, field_validator, model_validator


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

    def between(self, value: int):
        """
        Check if the value is within the limits.

        Parameters
        ----------
        value : int
            The value to check.

        Returns
        -------
        bool
            True if the value is within the limits, False otherwise.
        """
        if self.max is None:
            return self.min <= value
        if self.min is None:
            return value <= self.max

        return self.min <= value <= self.max


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


class PromptOutputFormat(str, Enum):
    """
    Enum to represent the various output formats for a format test.
    """

    HTML = "html"
    JSON = "json"
    MARKDOWN = "markdown"


class FormatTestSpecification(BaseModel):
    """
    This type of tests validates that the prompt output is in a specific format.

    Attributes
    ----------
    format: Literal["html", "json", "markdown"]
        The expected format of the prompt output.
    """

    type: Literal["format"] = "format"
    format: PromptOutputFormat


class PropertyUnit(str, Enum):
    """
    Enum to represent the various units for a property test.
    """

    WORDS = "words"
    SENTENCES = "sentences"
    LINES = "lines"
    PARAGRAPHS = "paragraphs"
    CHARACTERS = "characters"


class PropertyTestSpecification(BaseModel):
    """
    This type of test validates that the output by checking if it has a specific property.

    For example, does the prompt output a text that has a specific number of words, sentences, lines, or paragraphs.
    The configured limits must have a min or max value, or both.

    Attributes
    ----------
    unit: Literal["words", "sentences", "lines", "paragraphs"]
        The unit of the property to check.
    limit: Limits
        The limits for the property.
    equals: Optional[int] = None
    """

    type: Literal["property"] = "property"
    unit: PropertyUnit
    limit: Optional[Limits] = None
    equals: Optional[int] = None

    @model_validator(mode="after")
    def limit_or_equals_specified(self):
        if self.limit is None and self.equals is None:
            raise ValueError("You must specify at least one of limit or equals values.")

        return self


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
    frequency_penalty: Optional[float] = None
    test_path: Optional[str] = None
    tests: Optional[
        Dict[str, Annotated[TestSpecificationTypes, Field(discriminator="type")]]
    ] = None
    system_role: Optional[str] = None
    system_role_text: str = "You are a helpfull assistant."

    @field_validator("prompt_version")
    def convert_float_to_string(cls, v):
        if isinstance(v, float):
            return str(v)
        return v

    def to_dict(self) -> dict:
        """
        Convert the metadata to a dictionary.

        Returns
        -------
        dict
            The dictionary representation of the metadata.
        """
        return {
            "provider": self.provider,
            "model": self.model,
            "prompt_version": self.prompt_version,
            "input": self.input,
            "output": self.output,
            "output_format": self.output_format,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "presence_penalty": self.presence_penalty,
            "frequency_penalty": self.frequency_penalty,
            "test_path": self.test_path,
            "tests": {key: value.dict() for key, value in self.tests.items()}
            if self.tests
            else None,
            "system_role": self.system_role,
            "system_role_text": self.system_role_text,
        }

    def to_json(self) -> str:
        """
        Convert the metadata to a JSON string.

        Returns
        -------
        str
            The JSON string representation of the metadata.
        """
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: dict) -> "EngineeredPromptMetadata":
        """
        Create an EngineeredPromptMetadata instance from a dictionary.

        Parameters
        ----------
        data : dict
            A dictionary containing the data to create an EngineeredPromptMetadata instance.

        Returns
        -------
        EngineeredPromptMetadata
            An EngineeredPromptMetadata instance created from the provided dictionary.
        """
        if data.get("tests"):
            data["tests"] = {
                key: TestSpecificationTypes(**value)
                for key, value in data["tests"].items()
            }
        return cls(**data)

    @classmethod
    def from_json(cls, json_str: str) -> "EngineeredPromptMetadata":
        """
        Create an EngineeredPromptMetadata instance from a JSON string.

        Parameters
        ----------
        json_str : str
            A JSON string containing the data to create an EngineeredPromptMetadata instance.

        Returns
        -------
        EngineeredPromptMetadata
            An EngineeredPromptMetadata instance created from the provided JSON string.
        """
        return cls.from_dict(json.loads(json_str))

    @staticmethod
    def model_validate(data: dict) -> "EngineeredPromptMetadata":
        """
        Validate the metadata dictionary.

        Parameters
        ----------
        data : dict
            The dictionary representation of the metadata.

        Returns
        -------
        EngineeredPromptMetadata
            The metadata object.
        """

        return EngineeredPromptMetadata(**data)


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
    filename: Optional[str] = None

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

    def to_dict(self) -> dict:
        """
        Convert the specification to a dictionary.

        Returns
        -------
        dict
            The dictionary representation of the specification.
        """

        return {
            "metadata": self.metadata.dict(),
            "prompt": self.prompt,
            "filename": self.filename,
        }

    @staticmethod
    def from_dict(data: dict) -> "EngineeredPromptSpecification":
        """
        Create an EngineeredPromptSpecification from a dictionary.

        Parameters
        ----------
        data : dict
            The dictionary representation of the specification.

        Returns
        -------
        EngineeredPromptSpecification
            The specification object.
        """

        return EngineeredPromptSpecification(
            metadata=EngineeredPromptMetadata(**data["metadata"]),
            prompt=data["prompt"],
            filename=data["filename"],
        )


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

    id: str
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

        return PromptInput(
            id=str(uuid4()), input=input_data.content, properties=input_data.metadata
        )

    def save(self, filename: str) -> None:
        """
        Save the specification to a file.

        Parameters
        ----------
        filename : str
            The path to the file.
        """

        file_content = frontmatter.Post(self.input, **self.properties)
        frontmatter.dump(file_content, filename)

    def __hash__(self) -> int:
        return hash((self.input, frozenset(self.properties.items())))
