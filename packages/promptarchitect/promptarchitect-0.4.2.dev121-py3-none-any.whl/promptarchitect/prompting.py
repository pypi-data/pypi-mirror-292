"""
This module contains the `EngineeredPrompt` class that represents a validated prompt and associated input.
"""

import json
import logging
import os
from typing import Dict, Optional
from uuid import uuid4

import chevron
from pydantic import BaseModel

from promptarchitect.completions import create_completion
from promptarchitect.specification import EngineeredPromptSpecification, PromptInput

logger = logging.getLogger(__name__)


class PromptOutput(BaseModel):
    response: str
    input_tokens: int
    output_tokens: int
    completion: object


class EngineeredPrompt:
    """
    The engineered prompt. A validated, well thought-out prompt that is easy to use in your application.

    We support running and rendering the prompt in the specification in your application.
    This class is also used during validation to run the prompt.

    Attributes
    ----------
    specification : EngineeredPromptSpecification
        The specification for the prompt.
    """

    def __init__(
        self,
        specification: EngineeredPromptSpecification = None,
        prompt_file: str = None,
        output_path: str = None,
    ):
        """Initialize the engineered prompt with the specification.

        Parameters
        ----------
        specification : EngineeredPromptSpecification
            The specification for the prompt.

        prompt_file : str
            The path to a prompt file.

        output_path : str
            The path to the output directory if you want to save the response to a file.
        """

        self.id = str(uuid4())

        # Convert in the case of a Path object
        self.prompt_file = str(prompt_file) if prompt_file is not None else None
        self.output_path = str(output_path) if output_path is not None else None

        if specification is None and prompt_file is None:
            raise ValueError("Either specification or prompt_file must be provided.")

        if specification is not None and prompt_file is not None:
            raise ValueError(
                "Only one of specification or prompt_file can be provided."
            )

        if self.prompt_file is not None:
            self.specification = EngineeredPromptSpecification.from_file(
                self.prompt_file
            )
        else:
            self.specification = specification

        # If the system role is provided in the specification, we'll use that
        # and read it from the file specified in the metadata
        # Otherwise we'll use the default system role
        if self.specification.metadata.system_role is not None:
            with open(self.specification.metadata.system_role, "r") as file:
                self.specification.metadata.system_role_text = file.read().strip()

        # Initialize the completion, so for Open Source models we can download the model
        self.completion = create_completion(
            self.specification.metadata.provider,
            self.specification.metadata.model,
            self.specification.metadata,
            self.specification.metadata.system_role_text,
        )

    def execute(
        self,
        input_text: Optional[str] = None,
        input_file: Optional[str] = None,
        properties: Optional[Dict[str, object]] = None,
    ) -> str:
        """
        Executes the prompt with the input text or input file.

        The output of this operation is not cached.

        This function is for backwards compatibility with the previous version of the library.

        Returns
        -------
        str
            The output of the prompt.
        """
        logger.warning("The execute method is deprecated. Use run instead.")

        return self.run(input_text, input_file, properties)

    def _number_of_mustaches_in_prompt(self) -> int:
        """
        Count the number of unique mustaches in the prompt, excluding the input mustache,
        and only count the variables, because these are the moustaches.


        """
        mustaches = set(chevron.tokenizer.tokenize(self.specification.prompt))

        # filter on literal mustaches
        number_of_mustaches = len([m for m in mustaches if m[0] == "variable"])
        # If the mustache {{input}} is in the prompt, we'll remove it from the count
        if "{{input}}" in self.specification.prompt:
            number_of_mustaches -= 1
        return number_of_mustaches

    def run(
        self,
        input_text: Optional[str] = None,
        input_file: Optional[str] = None,
        properties: Optional[Dict[str, object]] = None,
    ) -> str:
        """
        Runs the prompt with the input text or input file.

        The output of this operation is automatically cached until the application is closed.

        Parameters
        ----------
        input_text : str, optional
            The input text to the prompt.
        input_file : str, optional
            The path to the input file.
        properties : Dict[str, object], optional
            Additional properties for the prompt input to render the prompt with variables.

        Returns
        -------
        str
            The output of the prompt.
        """

        rendered_input = self.render(input_text, input_file, properties)

        response = self.completion.completion(rendered_input)

        if self.output_path is not None:
            output_file = os.path.join(
                self.output_path, self.specification.metadata.output
            )
            self.write_output_to_file(response, output_file)

        return response

    def write_output_to_file(self, response: str, output_file: str):
        """
        Writes the response to a file in the format as specified in the specification.

        Parameters
        ----------
        response : str
            The response from the prompt.
        output_file : str
            The path to the output file.
        """

        try:
            # Create base path if it does not exist
            os.makedirs(os.path.dirname(output_file), exist_ok=True)

            # Check the output format in the specification
            if self.specification.metadata.output_format == "json":
                # Write the response to a JSON file
                with open(output_file, "w") as file:
                    json.dump({"response": response}, file)

            else:
                # Consider the output format to be text
                with open(output_file, "w") as file:
                    file.write(response)

        except Exception as e:
            logger.error(f"Error writing output to file: {e}")

    def render(
        self,
        input_text: Optional[str] = None,
        input_file: Optional[str] = None,
        properties: Optional[Dict[str, object]] = None,
    ) -> str:
        """
        Render the prompt with the input_text

        We'll read the input_file if is is provided. The input file will provide this method
        with the input_text and properties. If you specify the input_text you can optionally
        include extra properties you need to render the prompt.

        Specifying properties with an `input_file` is not supported. You also can't provide
        both `input_text` and `input_file`. You must provide one or the other.

        Parameters
        ----------
        input_text : str, optional
            The input text to the prompt.
        input_file : str, optional
            The path to the input file.
        properties : Dict[str, object], optional
            Additional properties for the prompt input.

        Returns
        -------
        str
            The rendered prompt.
        """
        input_text = self._determine_input_text_order(input_text, input_file)

        # Check if the number of mustaches in the prompt is equal to the number of properties
        # If not, we'll warn the user that the prompt might not render correctly
        if properties is not None:
            mustaches = self._number_of_mustaches_in_prompt()

            if mustaches != len(properties):
                logger.warning(
                    f"Mustaches mismatch: The number of mustaches in the prompt ({mustaches}) is not equal to the number of properties ({len(properties)}).\n"
                    f"This might result in the prompt not rendering correctly."
                )

        prompt = self.specification.prompt
        # Add a input property to prompt if it is not already in the prompt
        # Otherwise the input will not be rendered in the prompt
        if "{{input}}" not in self.specification.prompt:
            prompt = f"{self.specification.prompt} {{{{input}}}}"

        # We'll render the prompt with the input_text and properties
        template_properties = properties.copy() if properties is not None else {}
        template_properties["input"] = input_text

        return chevron.render(prompt, template_properties)

    def _determine_input_text_order(self, input_text: str, input_file: str) -> str:
        if input_text is not None and input_file is not None:
            raise ValueError("Only one of input_text or input_file can be provided.")

        # This is the order to pick the input for the rendering of the prompt
        # 1. input_text
        # 2. input_file
        # 3. self.specification.metadata.input

        if (
            input_text is None
            and input_file is None
            and self.specification.metadata.input is None
        ):
            input_text = ""

        elif input_text is None:
            input_file = (
                input_file
                if input_file is not None
                else self.specification.metadata.input
            )

            if input_file is not None:
                prompt_input = PromptInput.from_file(input_file)

                # properties = prompt_input.properties
                input_text = prompt_input.input

        return input_text

    def to_dict(self) -> Dict:
        """
        Convert the EngineeredPrompt instance to a dictionary.

        Returns
        -------
        dict
            A dictionary representation of the EngineeredPrompt instance.
        """
        return {
            "id": self.id,
            "specification": self.specification.dict() if self.specification else None,
            "prompt_file": self.prompt_file,
            "output_path": self.output_path,
            "completion": self.completion.to_dict() if self.completion else None,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "EngineeredPrompt":
        """
        Create an EngineeredPrompt instance from a dictionary.

        Parameters
        ----------
        data : dict
            A dictionary containing the data to create an EngineeredPrompt instance.

        Returns
        -------
        EngineeredPrompt
            An EngineeredPrompt instance created from the provided dictionary.
        """
        specification = (
            EngineeredPromptSpecification(**data["specification"])
            if data["specification"]
            else None
        )

        return cls(
            id=data.get("id"),
            specification=specification,
            prompt_file=data.get("prompt_file"),
            output_path=data.get("output_path"),
        )
