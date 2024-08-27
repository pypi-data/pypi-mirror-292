import json
import logging
import os
import re
import timeit

import anthropic
import coloredlogs
import dotenv
from retry import retry

from promptarchitect.completions.core import Completion

# Configuring logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
coloredlogs.install(level="INFO")
dotenv.load_dotenv()


class ClaudeCompletion(Completion):
    """
    A class to interact with Anthropic's Claude.ai API to fetch completions for prompts
    using specified models.
    """

    def __init__(self, system_role: str = "", model=None, parameters={}):
        """
        Initialize the ClaudeCompletion class with necessary API client and
        model configuration.

        Args:
            system_role (str): The role assigned to the system in the conversation.
            Defaults to an empty string.
            model (str): The model used for the Claude API calls.
            Defaults to 'claude-3-5-sonnet-20240620'.
        """

        super().__init__(system_role, model, parameters, "anthropic.json")
        self.api_key = None

    @retry(
        (anthropic.AnthropicError),
        delay=5,
        backoff=2,
        max_delay=40,
    )
    def completion(self, prompt: str) -> str:
        """
        Fetches a completion for a given prompt using specified parameters.

        Args:
            parameters (dict, optional): Additional parameters for the completion
            request. Defaults to None.

        Returns:
            str: The content of the completion.
        """

        # Read the API key from the environment
        self.api_key = os.getenv("CLAUDE_API_KEY")

        if not self.api_key:
            raise ValueError("API key for Claude.ai is required. Set CLAUDE_API_KEY.")

        self.prompt = prompt

        client = anthropic.Client(api_key=self.api_key)

        request = {
            "model": self.model,
            "messages": [
                # {"role": "system", "content": self.system_role},
                {"role": "user", "content": self.system_role + " " + self.prompt},
            ],
        }

        if "response_format" in self.parameters:
            self.is_json = True
            if self.parameters["response_format"].strip() in ["json", "json_object"]:
                response_format = {"type": "json_object"}
                self.parameters["response_format"] = response_format

        # Add the parameters to the request
        # Skip the parameters that are not supported by Claude.ai
        if self.parameters is not None:
            for key, value in self.parameters.items():
                if key in [  # These are the parameters that Claude.ai accepts
                    "temperature",
                    "max_tokens",
                ]:
                    if key in ["temperature"] and value:
                        request[key] = float(value)
                    elif key in ["max_tokens"] and value:
                        request[key] = int(value)

        # Max_tokens is required for Claude.ai
        DEFAULT_MAX_TOKENS = (
            8129 if "claude-3-5-sonnet-20240620" in self.model else 4096
        )  # Only claude-3-5-sonnet-20240620 have max_tokens of 8129
        if "max_tokens" not in request:
            request["max_tokens"] = DEFAULT_MAX_TOKENS
            logger.warning(
                f"Parameter max_tokens not set, but is required for Claude.ai. "
                f"Defaulting to {DEFAULT_MAX_TOKENS}. Check the API docs of Anthropic."
            )

        # Warn the user if temperature and top_p are both set
        if "temperature" in request and "top_p" in request:
            logger.warning(
                "Both temperature and top_p are set. This gives unwanted behaviour. "
                "Check the API docs of Anthropic."
            )

        try:
            # Calculate the duration of the completion
            start = timeit.default_timer()
            response = client.messages.create(**request)
            end = timeit.default_timer()
            self.duration = end - start
        except anthropic.BadRequestError as e:
            # Parse and handle the error response
            error_data = json.loads(e.response.text)
            error_message = error_data.get("error", {}).get(
                "message", "An unknown error occurred."
            )
            error_type = error_data.get("error", {}).get("type", "unknown_error")
            raise ValueError(f"Error Type: {error_type} - {error_message}")

        except anthropic.AnthropicError as e:
            # Handle general Anthropic API errors
            error_data = json.loads(e.response.text)
            error_message = error_data.get("error", {}).get(
                "message", "An unknown error occurred."
            )
            error_type = error_data.get("error", {}).get("type", "unknown_error")
            raise RuntimeError(f"Error Type: {error_type} - {error_message}")

        except Exception as e:
            # Handle any other unforeseen errors
            raise RuntimeError(f"An unexpected error occurred: {str(e)}")

        self._response = dict(response)
        # Calculate the cost of the completion

        self.cost = self._calculate_cost(
            self._response["usage"].input_tokens,
            self._response["usage"].output_tokens,
        )

        self.response_message = response.content[0].text
        if self.is_json:
            # Claude.ai has the quirks of returning JSON in a weird format
            # With starting and ending quotes. So we need to extract the JSON
            self.response_message = self._extract_json(self.response_message)

        return self.response_message

    def _extract_json(self, text):
        # Regular expression pattern to find text that looks like JSON
        # This pattern assumes JSON starts with '[' or '{' and ends with ']' or '}'
        pattern = r"\{[\s\S]*\}|\[[\s\S]*\]"

        # Searching the text for JSON pattern
        match = re.search(pattern, text)

        if match:
            json_text = match.group(0)
            try:
                # Validating and returning the JSON object
                _ = json.loads(json_text)
                return json_text
            except json.JSONDecodeError:
                return "The extracted text is not valid JSON."
        else:
            return "No JSON found in the text."

    def to_dict(self):
        data = super().to_dict()
        data.update(
            {
                "provider_file": "claude.json",
            }
        )
        return data

    @classmethod
    def from_dict(cls, data):
        obj = cls(
            system_role=data["system_role"],
            model=data["model"],
            parameters=data["parameters"],
        )
        obj.prompt = data.get("prompt", "")
        obj.cost = data.get("cost", 0.0)
        obj.is_json = data.get("is_json", False)
        obj.test_path = data.get("test_path", "")
        obj.response_message = data.get("response_message", "")
        obj.duration = data.get("duration", 0.0)
        return obj
