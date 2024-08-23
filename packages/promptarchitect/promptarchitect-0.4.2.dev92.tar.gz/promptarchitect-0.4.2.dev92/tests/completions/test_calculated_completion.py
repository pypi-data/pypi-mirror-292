import pytest
from promptarchitect.completions.calculated import (
    CalculatedCompletion,
    Operation,
    Unit,
)


def test_calculated_operations_used():
    completion = CalculatedCompletion()
    comment = "MAX(LINES) == 10"
    assert completion.calculated_operations_used(comment) is True


def test_completion_passed():
    completion = CalculatedCompletion()
    prompt = "MAX(LINES) == 10\nThis is a test prompt."
    expected_response = "JA"
    assert completion.completion(prompt) == expected_response


def test_completion_failed():
    completion = CalculatedCompletion()
    prompt = "MAX(WORDS) == 5\nThis is a test prompt with more than 5 words."
    expected_response = "NEE, MAX(WORDS) is niet gelijk 5, maar 10"
    assert completion.completion(prompt) == expected_response


def test_apply_test_operation_lines_max_passed():
    completion = CalculatedCompletion()
    data = (
        "Line 1\nLine 2\nLine 3\nLine 4\nLine 5\nLine 6\nLine 7\nLine 8\n"
        "Line 9\nLine 10"
    )
    operation = Operation.MAX
    unit = Unit.LINES
    expected = 10
    assert completion._apply_test_operation(data, operation, unit, expected) == (
        True,
        10,
    )


def test_apply_test_operation_lines_max_failed():
    completion = CalculatedCompletion()
    data = (
        "Line 1\nLine 2\nLine 3\nLine 4\nLine 5\nLine 6\nLine 7\nLine 8\n"
        "Line 9\nLine 10\nLine 11"
    )
    operation = Operation.MAX
    unit = Unit.LINES
    expected = 10
    assert completion._apply_test_operation(data, operation, unit, expected) == (
        False,
        11,
    )


def test_calculated_operations_used_no_operation():
    completion = CalculatedCompletion()
    comment = "This is a comment without any calculated operation."
    assert completion.calculated_operations_used(comment) is False


def test_calculated_operations_used_valid_operation():
    completion = CalculatedCompletion()
    comment = "MAX(LINES) == 10"
    assert completion.calculated_operations_used(comment) is True


def test_parse_comment_valid_comment():
    completion = CalculatedCompletion()
    comment = "MAX(LINES) == 10"
    operation, unit, expected_result = completion._parse_comment(comment)
    assert operation == Operation.MAX
    assert unit == Unit.LINES
    assert expected_result == 10


def test_parse_comment_invalid_comment():
    completion = CalculatedCompletion()
    comment = "INVALID_OPERATION(UNIT) == 5"
    with pytest.raises(ValueError):
        completion._parse_comment(comment)
