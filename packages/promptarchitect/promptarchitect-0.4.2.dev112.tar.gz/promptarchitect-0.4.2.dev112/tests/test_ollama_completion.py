from promptarchitect.ollama_completion import OllamaCompletion


def test_completion():
    parameters = {"temperature": 0.7}
    completion = OllamaCompletion(
        "You're a friendly assistant.", model="gemma2", parameters=parameters
    )

    prompt = "What is the capital of France?"

    response = completion.completion(prompt)

    assert response is not None
    assert completion.parameters == parameters
    assert completion.cost is not None
    assert completion.latency is not None
