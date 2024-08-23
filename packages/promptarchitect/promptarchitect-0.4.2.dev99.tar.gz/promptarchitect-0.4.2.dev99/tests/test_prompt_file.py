import pytest
from promptarchitect.prompt_file import PromptFile

# Sample prompt data to use in tests
valid_prompt_content = """
---
provider: openai
model: gpt-4o
input: input.txt
output: output.txt
tests:
  test_01: Test description 1
  test_02: Test description 2
---
This is a test prompt.
"""

valid_prompt_content_subst = """
---
provider: openai
model: gpt-4o
input: input.txt
output: output.txt
tests:
  test_01: Test description 1
  test_02: Test description 2
---
This is a $test prompt.
"""


# Define fixtures to use in your tests
@pytest.fixture
def valid_prompt_file(tmp_path):
    d = tmp_path / "sub"
    d.mkdir()
    p = d / "prompt.txt"
    p.write_text(valid_prompt_content)
    return p


@pytest.fixture
def valid_prompt_file_subst(tmp_path):
    d = tmp_path / "sub"
    d.mkdir()
    p = d / "prompt.txt"
    p.write_text(valid_prompt_content_subst)
    return p


def test_prompt_file_init_with_valid_file(valid_prompt_file):
    prompt_file = PromptFile(filename=str(valid_prompt_file))
    assert prompt_file.filename == str(valid_prompt_file)
    assert prompt_file.original_prompt == "This is a test prompt."
    assert prompt_file.prompt == "This is a test prompt."
    assert prompt_file.metadata == {
        "provider": "openai",
        "model": "gpt-4o",
        "input": "input.txt",
        "output": "output.txt",
        "tests": {
            "test_01": "Test description 1",
            "test_02": "Test description 2",
        },
    }
    assert prompt_file.tests == {
        "test_01": "Test description 1",
        "test_02": "Test description 2",
    }


def test_prompt_file_init_with_non_existent_file():
    with pytest.raises(FileNotFoundError):
        PromptFile(filename="non_existent_file.txt")


def test_to_dict(valid_prompt_file):
    prompt_file = PromptFile(filename=str(valid_prompt_file))
    data_dict = prompt_file.to_dict()
    assert data_dict == {
        "filename": str(valid_prompt_file),
        "original_prompt": "This is a test prompt.",
        "prompt": "This is a test prompt.",
        "metadata": {
            "provider": "openai",
            "model": "gpt-4o",
            "input": "input.txt",
            "output": "output.txt",
            "tests": {
                "test_01": "Test description 1",
                "test_02": "Test description 2",
            },
        },
        "tests": {
            "test_01": "Test description 1",
            "test_02": "Test description 2",
        },
    }


def test_from_dict(valid_prompt_file):
    data = {
        "filename": str(valid_prompt_file),
        "original_prompt": "This is a test prompt.",
        "prompt": "This is a test prompt.",
        "metadata": {
            "provider": "openai",
            "model": "gpt-4o",
            "input": "input.txt",
            "output": "output.txt",
            "tests": {
                "test_01": "Test description 1",
                "test_02": "Test description 2",
            },
        },
        "tests": {
            "test_01": "Test description 1",
            "test_02": "Test description 2",
        },
    }
    prompt_file = PromptFile.from_dict(data)
    assert prompt_file.filename == str(valid_prompt_file)
    assert prompt_file.original_prompt == "This is a test prompt."
    assert prompt_file.prompt == "This is a test prompt."
    assert prompt_file.metadata == {
        "provider": "openai",
        "model": "gpt-4o",
        "input": "input.txt",
        "output": "output.txt",
        "tests": {
            "test_01": "Test description 1",
            "test_02": "Test description 2",
        },
    }
    assert prompt_file.tests == {
        "test_01": "Test description 1",
        "test_02": "Test description 2",
    }


def test_substitute_prompt_match(valid_prompt_file_subst):
    prompt_file = PromptFile(filename=str(valid_prompt_file_subst))
    substituted_prompt = prompt_file.substitute_prompt(test="real")
    assert substituted_prompt == "This is a real prompt."


def test_substitute_prompt_no_match(valid_prompt_file):
    prompt_file = PromptFile(filename=str(valid_prompt_file))
    substituted_prompt = prompt_file.substitute_prompt(name="John")
    assert substituted_prompt == "This is a test prompt."


if __name__ == "__main__":
    pytest.main([__file__, "-vv"])

# Additional test cases for the PromptFile class
