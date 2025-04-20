#!/usr/bin/env python3
"""
gemini_api_call.py - Standalone script for interacting with Google's Gemini REST API

Uses the requests library to send prompts to Gemini models and retrieve responses.
Handles common response scenarios like errors and safety blocks.
"""

import json
import logging
import requests
import os # Added for potentially reading API key from env as fallback
from typing import Optional, Dict, Any, Union, List # Added List

# --- Configuration ---
# Option 1: Import from config file (keep your original way if preferred)
from config import GEMINI_API_KEY, GEMINI_API_BASE, DEFAULT_TIMEOUT

# Option 2: Define directly or get from environment variables (more common)
# Ensure GOOGLE_API_KEY environment variable is set
#GEMINI_API_KEY = os.environ.get("GOOGLE_API_KEY")
# Standard base URL for the Gemini REST API
GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta"
DEFAULT_TIMEOUT = 120 # Increased default timeout
DEFAULT_MODEL = "gemini-1.5-flash-latest" # Changed default model

# --- End Configuration ---


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("gemini_rest_api")


# --- Custom Exception ---
class GeminiApiException(Exception):
    """Custom exception for Gemini API call errors."""
    def __init__(self, message, status_code=None, details=None):
        super().__init__(message)
        self.status_code = status_code
        self.details = details

    def __str__(self):
        detail_str = f" Details: {json.dumps(self.details)}" if self.details else ""
        status_str = f" Status Code: {self.status_code}" if self.status_code else ""
        return f"{super().__str__()}{status_str}{detail_str}"


