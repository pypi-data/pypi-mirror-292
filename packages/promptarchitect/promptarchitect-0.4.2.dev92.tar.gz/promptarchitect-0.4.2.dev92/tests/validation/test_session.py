import pytest
from promptarchitect.prompting import EngineeredPrompt
from promptarchitect.specification import (
    EngineeredPromptMetadata,
    EngineeredPromptSpecification,
)
from promptarchitect.validation import SessionConfiguration, TestSession
from unittest.mock import patch

from promptarchitect.validation.testcases import (
    ModelCosts,
    TestCase,
    TestCaseOutcome,
    TestCaseStatus,
)


class FakeTestCase(TestCase):
    def __init__(self, id: str, prompt: EngineeredPrompt):
        self.test_id = id
        self.prompt = prompt

    def run(self):
        model_costs = ModelCosts(input_tokens=0, output_tokens=0, costs=0.0)

        return TestCaseOutcome(
            test_id=self.test_id,
            status=TestCaseStatus.PASSED,
            duration=0,
            costs=model_costs,
        )


@pytest.fixture
def valid_config():
    return {
        "prompt_path": "/path/to/prompts",
        "output_path": "/path/to/output",
        "template_path": "/path/to/templates",
        "report_path": "/path/to/report",
        "report_format": "html",
    }


@pytest.fixture
def valid_spec():
    return EngineeredPromptSpecification(
        metadata=EngineeredPromptMetadata(
            provider="openai",
            model="gpt-4o-mini",
            test_path="/path/to/tests",
            tests={},
        ),
        prompt="Placeholder prompt.",
        filename="test_prompt.prompt",
    )


@pytest.fixture
def dummy_test_case(valid_spec):
    return FakeTestCase("test01", EngineeredPrompt(valid_spec))


def test_test_session_initialization(valid_config):
    config = SessionConfiguration(**valid_config)
    session = TestSession(config)

    assert session.config == config


@patch("promptarchitect.validation.discover_test_cases")
def test_start_session(
    mock_discover_test_cases, valid_config, dummy_test_case, valid_spec
):
    mock_discover_test_cases.return_value = ([valid_spec], [dummy_test_case])

    config = SessionConfiguration(**valid_config)
    session = TestSession(config)

    session.start()

    mock_discover_test_cases.assert_called_once()

    assert len(session.test_cases) == 1
    assert len(session.prompts) == 1
    assert len(session.test_outcomes) == 1
