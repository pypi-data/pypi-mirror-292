from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from promptarchitect.prompting import EngineeredPrompt
from promptarchitect.specification import (
    FormatTestSpecification,
    PromptInput,
    PromptOutputFormat,
)
from promptarchitect.validation.testcases import (
    FormatTestCase,
    TestCaseStatus,
)


def create_prompt_with_response(response: str) -> EngineeredPrompt:
    prompt = MagicMock()
    prompt.run = MagicMock()
    prompt.run.return_value = response

    return prompt  # noqa


@pytest.fixture
def input_sample():
    return PromptInput(id=str(uuid4()), input="Sample input", properties={})


def test_is_valid_html(input_sample):
    prompt = create_prompt_with_response("<html><body><p>Valid HTML</p></body></html>")
    spec = FormatTestSpecification(format=PromptOutputFormat.HTML)
    test_case = FormatTestCase("test_id", prompt, input_sample, spec)

    outcome = test_case.run()

    assert outcome.status == TestCaseStatus.PASSED


def test_is_valid_json(input_sample):
    prompt = create_prompt_with_response('{ "key": "value" }')
    spec = FormatTestSpecification(format=PromptOutputFormat.JSON)
    test_case = FormatTestCase("test_id", prompt, input_sample, spec)

    outcome = test_case.run()

    assert outcome.status == TestCaseStatus.PASSED


def test_is_invalid_json(input_sample):
    prompt = create_prompt_with_response('{ "key": "value }')
    spec = FormatTestSpecification(format=PromptOutputFormat.JSON)
    test_case = FormatTestCase("test_id", prompt, input_sample, spec)

    outcome = test_case.run()

    assert outcome.status == TestCaseStatus.FAILED


def test_is_valid_markdown(input_sample):
    prompt = create_prompt_with_response("# Stuff\n\nSome text.")
    spec = FormatTestSpecification(format=PromptOutputFormat.MARKDOWN)
    test_case = FormatTestCase("test_id", prompt, input_sample, spec)

    outcome = test_case.run()

    assert outcome.status == TestCaseStatus.PASSED
