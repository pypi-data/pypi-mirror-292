import json
import logging
import re
import timeit

import coloredlogs
import dotenv
import ollama
import requests

from promptarchitect.completions.core import Completion

# Configuring logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
coloredlogs.install(level="INFO")
dotenv.load_dotenv()


class OllamaCompletion(Completion):
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

        super().__init__(system_role, model, parameters, "ollama.json")

        # Check if the model is downloaded and available
        if self.model not in self.list_models():
            raise ValueError(
                f"Model {self.model} is not available. Please download it. "
                "Use the download_model() method to download the model.\n"
                "Visit https://ollama.com/ for more information on available models."
            )

        self.api_key = None

    def _is_ollama_server_running(url="http://localhost:11434"):
        """
        Check if the Ollama server is running by sending a GET request to the server.

        Parameters
        ----------
        url : str
            The URL of the Ollama server. Defaults to 'http://localhost:11434'.

        Returns
        -------
        bool
            True if the server is running, False otherwise.

        """
        try:
            response = requests.get(url)
            # If the server is running, it should return a status code of 200
            if response.status_code == requests.codes.ok:
                return True
            else:
                return False
        except requests.ConnectionError:
            # If the connection fails, the server is not running
            return False

    def list_models(self):
        """
        Lists the available models for Ollama.
        """
        return ollama.list()

    def delete_model(self, model):
        logger.debug(f"Deleting model {model}")
        ollama.delete(model)

    def download_model(self, model):
        logger.debug(f"Downloading model {model}")
        ollama.pull(model)
        logger.debug(f"Model {model} downloaded")

    def completion(self, prompt: str) -> str:
        """
        Fetches a completion for a given prompt using specified parameters.

        Args:
            parameters (dict, optional): Additional parameters for the completion
            request. Defaults to None.

        Returns:
            str: The content of the completion.
        """

        # Check if Ollama server is running
        if not self._is_ollama_server_running():
            raise ValueError(
                "Ollama server is not running. Please start the server or install "
                "the Ollama package. Visit https://ollama.com/ for more information."
            )

        self.prompt = prompt

        request = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": self.system_role + " " + self.prompt},
            ],
        }

        if "response_format" in self.parameters:
            self.is_json = True
            if self.parameters["response_format"].strip() in ["json"]:
                response_format = {"format": "json"}
                self.parameters["response_format"] = response_format

        # # Add the parameters to the request
        if self.parameters is not None:
            for key, value in self.parameters.items():
                if key in [
                    "temperature",
                ]:
                    if key in ["temperature"] and value:
                        request["options"] = {"temperature": float(value)}

        try:
            # Calculate the duration of the completion
            start = timeit.default_timer()

            # Calling the local model
            response = ollama.chat(**request)

            end = timeit.default_timer()
            self.duration = end - start
        except ollama.ResponseError as e:
            raise ValueError(f"Ollama error: {e.error}")

        self._response = dict(response)
        # Calculate the cost of the completion
        # For now we calculate the cost as 0.0
        self.cost = self._calculate_cost(0.0, 0.0)

        self.response_message = response["message"]["content"]
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
