from promptarchitect.claude_completion import ClaudeCompletion


def test_completion():
    completion = ClaudeCompletion("You're a friendly assistant.")
    prompt = "What is the capital of France?"

    response = completion.completion(prompt)

    assert response is not None


def test_assign_parameters():
    parameters = {"temperature": 0.7}
    completion = ClaudeCompletion("You're a friendly assistant.", parameters=parameters)

    assert completion.parameters == parameters
    assert completion.model == "claude-3-5-sonnet-20240620"


def test_cost_and_latency():
    completion = ClaudeCompletion("You're a friendly assistant.")
    prompt = "What is the capital of France?"

    completion.completion(prompt)

    assert completion.cost is not None
    assert completion.latency is not None
