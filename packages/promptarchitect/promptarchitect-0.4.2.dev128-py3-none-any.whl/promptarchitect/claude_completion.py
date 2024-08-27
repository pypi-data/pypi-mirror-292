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

    def _get_api_key(self) -> str:
        api_key = os.getenv("CLAUDE_API_KEY")
        if not api_key:
            raise ValueError("API key for Claude.ai is required. Set CLAUDE_API_KEY.")
        return api_key

    def _prepare_request(self, prompt: str) -> dict:
        request = {
            "model": self.model,
            "messages": [{"role": "user", "content": f"{self.system_role} {prompt}"}],
        }

        self._handle_response_format()

        for key, value in self.parameters.items():
            if key in ["temperature", "max_tokens"]:
                request[key] = self._cast_parameter_value(key, value)

        request["max_tokens"] = request.get("max_tokens", self._default_max_tokens())
        self._check_conflicting_parameters(request)

        return request

    def _handle_response_format(self):
        if "response_format" in self.parameters:
            self.is_json = True
            if self.parameters["response_format"].strip() in ["json", "json_object"]:
                self.parameters["response_format"] = {"type": "json_object"}

    def _cast_parameter_value(self, key: str, value) -> float or int:
        if key == "temperature":
            return float(value)
        elif key == "max_tokens":
            return int(value)

    def _default_max_tokens(self) -> int:
        if "claude-3-5-sonnet-20240620" in self.model:
            return 8129
        return 4096

    def _check_conflicting_parameters(self, request: dict):
        if "temperature" in request and "top_p" in request:
            logger.warning(
                "Both temperature and top_p are set. This gives unwanted behaviour. "
                "Check the API docs of Anthropic."
            )

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

        self.api_key = self._get_api_key()
        self.prompt = prompt
        self.client = anthropic.Client(api_key=self.api_key)

        request = self._prepare_request(prompt)

        try:
            self._execute_request(request)
        except anthropic.BadRequestError as e:
            self._handle_bad_request(e)
        except anthropic.AnthropicError as e:
            self._handle_anthropic_error(e)
        except Exception as e:
            raise RuntimeError(f"An unexpected error occurred: {str(e)}")

        return self._process_response()

    def _execute_request(self, request: dict):
        start = timeit.default_timer()
        response = self.client.messages.create(**request)
        end = timeit.default_timer()

        self.duration = end - start
        self._response = dict(response)

    def _handle_bad_request(self, error: anthropic.BadRequestError):
        error_data = json.loads(error.response.text)
        error_message = error_data.get("error", {}).get(
            "message", "An unknown error occurred."
        )
        error_type = error_data.get("error", {}).get("type", "unknown_error")
        raise ValueError(f"Error Type: {error_type} - {error_message}")

    def _handle_anthropic_error(self, error: anthropic.AnthropicError):
        error_data = json.loads(error.response.text)
        error_message = error_data.get("error", {}).get(
            "message", "An unknown error occurred."
        )
        error_type = error_data.get("error", {}).get("type", "unknown_error")
        raise RuntimeError(f"Error Type: {error_type} - {error_message}")

    def _process_response(self) -> str:
        self.cost = self._calculate_cost(
            self._response["usage"].input_tokens,
            self._response["usage"].output_tokens,
        )

        self.response_message = self._response["content"][0].text
        if self.is_json:
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
