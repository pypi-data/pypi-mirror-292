import pytest
from promptarchitect.log_error import LogError, Severity


def test_log_error():
    error = LogError()
    error.log_error("Test Error", "This is a test error", Severity.ERROR)
    assert len(error.errors) == 1


def test_count_errors():
    error = LogError()
    error.log_error("Test Error", "This is a test error", Severity.ERROR)
    error.log_error("Test Warning", "This is a test warning", Severity.WARNING)
    assert error.count_errors() == 1
    assert error.count_errors("Test") == 1


def test_count_warnings():
    error = LogError()
    error.log_error("Test Error", "This is a test error", Severity.ERROR)
    error.log_error("Test Warning", "This is a test warning", Severity.WARNING)
    assert error.count_warnings() == 1
    assert error.count_warnings("Test") == 1


def test_to_dict():
    error = LogError()
    error.log_error("Test Error", "This is a test error", Severity.ERROR)
    error_dict = error.to_dict()
    assert "errors" in error_dict
    assert "duplicates" in error_dict


def test_from_dict():
    error_dict = {
        "errors": [
            {
                "name": "Test Error",
                "message": "This is a test error",
                "severity": "ERROR",
            }
        ],
        "duplicates": 0,
    }
    error = LogError.from_dict(error_dict)
    assert len(error.errors) == 1
    assert error.duplicates == 0


if __name__ == "__main__":
    pytest.main([__file__])
