"""Implements the validation logic of promptarchitect."""

import logging
import os
from itertools import product
from os import PathLike
from typing import List, Literal, Tuple

from pydantic import BaseModel

from promptarchitect.prompting import EngineeredPrompt
from promptarchitect.reporting import create_test_reporter
from promptarchitect.specification import EngineeredPromptSpecification, PromptInput
from promptarchitect.validation.testcases import (
    TestCase,
    TestCaseOutcome,
    create_test_case,
)

logger = logging.getLogger(__name__)


def discover_input_samples(
    prompt_spec: EngineeredPromptSpecification,
) -> List[PromptInput]:
    """
    Discover input samples for an engineered prompt specification.

    Parameters
    ----------
    prompt_spec: EngineeredPromptSpecification

    Returns
    -------
    List[PromptInput]
        List of input samples for the prompt.
    """
    sample_files = sorted([
        f for f in os.listdir(prompt_spec.metadata.test_path) if f.endswith(".md") or f.endswith(".txt")
    ])

    input_samples = [
        PromptInput.from_file(os.path.join(prompt_spec.metadata.test_path, f))
        for f in sample_files
    ]

    return input_samples


def discover_test_cases(
    path: PathLike,
) -> Tuple[List[EngineeredPromptSpecification], List[TestCase]]:
    """
    Discovers test cases from the given ø.

    Parameters
    ----------
    path: Path where to search for prompt files.

    Returns
    -------
    Tuple[List[EngineeredPromptSpecification], List[TestCase]]
        Tuple containing the list of discovered prompts and test cases.
    """

    prompt_files = sorted([f for f in os.listdir(path) if f.endswith(".prompt")])

    prompt_specs = [
        EngineeredPromptSpecification.from_file(os.path.join(path, f))
        for f in prompt_files
    ]

    test_cases = []

    for prompt_spec in prompt_specs:
        prompt = EngineeredPrompt(prompt_spec)
        input_samples = discover_input_samples(prompt_spec)

        # We're generating a cartesian product of the input samples and test specifications.
        # We need a test case per input spample per test spec.
        test_input_combinations = product(
            input_samples, prompt_spec.metadata.tests.keys()
        )

        for input_sample, test_spec_id in test_input_combinations:
            test_spec = prompt_spec.metadata.tests[test_spec_id]

            test_case = create_test_case(
                test_id=test_spec_id,
                prompt=prompt,
                spec=test_spec,
                input_sample=input_sample,
            )

            test_cases.append(test_case)

    return (prompt_specs, test_cases)


class SessionConfiguration(BaseModel):
    """
    Configures the test session.

    Attributes
    ----------
    prompt_path: PathLike
        The path to the directory containing the prompts.
    output_path: PathLike
        The path to the directory where the generated prompts will be saved.
    template_path: PathLike
        The path to the directory containing the templates for the test report.
    report_path: PathLike
        The path to the directory where the test report will be saved.
    report_format: Literal["html", "json"]
    """

    prompt_path: PathLike
    output_path: PathLike
    template_path: PathLike
    report_path: PathLike
    report_format: Literal["html", "json"]


class TestSession:
    """
    A test session contains the process logic needed to run tests against a set of engineered prompts.

    Attributes
    ----------
    config: SessionConfiguration
        The configuration for the test session.
    test_cases: List[TestCase]
        The list of discovered test cases.
    """

    prompts: List[EngineeredPromptSpecification]
    test_cases: List[TestCase]
    test_outcomes: List[TestCaseOutcome]

    def __init__(self, config: SessionConfiguration):
        """
        Initialize the test session.

        Parameters
        ----------
        config: SessionConfiguration
            The configuration for the test session.
        """
        self.config = config

    def start(self):
        """Starts the test session."""

        self._discover_tests()
        self._run_tests()
        self._report_test_results()

        logger.info("Test session completed.")

    def _discover_tests(self):
        logger.info("Discovering test cases from path %s", self.config.prompt_path)

        self.prompts, self.test_cases = discover_test_cases(self.config.prompt_path)

        logger.info(
            "Discovered %d prompts and %d test cases.",
            len(self.prompts),
            len(self.test_cases),
        )

    def _run_tests(self):
        logger.info("Running test cases.")

        test_outcomes = []

        for test_case in self.test_cases:
            outcome = test_case.run()
            test_outcomes.append(outcome)

            logger.info(
                "Test case %s completed with status %s",
                test_case.test_id,
                outcome.status,
            )

        self.test_outcomes = test_outcomes

    def _report_test_results(self):
        logger.info("Generating test report.")

        reporter = create_test_reporter(
            self.config.report_format, self.config.report_path
        )

        reporter.generate_report(self.test_outcomes)

        logger.info("Completed generating report at %s.", self.config.report_path)
