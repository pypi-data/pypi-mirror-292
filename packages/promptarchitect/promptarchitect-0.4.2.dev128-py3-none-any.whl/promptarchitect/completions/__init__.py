from promptarchitect.claude_completion import ClaudeCompletion
from promptarchitect.completions.core import Completion
from promptarchitect.ollama_completion import OllamaCompletion
from promptarchitect.openai_completion import OpenAICompletion
from promptarchitect.specification import EngineeredPromptMetadata


def create_completion(
    provider: str, model: str, metadata: EngineeredPromptMetadata, system_role: str
) -> Completion:
    parameters = _get_model_parameters(metadata)

    if provider == "ollama":
        return OllamaCompletion(system_role, model, parameters)
    elif provider == "openai":
        return OpenAICompletion(system_role, model, parameters)
    elif provider == "anthropic":
        return ClaudeCompletion(system_role, model, parameters)
    else:
        raise ValueError(f"Provider {provider} is not supported.")


def _get_model_parameters(metadata: EngineeredPromptMetadata) -> dict:
    return {
        "temperature": metadata.temperature,
        "max_tokens": metadata.max_tokens,
        "frequency_penalty": metadata.frequency_penalty,
        "presence_penalty": metadata.presence_penalty,
    }
