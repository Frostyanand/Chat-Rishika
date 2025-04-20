# Elysia API Layer

The API Layer provides interfaces to various Large Language Model (LLM) APIs. 
Each file in this directory represents a standalone script for a specific API provider.

## Current Implementations

- `gemini_api_call.py` - Google's Gemini Pro API integration

## Usage

Each API implementation provides a single, simple function to call the respective model:

```python
from api_layer.gemini_api_call import gemini_api_call

# Basic usage
response = gemini_api_call("Your prompt here")

# Advanced usage with parameters
response = gemini_api_call(
    prompt="Your prompt here",
    temperature=0.7,
    top_p=0.95,
    max_tokens=1000
)
```

## API Structure

Each API implementation follows a consistent pattern:

1. **Single Entry Point**: One main function per file (e.g., `gemini_api_call`)
2. **Consistent Parameters**: Common parameters across implementations
   - `prompt`: The text prompt to send to the model
   - `temperature`: Controls randomness (0.0-1.0)
   - `top_p`: Controls diversity via nucleus sampling
   - `max_tokens`: Maximum output length
3. **Error Handling**: Proper error handling for API timeouts, failures, etc.
4. **Logging**: Basic logging for debugging purposes

## Configuration

All API keys and settings are stored in the centralized `config.py` file in the project root.
API implementations must import their configuration from there:

```python
from config import GEMINI_API_KEY, GEMINI_API_BASE, DEFAULT_TIMEOUT
```

## Adding New API Implementations

To add a new API implementation:

1. Create a new file named `[provider]_api_call.py`
2. Follow the existing pattern with a single main function
3. Add keys and settings to the project's `config.py`
4. Update this README to include the new implementation

## Testing

Each API implementation has a corresponding test file in the `tests/` directory.
To run tests, use:

```bash
python -m tests.test_gemini
``` 