from promptarchitect.ollama_completion import OllamaCompletion


def test_completion():
    completion = OllamaCompletion("You're a friendly assistant.")
    prompt = "What is the capital of France?"

    response = completion.completion(prompt)

    assert response is not None


def test_assign_parameters():
    parameters = {"temperature": 0.7}
    completion = OllamaCompletion("You're a friendly assistant.", parameters=parameters)

    assert completion.parameters == parameters


def test_cost_and_latency():
    completion = OllamaCompletion("You're a friendly assistant.")
    prompt = "What is the capital of France?"

    completion.completion(prompt)

    assert completion.cost is not None
    assert completion.latency is not None
