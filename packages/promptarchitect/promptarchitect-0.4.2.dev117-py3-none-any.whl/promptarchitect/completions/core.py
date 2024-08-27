import json
import logging
from abc import ABC, abstractmethod
from pathlib import Path

# Configuring logging
logger = logging.getLogger(__name__)


class Completion(ABC):
    """
    Abstract base class for completions.
    """

    def __init__(
        self,
        system_role: str,
        model: str,
        parameters: dict,
        provider_file: str,
        rule_based: bool = False,
    ):
        """
        Initialize the CompletionBase class with necessary configuration.

        Args:
            system_role (str): The role assigned to the system in the conversation.
            model (str): The model used for the API calls.
            parameters (dict): Additional parameters for the completion request.
            model_provider_config (str): Path to the model provider configuration file.
        """
        if not rule_based:
            provider_file_path = (
                Path(__file__).parent.parent / "provider" / provider_file
            )

            with open(provider_file_path, "r") as config_pricing_file:
                self.provider_file = json.load(config_pricing_file)

            if model is None:
                # Search for the model name where the default is True
                model = self.get_default_model()

            # Check if the model is supported in the provider file as key or as alias
            self.model = self._get_model_name(self.provider_file, model)
            if self.model is None:
                raise ValueError(
                    f"Model {model} not supported. Check the provider file {provider_file}."  # noqa: E501
                )

        self.system_role = system_role
        self.prompt = ""
        self.parameters = parameters
        self.cost = 0.0
        self.is_json = False
        self.test_path = ""
        self.response_message = ""
        self.duration = 0.0

    def _get_model_name(self, data, search_string):
        for key, value in data.items():
            if key == search_string or value.get("alias") == search_string:
                return key
        return None

    def _calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """
        Calculate the cost of the completion based on the number of tokens.

        Args:
            input_tokens (int): The number of input tokens.
            output_tokens (int): The number of output tokens.

        Returns:
            float: The cost of the completion.
        """
        cost = (
            input_tokens * self.provider_file[self.model]["input_tokens"]
            + output_tokens * self.provider_file[self.model]["output_tokens"]
        )
        return cost

    def get_default_model(self):
        """
        Get the default model from the provider file.
        """
        for model_name, model_config in self.provider_file.items():
            if model_config.get("default", False):
                return model_name
        return None

    @abstractmethod
    def completion(self, prompt: str) -> str:
        """
        Perform a completion task with the given data.
        This method should be overridden by derived classes.
        """
        raise NotImplementedError("Subclasses must override this method.")

    def to_dict(self):
        """
        Convert the completion to a dictionary.
        """
        return {
            "system_role": self.system_role,
            "prompt": self.prompt,
            "model": self.model,
            "parameters": self.parameters if self.parameters else {},
            "cost": self.cost,
            "is_json": self.is_json,
            "test_path": self.test_path,
            "response_message": self.response_message,
            "duration": self.duration,
            "provider_file": self.provider_file,
        }

    @classmethod
    def from_dict(cls, data):
        """
        Create a completion from a dictionary.
        """
        completion = cls(
            system_role=data["system_role"],
            model=data["model"],
            parameters=data["parameters"],
            provider_file=data["provider_file"],
        )
        completion.prompt = data["prompt"]
        completion.cost = data["cost"]
        completion.is_json = data["is_json"]
        completion.test_path = data["test_path"]
        completion.response_message = data["response_message"]
        completion.duration = data["duration"]
        return completion
