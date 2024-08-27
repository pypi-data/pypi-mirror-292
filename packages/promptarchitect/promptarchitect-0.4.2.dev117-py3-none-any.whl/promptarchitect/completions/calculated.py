import re
from enum import Enum
from timeit import default_timer

from promptarchitect.completions.core import Completion


class Operation(Enum):
    MAX = "max"
    MIN = "min"
    COUNT = "count"


class Unit(Enum):
    LINES = "lines"
    WORDS = "words"
    CHARACTERS = "characters"
    SENTENCES = "sentences"


class CalculatedCompletion(Completion):
    SYSTEM_ROLE = "Calculate the number of lines, words, characters, or sentences in the prompt. No LLM is used for this."  # noqa

    def __init__(self, parameters={}):
        super().__init__(
            system_role=self.SYSTEM_ROLE,
            model=None,
            parameters=parameters,
            provider_file=None,
            rule_based=True,
        )

        self.system_role = self.SYSTEM_ROLE
        self.model = "calculated"

    def _build_regex_pattern(self):
        operations = "|".join(op.name for op in Operation)
        units = "|".join(unit.name for unit in Unit)
        pattern = rf"({operations})\(({units})\)\s*==\s*(\d+)"
        return pattern

    def _parse_comment(self, comment):
        pattern = self._build_regex_pattern()
        matches = list(re.finditer(pattern, comment, re.IGNORECASE))

        if len(matches) != 1:
            raise ValueError("There must be exactly one operation per comment.")

        match = matches[0]
        operation_type = match.group(1).upper()
        unit_type = match.group(2).upper()
        expected_result = int(match.group(3))

        operation = Operation[operation_type]
        unit = Unit[unit_type]

        return operation, unit, expected_result

    def calculated_operations_used(self, comment):
        """
        Check if the comment contains a calculated operation.

        Calculates the number of lines, words, characters, or sentences in the prompt.

        Parameters:
            comment (str): The comment to check for calculated operations.

        Returns:
            bool: True if a calculated operation is found, False otherwise.

        """

        pattern = self._build_regex_pattern()
        return bool(re.search(pattern, comment, re.IGNORECASE))

    def completion(self, prompt: str) -> str:
        response = ""
        start = default_timer()
        # Split the prompt into calculation and prompt
        calculation, _, prompt_to_calculate = prompt.partition("\n")
        operation, unit, expected = self._parse_comment(calculation)
        passed, calculation = self._apply_test_operation(
            prompt_to_calculate, operation, unit, expected
        )

        if passed:
            response = "JA"
        else:
            response = (
                f"NEE, {operation.name}({unit.name}) is niet gelijk {expected}, "
                f"maar {calculation}"
            )
        self.response_message = response
        self.duration = default_timer() - start
        return response

    def _apply_test_operation(
        self, data: str, operation: Operation, unit: Unit, expected: int
    ):
        try:
            if unit == Unit.LINES:
                items = data.split("\n")
            elif unit == Unit.SENTENCES:
                items = re.split(r"[.!?]", data)
            elif unit == Unit.WORDS:
                items = data.split()
            elif unit == Unit.CHARACTERS:
                items = list(data)  # Convert string to list of characters
            else:
                raise ValueError(f"Unsupported unit: {unit}")

            count = len(items)

            if operation == Operation.MAX:
                # Check if the maximum length of any item does not exceed
                # the expected value
                return len(items) <= expected, count
            elif operation == Operation.MIN:
                # Check if the minimum length of any item is greater than or
                # equal to the expected value
                return len(items) >= expected, count
            elif operation == Operation.COUNT:
                # Compare the total count of items with the expected value
                return len(items) == expected, count
            else:
                raise ValueError(f"Unsupported operation: {operation}")

        except Exception as e:
            print(f"An error occurred while applying the operation: {str(e)}")
            return False, count

    def to_dict(self):
        return {
            "system_role": self.system_role,
            "model": self.model,
            "parameters": self.parameters,
            "response_message": self.response_message,
            "duration": self.duration,
            "cost": self.cost,
        }

    @classmethod
    def from_dict(cls, data):
        obj = cls(parameters=data.get("parameters", {}))
        obj.system_role = data.get("system_role", cls.SYSTEM_ROLE)
        obj.model = data.get("model", "calculated")
        obj.response_message = data.get("response_message", "")
        obj.duration = data.get("duration", 0.0)
        obj.cost = data.get("cost", 0.0)
        return obj
