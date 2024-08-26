import logging
import os
from string import Template

import coloredlogs
import frontmatter

# Configuring logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
coloredlogs.install(level="INFO")


class PromptFile:
    """
    A class to read the prompt file and return the prompt as a string.

    Attributes:
    filename (str): The name of the file containing the prompt.
    original_prompt (str): The original prompt text with template strings.
    prompt (str): The prompt text after template substitution.
    metadata (dict): The metadata extracted from the prompt file.
    tests (dict): The test prompts extracted from the prompt file.
    """

    def _get_metadata(self, prompt: str) -> dict:
        """
        Extracts the metadata from the prompt using frontmatter.

        Args:
            prompt (str): The prompt text.

        Returns:
            dict: The extracted metadata as key-value pairs.
        """
        post = frontmatter.loads(prompt)
        metadata = post.metadata

        return metadata

    def _get_prompt_text(self, prompt: str) -> str:
        """
        Extracts the prompt text from the prompt using frontmatter.

        Args:
            prompt (str): The prompt text.

        Returns:
            str: The extracted prompt text.
        """
        post = frontmatter.loads(prompt)
        return post.content.strip()

    def read_input(self, filename: str) -> str:
        """
        Reads the input file and returns the input as a string.

        Args:
            filename (str): The name of the file containing the input.

        Returns:
            str: The input text.
        """
        if not os.path.exists(filename):
            logger.warning(f"File {filename} not found.")
            return ""

        with open(filename, "r") as file:
            input_text = file.read()

        return input_text

    def __init__(self, filename: str = "prompt.txt"):
        """
        Initialize the PromptFile class with the filename of the prompt file.

        Args:
            filename (str): The name of the file containing the prompt.
            Defaults to 'prompt.txt'.
        """

        self.filename = filename
        self.metadata = {}
        self.original_prompt = ""

        # Read the contents of the prompt file
        try:
            with open(self.filename, "r") as file:
                self.text = file.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"File {self.filename} not found.")

        # Store the original prompt text
        self.original_prompt = self._get_prompt_text(self.text)
        self.metadata = self._get_metadata(self.text)
        self.tests = self.metadata.get("tests", {})

        # Initialize the prompt with the original prompt text
        self.prompt = self.original_prompt

    def substitute_prompt(self, **kwargs):
        """
        Substitute the template strings in the original prompt with actual values.

        Args:
            **kwargs: The key-value pairs to substitute in the template.

        Returns:
            str: The prompt with the template strings substituted.
        """
        template = Template(self.original_prompt)
        self.prompt = template.safe_substitute(**kwargs)
        return self.prompt

    def read_prompt(self) -> str:
        """
        Read the prompt file and return the prompt as a string.

        Returns:
            str: The prompt text.
        """
        if not os.path.exists(self.filename):
            logger.error(f"File {self.filename} not found.")
            return ""

        with open(self.filename, "r") as file:
            prompt = file.read()

        return prompt

    def to_dict(self):
        """
        Converts the PromptFile object to a dictionary.

        Returns:
            dict: The PromptFile object as a dictionary.
        """
        return {
            "filename": self.filename,
            "original_prompt": self.original_prompt,
            "prompt": self.prompt,
            "metadata": self.metadata,
            "tests": self.tests,
        }

    @classmethod
    def from_dict(cls, data):
        """
        Creates a PromptFile object from a dictionary.

        Args:
            data (dict): The dictionary containing the PromptFile object data.

        Returns:
            PromptFile: The PromptFile object created from the dictionary.
        """
        obj = cls(data["filename"])
        obj.original_prompt = data["original_prompt"]
        obj.prompt = data["prompt"]
        obj.metadata = data["metadata"]
        obj.tests = data["tests"]
        return obj
