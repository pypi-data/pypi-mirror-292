from promptarchitect.claude_completion import ClaudeCompletion
from promptarchitect.completions.core import Completion
from promptarchitect.ollama_completion import OllamaCompletion
from promptarchitect.openai_completion import OpenAICompletion


def create_completion(
    provider: str, model: str, parameters: dict, system_role: str
) -> Completion:
    if provider == "ollama":
        return OllamaCompletion(system_role, model, parameters)
    elif provider == "openai":
        return OpenAICompletion(system_role, model, parameters)
    elif provider == "anthropic":
        return ClaudeCompletion(system_role, model, parameters)
    else:
        raise ValueError(f"Provider {provider} is not supported.")