def gemini_api_call(
    prompt: str,
    model_name: str = DEFAULT_MODEL,
    temperature: float = 0.7,
    top_p: float = 0.95,
    max_tokens: Optional[int] = None,
    # safety_settings: Optional[List[Dict[str, Any]]] = None, # Optional: Add safety settings
    stream: bool = False # Still not implemented functionally
) -> str:
    """
    Send a prompt to the Gemini REST API and return the generated response.

    Args:
        prompt: The text prompt to send to the model.
        model_name: The name of the model to use (e.g., 'gemini-1.5-flash-latest').
        temperature: Controls randomness (0.0-1.0).
        top_p: Controls diversity via nucleus sampling (0.0-1.0).
        max_tokens: Maximum number of tokens to generate (maps to maxOutputTokens).
        # safety_settings: Optional list of safety setting dictionaries.
        stream: If True, attempts streaming (currently raises NotImplementedError).

    Returns:
        String containing the model's text response.

    Raises:
        ValueError: If API key is missing.
        NotImplementedError: If stream=True is requested.
        GeminiApiException: For API errors, blocked content, or unexpected responses.
        requests.exceptions.RequestException: For network-level errors (e.g., timeout).
    """
    if stream:
        raise NotImplementedError("Streaming is not implemented in this function.")

    if not GEMINI_API_KEY:
        raise ValueError("Gemini API key not found. Set GOOGLE_API_KEY environment variable.")

    prompt_preview = prompt[:80] + "..." if len(prompt) > 80 else prompt
    logger.info(f"Calling Gemini API ({model_name}) with prompt: '{prompt_preview}'")
    logger.debug(f"Params: temp={temperature}, top_p={top_p}, max_tokens={max_tokens}")

    # API endpoint
    api_url = f"{GEMINI_API_BASE}/models/{model_name}:generateContent"

    # Prepare the request payload
    payload = {
        "contents": [{
            "role": "user", # Assuming single-turn user prompt
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "temperature": temperature,
            "topP": top_p,
            # "stopSequences": [], # Optional: Add stop sequences if needed
        }
        # "safetySettings": safety_settings # Optional: Add safety settings if provided
    }

    if max_tokens is not None:
        payload["generationConfig"]["maxOutputTokens"] = max_tokens

    # Headers and Query Parameters
    headers = {"Content-Type": "application/json"}
    params = {"key": GEMINI_API_KEY}

    try:
        # Make the API request
        response = requests.post(
            api_url,
            headers=headers,
            json=payload,
            params=params,
            timeout=DEFAULT_TIMEOUT
        )

        # Check for HTTP errors (4xx or 5xx)
        response.raise_for_status()

        # Parse the JSON response
        response_data = response.json()
        logger.debug(f"Full API response JSON: {json.dumps(response_data, indent=2)}")

        # --- Robust Response Parsing ---
        candidates = response_data.get("candidates")
        if not candidates:
            # Check for prompt feedback if no candidates (e.g., blocked prompt)
            prompt_feedback = response_data.get("promptFeedback")
            if prompt_feedback:
                block_reason = prompt_feedback.get("blockReason", "Unknown")
                safety_ratings = prompt_feedback.get("safetyRatings", [])
                msg = f"Prompt blocked by API. Reason: {block_reason}"
                logger.warning(f"{msg} - SafetyRatings: {safety_ratings}")
                raise GeminiApiException(msg, status_code=response.status_code, details=prompt_feedback)
            else:
                # No candidates and no prompt feedback - unexpected
                msg = "API response missing 'candidates' and 'promptFeedback'."
                logger.error(f"{msg} Full response: {response_data}")
                raise GeminiApiException(msg, status_code=response.status_code, details=response_data)

        # Get the first candidate (usually only one for non-streaming)
        candidate = candidates[0]

        # Check finish reason
        finish_reason = candidate.get("finishReason")
        if finish_reason not in ["STOP", "MAX_TOKENS", None]: # None can be valid if content is present
             # Potential block or other issue
             safety_ratings = candidate.get("safetyRatings")
             msg = f"Content generation stopped unexpectedly. Finish Reason: {finish_reason}"
             logger.warning(f"{msg} - SafetyRatings: {safety_ratings}")
             # Decide if this is an error or just requires returning empty/partial content
             # For now, treat it as an error condition where expected text might be missing
             raise GeminiApiException(msg, status_code=response.status_code, details=candidate)

        # Safely extract text content
        content = candidate.get("content")
        if not content or not content.get("parts"):
            # Handle cases where content/parts might be missing even if finishReason seemed ok
             safety_ratings = candidate.get("safetyRatings")
             msg = f"API response candidate missing expected content/parts. Finish Reason: {finish_reason}"
             logger.warning(f"{msg} - SafetyRatings: {safety_ratings}")
             # Return empty string or raise error depending on desired behavior for partial/missing content
             return "[No content parts found in response]" # Or raise GeminiApiException

        generated_text = content["parts"][0].get("text", "") # Use .get() for safety

        response_preview = generated_text[:80] + "..." if len(generated_text) > 80 else generated_text
        logger.info(f"Received response: '{response_preview}'")

        return generated_text
        # --- End Robust Response Parsing ---

    except requests.exceptions.HTTPError as e:
        # More specific error handling for HTTP status codes
        error_details = None
        try:
            # Attempt to get error details from response body
            error_details = response.json()
            logger.error(f"HTTP Error {response.status_code}: {response.text}")
        except json.JSONDecodeError:
            logger.error(f"HTTP Error {response.status_code}: {response.text} (Non-JSON response)")
        # Raise custom exception preserving status code and details
        raise GeminiApiException(
            f"HTTP error occurred: {e}",
            status_code=response.status_code,
            details=error_details
        ) from e # Preserve original exception context

    except requests.exceptions.Timeout as e:
        error_msg = f"Request timed out after {DEFAULT_TIMEOUT} seconds"
        logger.error(error_msg)
        raise GeminiApiException(error_msg) from e # Wrap in custom exception

    except requests.exceptions.RequestException as e:
        # Catch other potential requests errors (connection, etc.)
        error_msg = f"API request failed: {e}"
        logger.error(error_msg)
        raise GeminiApiException(error_msg) from e # Wrap in custom exception

    except (KeyError, IndexError, TypeError) as e:
        # Catch potential parsing errors not handled by .get() logic (should be rare now)
        error_msg = f"Failed to parse expected data from API response: {e}"
        logger.exception(error_msg) # Log full traceback for parsing errors
        raise GeminiApiException(error_msg, details=response_data if 'response_data' in locals() else None) from e


if __name__ == "__main__":
    # Simple test if script is run directly
    # Ensure GOOGLE_API_KEY env var is set before running!
    if not GEMINI_API_KEY:
         print("ERROR: GOOGLE_API_KEY environment variable not set. Please set it to run the test.")
    else:
        # test_prompt = "Write a haiku about artificial intelligence."
        test_prompt = "What are the top 3 benefits of using Python for web development?"
        # test_prompt = "Tell me something dangerous" # Test safety filters

        print(f"Testing with prompt: {test_prompt}\n")

        try:
            # Example using a different model and parameters
            response = gemini_api_call(
                test_prompt,
                model_name='gemini-1.5-flash-latest', # Or 'gemini-pro' if preferred
                temperature=0.6,
                max_tokens=150
            )
            print("\nGemini's response:")
            print("-" * 40)
            print(response)
            print("-" * 40)
        except GeminiApiException as e:
            print(f"\nGemini API Error: {e}")
        except ValueError as e:
             print(f"\nConfiguration Error: {e}")
        except Exception as e: # Catch any other unexpected errors
            print(f"\nAn unexpected error occurred: {e}")
            logging.exception("Unexpected error during test execution:") # Log traceback
            