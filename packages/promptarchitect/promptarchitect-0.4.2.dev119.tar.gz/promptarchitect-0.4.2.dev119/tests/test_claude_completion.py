import pytest
from promptarchitect.claude_completion import ClaudeCompletion

@pytest.mark.llm
def test_completion():
    completion = ClaudeCompletion("You're a friendly assistant.")
    prompt = "What is the capital of France?"

    response = completion.completion(prompt)

    assert response is not None

@pytest.mark.llm
def test_assign_parameters():
    parameters = {"temperature": 0.7}
    completion = ClaudeCompletion("You're a friendly assistant.", parameters=parameters)

    assert completion.parameters == parameters
    assert completion.model == "claude-3-5-sonnet-20240620"

@pytest.mark.llm
def test_cost_and_latency():
    completion = ClaudeCompletion("You're a friendly assistant.")
    prompt = "What is the capital of France?"

    completion.completion(prompt)

    assert completion.cost is not None
    assert completion.duration is not None

@pytest.mark.llm
def test_model_alias():
    completion = ClaudeCompletion(
        "You're a friendly assistant.", model="claude-3-5-sonnet"
    )
    assert completion.model == "claude-3-5-sonnet-20240620"

@pytest.mark.llm
def test_model_unknown_alias():
    with pytest.raises(ValueError):
        ClaudeCompletion("You're a friendly assistant.", model="claude-1.0")
