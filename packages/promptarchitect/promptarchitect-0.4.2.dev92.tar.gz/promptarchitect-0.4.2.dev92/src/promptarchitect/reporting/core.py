from abc import ABC
from typing import List

from promptarchitect.validation.testcases import TestCaseOutcome


class TestReporter(ABC):
    """Base class for building a test reporter."""

    report_path: str

    def __init__(self, report_path: str):
        """
        Initialize the test reporter.

        Parameters
        ----------
        report_path : str
            The path to the report
        """
        self.report_path = report_path

    def generate_report(self, test_outcomes: List[TestCaseOutcome]):
        pass
