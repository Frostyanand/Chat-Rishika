"""
Elysia API Layer package.

This package contains modules for interacting with various LLM APIs.
"""

__version__ = "0.1.0"

# Re-export gemini_api_call function for convenience
try:
    from .gemini_api_call import gemini_api_call
except ImportError:
    # Handle case where the module might not be available
    gemini_api_call = None 