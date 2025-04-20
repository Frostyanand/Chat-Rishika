#!/usr/bin/env python3
"""
config.py - Centralized configuration for the Elysia AI assistant system

This file contains all configuration settings for the Elysia system,
including API keys, model parameters, and system settings.
"""

#################################################
# API Keys and Endpoints                        #
#################################################

# Gemini API Configuration
GEMINI_API_KEY = "your-gemini-api-key"  # Replace with your actual API key
GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta"

# OpenAI API Configuration (placeholder for future implementation)
OPENAI_API_KEY = ""
OPENAI_API_BASE = "https://api.openai.com/v1"

# Anthropic API Configuration (placeholder for future implementation)
ANTHROPIC_API_KEY = ""
ANTHROPIC_API_BASE = "https://api.anthropic.com/v1"

# Groq API Configuration (placeholder for future implementation)
GROQ_API_KEY = ""
GROQ_API_BASE = "https://api.groq.com/v1"

#################################################
# Global Settings                               #
#################################################

# Network request settings
DEFAULT_TIMEOUT = 10  # Timeout for API requests in seconds
MAX_RETRIES = 3       # Maximum number of retries for failed requests

# Models and parameters
DEFAULT_MODEL = "gemini-pro"  # Default model to use
DEFAULT_TEMPERATURE = 0.7     # Default temperature for generation
DEFAULT_TOP_P = 0.95          # Default top_p for generation
DEFAULT_MAX_TOKENS = 1000     # Default maximum tokens to generate

#################################################
# Elysia Personal Assistant Configuration       #
#################################################

# Personality settings
ASSISTANT_NAME = "Elysia"
ASSISTANT_PERSONA = "caring, warm, and emotionally intelligent"

# Memory settings
MAX_CONVERSATION_HISTORY = 50  # Maximum number of messages to retain in memory

# Logging settings
LOG_LEVEL = "INFO"  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_TO_FILE = True
LOG_FILE_PATH = "logs/elysia.log"

# Try to load local config overrides if they exist
try:
    from local_config import *
    print("Loaded local configuration overrides.")
except ImportError:
    pass  # No local overrides found, using defaults
