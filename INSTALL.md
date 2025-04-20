# Elysia Installation Guide

This document explains how to install and set up the Elysia AI assistant system.

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Internet connection (for downloading dependencies)

## Installation

### Using the unified setup script

The easiest way to install Elysia is using the unified setup script:

```bash
python setup.py install
```

This will:
1. Check for required dependencies
2. Clean up any existing build artifacts
3. Set up the package structure
4. Install all required dependencies
5. Download NLP components (NLTK data, spaCy models)
6. Configure the environment

### Installation options

- **Clean only**: To clean up build artifacts without installing:
  ```bash
  python setup.py clean
  ```

- **Development mode**: For development with live code changes:
  ```bash
  pip install -e .
  ```

## Project Structure

After installation, the project will have the following structure:

```
elysia/
├── api_layer/               # API integrations for LLM services
│   └── gemini_api_call.py   # Google Gemini API implementation
├── memory_management/       # User data and context management
├── personality_layer/       # Personality and response generation
├── tests/                   # Test modules
├── chatbot.py               # Main entry point
├── config.py                # Centralized configuration
└── setup.py                 # Installation script
```

## Running Elysia

After installation, you can run Elysia with:

```bash
python chatbot.py
```

## Running Tests

To run tests for the API layer:

```bash
python -m tests.test_gemini
```

## Adding API Keys

Before using external API services, you need to add your API keys to the configuration.
Either edit `config.py` directly, or create a `local_config.py` file:

```python
# local_config.py - Will override settings in config.py
GEMINI_API_KEY = "your-actual-api-key-here"
```

## Troubleshooting

If you encounter issues during installation:

1. **Missing dependencies**: Run `pip install -r requirements.txt`
2. **Import errors**: Make sure you're running from the project root directory
3. **NLP data errors**: You can manually download data:
   ```bash
   python -m nltk.downloader punkt stopwords wordnet
   python -m spacy download en_core_web_sm
   ``` 