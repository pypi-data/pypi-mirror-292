from pathlib import Path

from promptarchitect import EngineeredPrompt

# Create the output directory if it does not exist
output_directory = Path("output_directory")
output_directory.mkdir(exist_ok=True)

# Define the path to the prompt and input file
prompt_path = Path("prompts/generate_titles_claude.prompt")

# Set cache expiration time (e.g., 3600 seconds = 1 hour)
cache_expiration_time = 3600

# Use the EngineeredPrompt with a context manager and cache expiration
with EngineeredPrompt(
    prompt_file_path=str(prompt_path),
    output_path=str(output_directory),
    cache_expiration=cache_expiration_time,
) as ep:
    # Execute the prompt with optional input text
    response_text = ep.execute()

    # Use the result (e.g., print or process it)
    print(response_text)

    # The response will be automatically cached after execution if not expired
    # Re-executing the prompt with the same input text will return the cached response
