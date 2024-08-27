import json
import re
from enum import Enum
from timeit import default_timer

import markdown
from bs4 import BeautifulSoup

from promptarchitect.completions.core import Completion


class Format(Enum):
    HTML = "html"
    JSON = "json"
    TEXT = "txt"
    MARKDOWN = "markdown"


class FormatCheckCompletion(Completion):
    # Default system role
    SYSTEM_ROLE = "Check the format of provided text based on predefined formats."

    def __init__(self, parameters=None, format: Format = Format.TEXT):
        super().__init__(
            system_role=self.SYSTEM_ROLE,
            model=None,
            parameters=parameters,
            provider_file=None,
            rule_based=True,
        )

        self.parameters = parameters
        self.system_role = self.SYSTEM_ROLE
        self.format = format
        self.model = "format_checker"
        self.response_message = ""

    def _build_regex_pattern(self) -> str:
        """
        Builds a regex pattern to find format check expressions like 'Format == json'.
        """
        formats = "|".join(f.name for f in Format)
        pattern = rf"FORMAT\s*==\s*({formats})"
        return pattern

    def format_check_used(self, comment: str) -> bool:
        """
        Check if the comment contains a format check expression.

        This searches for patterns of the form 'Format == [format]' where [format]
        is any of the defined formats.

        Parameters:
            comment (str): The comment to check for format check expressions.

        Returns:
            bool: True if a format check expression is found, False otherwise.
        """
        pattern = self._build_regex_pattern()
        return bool(re.search(pattern, comment, re.IGNORECASE))

    def check_format(self, data: str) -> bool:
        """
        Determines if the provided data matches the currently set format.

        Parameters:
            data (str): The data to check.

        Returns:
            bool: True if data matches the format, False otherwise.
        """
        method = {
            Format.HTML: self._is_valid_html,
            Format.JSON: self._is_valid_json,
            Format.TEXT: self._is_valid_text,
            Format.MARKDOWN: self._is_valid_markdown,
        }.get(self.format, self._is_valid_text)

        return method(data)

    def _is_valid_html(self, data: str) -> bool:
        soup = BeautifulSoup(data, "html.parser")
        return bool(soup.find())

    def _is_valid_json(self, data: str) -> bool:
        try:
            json.loads(data)
            return True
        except json.JSONDecodeError:
            return False

    def _is_valid_text(self, data: str) -> bool:
        return bool(data) and not bool(re.search(r"[^\x20-\x7E\s]", data))

    def _is_valid_markdown(self, data: str) -> bool:
        html_output = markdown.markdown(data)
        soup = BeautifulSoup(html_output, "html.parser")
        return bool(soup.find())

    def _parse_comment(self, comment: str):
        pattern = self._build_regex_pattern()
        matches = list(re.finditer(pattern, comment, re.IGNORECASE))

        if len(matches) != 1:
            raise ValueError("There must be exactly one operation per comment.")

        match = matches[0]
        format = match.group(1).upper()

        return Format[format]

    def completion(self, prompt: str) -> str:
        """
        Processes the comment to see if a specific format check expression is used.

        Parameters:
            prompt (str): The full prompt containing both the format check
            and the text to check.

        Returns:
            str: Response message confirming whether the specific format check
            expression is found and if the text matches the expected format.
        """
        start = default_timer()
        # Split the prompt into format check and the text to be checked
        format_check, _, prompt_to_check = prompt.partition("\n")
        try:
            expected_format = self._parse_comment(format_check)
            self.format = expected_format  # Update the format based on the comment
            format_is_correct = self.check_format(prompt_to_check)
            if format_is_correct:
                self.response_message = "JA"
            else:
                self.response_message = f"NEE, het formaat komt niet overeen met het verwachtte formaat ({expected_format.name})."  # noqa: E501
        except ValueError as e:
            self.response_message = str(e)

        self.duration = default_timer() - start
        return self.response_message

    def to_dict(self):
        return {
            "parameters": self.parameters,
            "system_role": self.system_role,
            "model": self.model,
            "format": self.format.value,
            "response_message": self.response_message,
            "duration": self.duration,
            "cost": 0.0,
        }

    @classmethod
    def from_dict(cls, data):
        obj = cls(parameters=data.get("parameters", {}))
        obj.system_role = data.get("system_role", cls.SYSTEM_ROLE)
        obj.model = data.get("model", "format_checker")
        obj.response_message = data.get("response_message", "")
        obj.duration = data.get("duration", 0.0)
        obj.cost = data.get("cost", 0.0)
        return obj
