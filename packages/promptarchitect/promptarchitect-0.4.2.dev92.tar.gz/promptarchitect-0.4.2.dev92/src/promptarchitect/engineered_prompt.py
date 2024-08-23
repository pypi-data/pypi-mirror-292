import json
import logging
import os
import time

import coloredlogs

from promptarchitect.claude_completion import ClaudeCompletion
from promptarchitect.completions.calculated import CalculatedCompletion
from promptarchitect.completions.format import FormatCheckCompletion
from promptarchitect.log_error import LogError, Severity
from promptarchitect.ollama_completion import OllamaCompletion
from promptarchitect.openai_completion import OpenAICompletion
from promptarchitect.prompt_file import PromptFile

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
coloredlogs.install(level="INFO")


class EngineeredPrompt:
    def __init__(
        self, prompt_file_path: str, output_path: str = "text", cache_expiration=None
    ) -> None:
        self._prompt = ""
        self.prompt_file_path = prompt_file_path
        self.output_path = output_path
        self.cache_expiration = cache_expiration  # Expiration time in seconds

        self.input_text = ""
        self.input_file = None
        self.errors = LogError()  # Initialize an empty list to store error messages
        self.completion = None  # Declare the completion object
        self.latency = 0.0
        self.cost = 0.0

        self.prompt_file = PromptFile(prompt_file_path)
        self.response_text = None
        self.setup_completion()  # Setup completion object

    def __enter__(self):
        """Enter the runtime context and try to load from cache."""
        if not self.load_from_cache():
            logger.info(
                "No valid cache found or cache is expired; proceeding with execution."
            )
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Exit the runtime context and store the result to cache if no
        exception occurred.

        Parameters:
            exc_type: The exception type.
            exc_value: The exception value.
            traceback: The traceback.
        """
        if exc_type is None:  # Only store to cache if no exception was raised
            self.store_to_cache()
        else:
            logger.error(f"An error occurred: {exc_value}")

    def setup_completion(self):
        self.provider = self.prompt_file.metadata.get("provider", "openai")

        try:
            system_role_file = self.prompt_file.metadata.get("system_role", "")
            if system_role_file:
                with open(system_role_file, "r") as file:
                    system_role = file.read()
            else:
                system_role = "You are a helpful assistant."

            if self.provider.lower() == "openai":
                self.completion = OpenAICompletion(
                    system_role=system_role,
                    model=self.prompt_file.metadata["model"]
                    if "model" in self.prompt_file.metadata
                    else None,
                    parameters=self.prompt_file.metadata,
                )
            elif self.provider.lower() == "anthropic":
                self.completion = ClaudeCompletion(
                    system_role=system_role,
                    model=self.prompt_file.metadata["model"]
                    if "model" in self.prompt_file.metadata
                    else None,
                    parameters=self.prompt_file.metadata,
                )
            elif self.provider.lower() == "ollama":
                self.completion = OllamaCompletion(
                    system_role=system_role,
                    model=self.prompt_file.metadata["model"]
                    if "model" in self.prompt_file.metadata
                    else None,
                    parameters=self.prompt_file.metadata,
                )
            else:
                raise ValueError(f"Provider {self.provider} not supported.")

            os.makedirs(self.output_path, exist_ok=True)
        except Exception as e:
            self.errors.log_error(
                name=self.prompt_file.filename,
                message=f"Error initializing completion: {e}",
                severity=Severity.ERROR,
            )

    def _get_input_text(self, input_text, input_file):
        """
        Get the input text from the input text, input file or the prompt file.
        In this order of priority:
            1. input_text
            2. input_file
            3. prompt_file.metadata["input"]

        Parameters:
            input_text (str): The input text to complete.
            input_file (str): The path to the input file.

        Returns:
            str: The input text.
        """

        if input_text and input_file:
            logger.debug(
                "Both input_text and input_file provided. "
                "Using input_text and ignoring input_file."
            )

        if input_text is None and input_file is None:
            # Read the input text from the prompt file metadata
            input_text = self.read_from_input_file(
                self.prompt_file.metadata.get("input")
            )
        else:
            input_text = self.read_from_input_file(input_file) if input_file else ""

        # If input_text is not None, use it as the input text
        return input_text

    def execute(self, input_text: str = None, input_file: str = None) -> str:
        """
        Execute the prompt completion for the EngineeredPrompt object.
        Parameters:
            input_text (str): The input text to complete.
            input_file (str): The path to the input file.

            The for the prompt will be prioritized in this order:
            1. input_text
            2. input_file
            3. prompt_file.metadata["input"]

        Returns:
            str: The completion response message.
        """

        if not self.completion:
            self.setup_completion()

        if self.response_text:  # Check if completion is already loaded from the cache
            logger.info("Using cached completion.")
            return self.response_text

        input_text = self._get_input_text(input_text, input_file)

        logger.debug(f"This is the input text: {input_text}")

        logger.info(f"Executing completion for {self.prompt_file.filename}")
        prompt = f"{self.prompt_file.prompt}\n{input_text}"
        self.response_text = self.completion.completion(prompt=prompt)
        self.input_file = input_file
        self.latency = self.completion.latency
        self.cost = self.completion.cost

        self.store_to_text(self.response_text)
        return self.response_text

    def read_from_input_file(self, input_file: str) -> str:
        if not input_file:
            return ""

        try:
            with open(input_file, "r") as file:
                input_text = file.read()
            return input_text
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Input file {input_file} not found: {e}")
            return ""
        except PermissionError as e:
            raise PermissionError(f"Error reading input file {input_file}: {e}")
            return ""
        except Exception as e:
            raise Exception(f"Error reading input file {input_file}: {e}")
            return ""

    def get_output_path(self):
        return os.path.join(self.output_path, self.prompt_file.metadata["output"])

    def store_to_text(self, response_text: str):
        output_path = os.path.join(
            self.output_path, self.prompt_file.metadata["output"]
        )
        if (
            "response_format" in self.prompt_file.metadata
            and "json" in self.prompt_file.metadata["response_format"]
        ):
            with open(output_path, "w") as file:
                json.dump(self.completion.response_message, file, indent=4)
        else:
            with open(output_path, "w") as file:
                file.write(self.completion.response_message)

        return output_path

    def store_to_cache(self):
        """Store the completion to a cache file."""
        cache_dir = os.path.join(self.output_path, "cache")
        os.makedirs(cache_dir, exist_ok=True)
        cache_file = os.path.join(
            cache_dir, f"{self.prompt_file.metadata['output']}.json"
        )

        with open(cache_file, "w") as file:
            json.dump(self.to_dict(), file, indent=4)

        logger.info(f"Stored completion to cache: {cache_file}")

    def load_from_cache(self) -> bool:
        """Load the completion from a cache file if it exists and isn't expired."""
        cache_file = os.path.join(
            self.output_path, f"cache/{self.prompt_file.metadata['output']}.json"
        )

        if not os.path.exists(cache_file) or os.path.getsize(cache_file) == 0:
            return False

        # Check if the cache is expired
        if self.cache_expiration:
            file_mtime = os.path.getmtime(cache_file)
            current_time = time.time()
            if current_time - file_mtime > self.cache_expiration:
                logger.info("Cache expired; re-executing prompt.")
                return False

        with open(cache_file, "r") as file:
            data = json.load(file)

        self.update_from_dict(data)
        logger.info(f"Loaded completion from cache: {cache_file}")
        return True

    def update_from_dict(self, data):
        """Update current instance with data from a dictionary."""
        self.input_file = data.get("input_file", self.input_file)
        self.input_text = data.get("input_text", self.input_text)
        self.latency = data.get("latency", self.latency)
        self.cost = data.get("cost", self.cost)
        self.errors = LogError.from_dict(data.get("errors", {}))
        self.response_text = data.get("response_text", "")

        # Use a dictionary to map completion types to their corresponding classes
        completion_classes = {
            "CalculatedCompletion": CalculatedCompletion,
            "FormatCheckCompletion": FormatCheckCompletion,
            "ollama": OllamaCompletion,
            "anthropic": ClaudeCompletion,
            "openai": OpenAICompletion,
        }

        completion_type = data.get("completion_type", "OpenAICompletion")
        completion_class = completion_classes.get(completion_type)

        if completion_class:
            self.completion = completion_class.from_dict(data["completion"])

        if self.completion:
            self.completion.response_message = data.get("response_message", "")

    def to_dict(self):
        return {
            "provider": self.provider,
            "prompt_file_path": self.prompt_file_path,
            "output_path": self.output_path,
            "input_file": self.input_file,
            "input_text": self.input_text,
            "latency": self.latency,
            "cost": self.cost,
            "errors": self.errors.to_dict(),
            "completion": self.completion.to_dict() if self.completion else None,
            "completion_type": (
                self.completion.__class__.__name__ if self.completion else None
            ),
            "response_message": (
                self.completion.response_message if self.completion else ""
            ),
            "response_text": self.response_text
            if hasattr(self, "response_text")
            else "",
        }

    @classmethod
    def from_dict(cls, data):
        obj = cls(data["prompt_file_path"], data["output_path"])
        obj.input_file = data["input_file"]
        obj.input_text = data["input_text"]
        obj.latency = data["latency"]
        obj.cost = data["cost"]
        obj.errors = (
            LogError.from_dict(data["errors"]) if data.get("errors") else LogError()
        )

        completion_type = data.get("completion_type", "OpenAICompletion")
        if completion_type == "CalculatedCompletion":
            obj.completion = CalculatedCompletion.from_dict(data["completion"])
        elif completion_type == "FormatCheckCompletion":
            obj.completion = FormatCheckCompletion.from_dict(data["completion"])
        elif completion_type == "ollama":
            obj.completion = OllamaCompletion.from_dict(data["completion"])
        elif completion_type == "anthropic":
            obj.completion = ClaudeCompletion.from_dict(data["completion"])
        elif completion_type == "openai":
            obj.completion = OpenAICompletion.from_dict(data["completion"])

        return obj
