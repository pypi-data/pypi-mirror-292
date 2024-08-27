import pytest
from promptarchitect.openai_completion import OpenAICompletion


@pytest.mark.llm
def test_completion():
    completion = OpenAICompletion("You're a friendly assistant.")
    prompt = "What is the capital of France?"

    response = completion.completion(prompt)

    assert response is not None


@pytest.mark.llm
def test_assign_parameters():
    parameters = {"temperature": 0.7}
    completion = OpenAICompletion("You're a friendly assistant.", parameters=parameters)

    assert completion.parameters == parameters


@pytest.mark.llm
def test_cost_and_latency():
    completion = OpenAICompletion("You're a friendly assistant.")
    prompt = "What is the capital of France?"

    completion.completion(prompt)

    assert completion.cost is not None
    assert completion.duration is not None


@pytest.mark.llm
def test_model_unknown_alias():
    with pytest.raises(ValueError):
        OpenAICompletion("You're a friendly assistant.", model="gpt-1.0")
