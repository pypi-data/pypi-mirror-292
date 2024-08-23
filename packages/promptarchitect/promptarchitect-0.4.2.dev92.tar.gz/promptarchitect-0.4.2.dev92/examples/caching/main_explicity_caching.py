from pathlib import Path

from promptarchitect import EngineeredPrompt

# Create the output directory if it does not exist
output_directory = Path("output_directory")
output_directory.mkdir(exist_ok=True)

# Define the path to the prompt and input file
prompt_path = Path("prompts/generate_titles_claude.prompt")

# Initialize the EngineeredPrompt
prompt = EngineeredPrompt(
    prompt_file_path=str(prompt_path), output_path="output_directory"
)

# Explicitly store the prompt to the cache
prompt.store_to_cache()

# Execute the prompt
response = prompt.execute()

# Show the response from the model
print(response)


# Now we will load the prompt from the cache, to see how it works
# Load the prompt from the cache
# Initialize a new EngineeredPrompt instance
prompt2 = EngineeredPrompt(
    prompt_file_path=str(prompt_path), output_path="output_directory"
)

# The prompt will be loaded from the cache
# Check the logger info message to see if the prompt was loaded from the cache
# The response will be the same as the previous execution
prompt2.load_from_cache()
response2 = prompt.execute()
print(response2)
