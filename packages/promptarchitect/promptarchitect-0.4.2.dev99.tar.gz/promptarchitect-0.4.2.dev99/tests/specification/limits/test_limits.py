import pytest
from pydantic import ValidationError
from promptarchitect.specification import Limits


def test_min_and_max_none():
    with pytest.raises(ValidationError) as excinfo:
        Limits()
    assert "You must specify at least one of min or max values." in str(excinfo.value)


def test_only_min_specified():
    limit = Limits(min=5)
    assert limit.min == 5
    assert limit.max is None


def test_only_max_specified():
    limit = Limits(max=10)
    assert limit.min is None
    assert limit.max == 10


def test_min_and_max_specified_correctly():
    limit = Limits(min=5, max=10)
    assert limit.min == 5
    assert limit.max == 10


def test_min_greater_than_max():
    with pytest.raises(ValidationError) as excinfo:
        Limits(min=10, max=5)
    assert "The min value must be less than the max value." in str(excinfo.value)
