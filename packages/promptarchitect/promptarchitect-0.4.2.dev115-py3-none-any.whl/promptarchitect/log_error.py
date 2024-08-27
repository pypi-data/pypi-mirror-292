import logging
from enum import Enum

import coloredlogs

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
coloredlogs.install(level="INFO")


Severity = {"ERROR": 0, "WARNING": 1}


class Operation(Enum):
    MAX = "max"
    MIN = "min"
    COUNT = "count"


class Unit(Enum):
    LINES = "lines"
    WORDS = "words"
    CHARACTERS = "characters"


class Severity(Enum):  # noqa
    ERROR = logging.ERROR
    WARNING = logging.WARNING


class LogError:
    def __init__(self):
        self.errors = []
        self.logged_messages = set()  # Set to track logged messages to avoid duplicates
        self.duplicates = 0  # Count of duplicates

    def log_error(
        self, name: str, message: str, severity: Severity, verbose: bool = True
    ):
        error_signature = (name, message)
        if error_signature in self.logged_messages:
            self.duplicates += 1
            if verbose:
                logger.info(severity.value, f"{message} - {name}")
            return  # Prevent duplicate logging

        self.errors.append(
            {"name": name, "message": message, "severity": severity.name}
        )
        self.logged_messages.add(error_signature)

    def count_errors(self, name: str = "") -> int:
        # Count all errors where name is in the key and severity is ERROR
        # If name is empty, count all errors with severity ERROR
        return sum(
            1
            for error in self.errors
            if error["severity"] == "ERROR" and name in error["name"]
        )

    def count_warnings(self, name: str = "") -> int:
        # Count all warnings where name is in the key and severity is WARNING
        # If name is empty, count all errors with severity WARNING
        return sum(
            1
            for error in self.errors
            if error["severity"] == "WARNING" and name in error["name"]
        )

    def to_dict(self):
        return {
            "errors": [
                {
                    "name": err["name"],
                    "message": err["message"],
                    "severity": err["severity"],
                }
                for err in self.errors
            ],
            "duplicates": self.duplicates,
        }

    @classmethod
    def from_dict(cls, data):
        obj = cls()
        obj.errors = data.get("errors", [])
        obj.duplicates = data.get("duplicates", 0)
        # Rebuild the logged_messages set to prevent re-logging of these errors
        obj.logged_messages = {(err["name"], err["message"]) for err in obj.errors}
        return obj
