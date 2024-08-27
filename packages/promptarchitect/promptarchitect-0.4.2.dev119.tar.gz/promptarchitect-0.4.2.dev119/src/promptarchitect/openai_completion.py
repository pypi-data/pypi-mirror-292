import json
import logging
import os
import re
import timeit

import coloredlogs
import dotenv
import openai
from openai import OpenAI
from retry import retry

from promptarchitect.completions.core import Completion

# Configuring logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
coloredlogs.install(level="INFO")
dotenv.load_dotenv()


class OpenAICompletion(Completion):
    """
    A class to interact with OpenAI API to fetch completions for prompts using
    specified models.
    """

    def __init__(self, system_role: str = "", model=None, parameters={}):
        """
        Initialize the OpenAICompletion class with necessary API client and
        model configuration.

        Args:
            system_role (str): The role assigned to the system in the conversation.
            Defaults to an empty string.
            model (str): The model used for the OpenAI API calls.
            Defaults to 'gpt-4-turbo-preview'.
        """

        super().__init__(system_role, model, parameters, "openai.json")
        self.api_key = None

    @retry(
        (openai.OpenAIError),
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

        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI()  # Instance of the OpenAI class initialized
        self.prompt = prompt

        request = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": self.system_role},
                {"role": "user", "content": self.prompt},
            ],
        }

        if "response_format" in self.parameters:
            self.is_json = True
            if self.parameters["response_format"].strip() in ["json", "json_object"]:
                response_format = {"type": "json_object"}
                self.parameters["response_format"] = response_format

        # Add the parameters to the request
        if self.parameters is not None:
            for key, value in self.parameters.items():
                if key in [
                    "temperature",
                    "max_tokens",
                    "top_p",
                    "frequency_penalty",
                    "presence_penalty",
                    "stop",
                ]:
                    if key in ["temperature"] and value:
                        request[key] = float(value)
                    elif key in ["max_tokens", "top_p"] and value:
                        request[key] = int(value)
                    else:
                        request[key] = value

        try:
            # Calculate the duration of the completion
            start = timeit.default_timer()
            response = self.client.chat.completions.create(**request)
            end = timeit.default_timer()
            self.duration = end - start
        except openai.BadRequestError as e:
            raise ValueError(f"Bad Request Error (wrong parameters): {e}")

        self._response = dict(response)

        # Calculate the cost of the completion
        self.cost = self._calculate_cost(
            self._response["usage"].prompt_tokens,
            self._response["usage"].completion_tokens,
        )

        self.response_message = response.choices[0].message.content
        if self.is_json:
            # OpenAI has the quirks of returning JSON in a weird format
            # With starting and ending quotes. So we need to extract the JSON
            self.response_message = self._extract_json(self.response_message)

        return self.response_message.strip()

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
                "provider_file": "openai.json",
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
