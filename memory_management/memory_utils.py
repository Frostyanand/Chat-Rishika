"""
Utility functions for the memory management system.

This module provides helper functions for working with memory stores,
including streak calculation, date handling, and entity extraction.
"""
import os
import json
from datetime import datetime, timedelta
import re
import logging
import html
import unicodedata
import uuid
from typing import Dict, List, Tuple, Optional, Any, Union


logger = logging.getLogger(__name__)


def calculate_streak_status(last_interaction: Optional[str], timezone: Optional[str] = None) -> Dict[str, Any]:
    """
    Calculate the current streak status based on the last interaction.
    
    Args:
        last_interaction: ISO formatted date of last interaction
        timezone: Optional timezone for the user
        
    Returns:
        Dict with streak status information
    """
    if not last_interaction:
        return {"active": False, "days_ago": None}
    
    try:
        # Parse the last interaction date
        last_date = datetime.fromisoformat(last_interaction.replace('Z', '+00:00'))
        
        # Get current date
        now = datetime.utcnow()
        
        # Calculate days difference
        delta = now - last_date
        days_ago = delta.days
        
        # Determine if streak is still active (within 36 hours)
        active = delta.total_seconds() < (36 * 60 * 60)  # 36 hours in seconds
        
        return {
            "active": active,
            "days_ago": days_ago
        }
    except ValueError as e:
        logger.error(f"Error calculating streak status: {str(e)}")
        return {"active": False, "days_ago": None}


def calculate_streak(last_interaction: Optional[str], 
                     current_streak: int = 0, 
                     longest_streak: int = 0) -> Tuple[int, int]:
    """
    Calculate user streak based on last interaction date.
    
    This function determines if a user's streak should be continued, reset, or incremented
    based on when they last interacted with the system.
    
    Args:
        last_interaction: ISO formatted date string of last interaction
        current_streak: The user's current streak count
        longest_streak: The user's longest recorded streak
        
    Returns:
        Tuple of (new_current_streak, new_longest_streak)
    """
    now = datetime.utcnow()
    
    # If this is the first interaction, start streak at 1
    if not last_interaction:
        return 1, max(1, longest_streak)
    
    try:
        # Parse the last interaction date
        last_date = datetime.fromisoformat(last_interaction.replace('Z', '+00:00'))
        
        # Convert to date (without time) in UTC
        last_day = last_date.date()
        today = now.date()
        
        # Calculate the difference in days
        delta_days = (today - last_day).days
        
        # Determine the new streak value
        if delta_days == 0:
            # Same day interaction, maintain streak
            new_streak = current_streak
        elif delta_days == 1:
            # Next day interaction, increment streak
            new_streak = current_streak + 1
        else:
            # More than one day passed, reset streak
            new_streak = 1
        
        # Update longest streak if needed
        new_longest = max(longest_streak, new_streak)
        
        return new_streak, new_longest
    
    except (ValueError, TypeError) as e:
        logger.error(f"Error calculating streak: {str(e)}")
        # Return safe default values
        return 1, max(1, longest_streak)


def sanitize_input(text: str, max_length: int = 10000) -> str:
    """
    Sanitize user input to prevent security issues.
    
    Args:
        text: The text to sanitize
        max_length: Maximum allowed length
        
    Returns:
        Sanitized text
    """
    if not isinstance(text, str):
        if text is None:
            return ""
        try:
            text = str(text)
        except Exception:
            return ""
    
    # Limit length
    if max_length > 0 and len(text) > max_length:
        text = text[:max_length]
    
    # Remove control characters
    text = ''.join(ch for ch in text if unicodedata.category(ch)[0] != 'C' or ch in ('\n', '\t', '\r'))
    
    # HTML escape to prevent XSS
    text = html.escape(text)
    
    return text


def sanitize_html(html_content: str, allowed_tags: List[str] = None) -> str:
    """
    Sanitize HTML content, keeping only allowed tags.
    
    Args:
        html_content: HTML content to sanitize
        allowed_tags: List of allowed HTML tags
        
    Returns:
        Sanitized HTML
    """
    if allowed_tags is None:
        # Default to strict whitelist
        allowed_tags = ['b', 'i', 'u', 'p', 'br', 'ul', 'ol', 'li']
    
    # First, escape everything
    escaped = html.escape(html_content)
    
    # Then, selectively unescape allowed tags
    for tag in allowed_tags:
        # Convert <tag> and </tag>
        escaped = escaped.replace(f"&lt;{tag}&gt;", f"<{tag}>")
        escaped = escaped.replace(f"&lt;/{tag}&gt;", f"</{tag}>")
    
    return escaped


def generate_secure_id() -> str:
    """
    Generate a secure unique identifier.
    
    Returns:
        Secure unique ID
    """
    return str(uuid.uuid4())


def is_valid_email(email: str) -> bool:
    """
    Check if an email address is valid.
    
    Args:
        email: Email address to check
        
    Returns:
        True if valid, False otherwise
    """
    # Simple regex for basic email validation
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def is_valid_username(username: str) -> bool:
    """
    Check if username is valid.
    
    Args:
        username: Username to check
        
    Returns:
        True if valid, False otherwise
    """
    # Only allow letters, numbers, underscores, periods, and hyphens
    # Length between 3 and 30 characters
    pattern = r'^[a-zA-Z0-9._-]{3,30}$'
    return bool(re.match(pattern, username))


def anonymize_sensitive_data(text: str) -> str:
    """
    Anonymize potentially sensitive data in text.
    
    Args:
        text: Text to anonymize
        
    Returns:
        Anonymized text
    """
    # Remove email addresses
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', text)
    
    # Remove phone numbers (various formats)
    text = re.sub(r'\b(\+\d{1,2}\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b', '[PHONE]', text)
    
    # Remove credit card numbers
    text = re.sub(r'\b(?:\d{4}[- ]?){3}\d{4}\b', '[CREDIT_CARD]', text)
    
    # Remove SSNs (US Social Security Numbers)
    text = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[SSN]', text)
    
    # Remove IP addresses
    text = re.sub(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', '[IP_ADDRESS]', text)
    
    return text


def extract_entities(text: str) -> List[Dict[str, Any]]:
    """
    Extract potential entities from text.
    
    This is a simple pattern-based entity extraction function that looks for
    common patterns like names, dates, locations, etc.
    
    Args:
        text: The text to extract entities from
        
    Returns:
        List of dictionaries with entity information
    """
    # Sanitize input first
    text = sanitize_input(text)
    
    entities = []
    
    # Simple patterns for demonstration purposes
    # In a real system, you would use NLP libraries like spaCy
    
    # Extract potential names (capitalized words not at start of sentence)
    name_pattern = r'(?<!^)(?<!\. )[A-Z][a-z]+'
    for match in re.finditer(name_pattern, text):
        name = match.group(0)
        entities.append({
            "type": "name",
            "value": name,
            "confidence": 0.7  # Arbitrary confidence score
        })
    
    # Extract dates (simple pattern)
    date_pattern = r'\b\d{1,2}[-/\.]\d{1,2}[-/\.]\d{2,4}\b'
    for match in re.finditer(date_pattern, text):
        date = match.group(0)
        entities.append({
            "type": "date",
            "value": date,
            "confidence": 0.8
        })
    
    # Extract emails (but anonymize them)
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    for match in re.finditer(email_pattern, text):
        # Don't store actual email, just note that one was detected
        entities.append({
            "type": "email",
            "value": "[EMAIL DETECTED]",
            "confidence": 0.9
        })
    
    # Extract locations (simple city/country names)
    locations = [
        "New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia",
        "San Antonio", "San Diego", "Dallas", "San Jose", "Austin", "London", "Paris",
        "Tokyo", "Berlin", "Rome", "Madrid", "Toronto", "Sydney", "Singapore"
    ]
    
    for location in locations:
        if location in text:
            entities.append({
                "type": "location",
                "value": location,
                "confidence": 0.8
            })
    
    return entities


def get_conversation_summary(messages, max_length=500):
    """
    Generate a simple summary of a conversation.
    
    Args:
        messages (list): List of message dictionaries
        max_length (int): Maximum length of summary
        
    Returns:
        str: Conversation summary
    """
    if not messages:
        return "No conversation to summarize."
    
    # Calculate basic statistics
    user_messages = [m for m in messages if m.get("is_user", False)]
    elysia_messages = [m for m in messages if not m.get("is_user", False)]
    
    total_messages = len(messages)
    total_user_messages = len(user_messages)
    total_elysia_messages = len(elysia_messages)
    
    # Get time span
    if messages and "timestamp" in messages[0] and "timestamp" in messages[-1]:
        start_time = datetime.fromisoformat(messages[0]["timestamp"].replace('Z', '+00:00') if messages[0]["timestamp"].endswith('Z') else messages[0]["timestamp"])
        end_time = datetime.fromisoformat(messages[-1]["timestamp"].replace('Z', '+00:00') if messages[-1]["timestamp"].endswith('Z') else messages[-1]["timestamp"])
        duration = end_time - start_time
        duration_minutes = duration.total_seconds() / 60
    else:
        duration_minutes = 0
    
    # Calculate word counts
    user_word_count = sum(len(m.get("content", "").split()) for m in user_messages)
    elysia_word_count = sum(len(m.get("content", "").split()) for m in elysia_messages)
    
    # Generate summary
    summary = f"Conversation with {total_messages} messages ({total_user_messages} from user, {total_elysia_messages} from Elysia). "
    
    if duration_minutes > 0:
        if duration_minutes < 60:
            summary += f"Duration: {duration_minutes:.1f} minutes. "
        else:
            summary += f"Duration: {duration_minutes/60:.1f} hours. "
            
    summary += f"User wrote {user_word_count} words, Elysia wrote {elysia_word_count} words. "
    
    # Extract topic hints from first and last user messages
    if user_messages:
        first_msg = user_messages[0].get("content", "")[:50]
        last_msg = user_messages[-1].get("content", "")[:50]
        
        summary += f"Started with: \"{first_msg}{'...' if len(first_msg) == 50 else ''}\". "
        if len(user_messages) > 1:
            summary += f"Ended with: \"{last_msg}{'...' if len(last_msg) == 50 else ''}\". "
    
    # Truncate if needed
    if len(summary) > max_length:
        summary = summary[:max_length-3] + "..."
        
    return summary


def merge_user_profiles(profile1, profile2, conflict_strategy="newer"):
    """
    Merge two user profiles, resolving conflicts according to the strategy.
    
    Args:
        profile1 (dict): First profile
        profile2 (dict): Second profile
        conflict_strategy (str): How to resolve conflicts - "newer", "p1", "p2"
        
    Returns:
        dict: Merged profile
    """
    if not profile1:
        return profile2.copy() if profile2 else {}
    if not profile2:
        return profile1.copy()
    
    # Start with a copy of profile1
    merged = profile1.copy()
    
    # Process each key in profile2
    for key, value in profile2.items():
        # Skip metadata or timestamps for special handling
        if key in ["last_updated"]:
            continue
            
        # If key doesn't exist in profile1, just add it
        if key not in merged:
            merged[key] = value
        else:
            # Handle different conflict resolution strategies
            if conflict_strategy == "p2":
                merged[key] = value
            elif conflict_strategy == "newer":
                # Check timestamps if available
                p1_timestamp = profile1.get("last_updated", "1970-01-01T00:00:00")
                p2_timestamp = profile2.get("last_updated", "1970-01-01T00:00:00")
                
                if p2_timestamp > p1_timestamp:
                    merged[key] = value
            # For "p1" strategy, keep the existing value (already done by copying)
            
    # Use the newer timestamp if available
    p1_timestamp = profile1.get("last_updated", "1970-01-01T00:00:00")
    p2_timestamp = profile2.get("last_updated", "1970-01-01T00:00:00")
    merged["last_updated"] = max(p1_timestamp, p2_timestamp)
    
    return merged 


def get_relevant_context_from_api(user_id, query, recent_messages=None, api_key=None, model_name=None):
    """
    Use an external API to get relevant context based on recent messages and query.
    This is a placeholder for future implementation using an LLM API.
    
    Args:
        user_id (str): User ID to retrieve context for
        query (str): The current query or message
        recent_messages (list): List of recent conversation messages
        api_key (str): API key for the LLM service
        model_name (str): Model to use for context retrieval
        
    Returns:
        dict: Context information extracted from the conversation
    """
    # This is a placeholder that would be implemented with an actual API call
    # to a service like OpenAI, Anthropic, etc.
    
    if not api_key:
        print("Warning: No API key provided for context retrieval")
        return {
            "relevant_facts": [],
            "related_topics": [],
            "conversation_summary": "No API key provided to generate summary"
        }
    
    if not recent_messages:
        return {
            "relevant_facts": [],
            "related_topics": [],
            "conversation_summary": "No recent messages to analyze"
        }
    
    # In a real implementation, this would make an API call to an LLM
    # For now, return a placeholder result
    print(f"Would make API call to get context for user {user_id} with query: {query[:50]}...")
    
    return {
        "relevant_facts": [],
        "related_topics": [],
        "conversation_summary": "API integration not yet implemented"
    }


def generate_memory_from_conversation(messages, api_key=None, model_name=None):
    """
    Generate a new permanent memory from a conversation.
    This is a placeholder for future implementation using an LLM API.
    
    Args:
        messages (list): List of recent messages
        api_key (str): API key for the LLM service
        model_name (str): Model to use for memory generation
        
    Returns:
        dict: Generated memory data or None if not possible
    """
    # This is a placeholder that would be implemented with an actual API call
    
    if not api_key or not messages:
        return None
    
    # In a real implementation, this would analyze the conversation and
    # extract important information worth remembering long-term
    
    # For now, return a placeholder
    return {
        "content": "This is a placeholder for a generated memory",
        "importance": 5,
        "memory_type": "conversation_insight",
        "created_at": datetime.now().isoformat()
    }


def safe_serialize(obj: Any) -> Any:
    """
    Safely serialize objects for storage, handling datetime objects.
    
    Args:
        obj: The object to serialize
        
    Returns:
        JSON-serializable representation of the object
    """
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    elif isinstance(obj, datetime.date):
        return obj.isoformat()
    elif isinstance(obj, (list, tuple)):
        return [safe_serialize(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: safe_serialize(v) for k, v in obj.items()}
    elif isinstance(obj, (int, float, bool, str, type(None))):
        return obj
    else:
        try:
            # Try to convert to string
            return str(obj)
        except Exception:
            # If all else fails
            return None


def load_json_file(file_path: str, default: Any = None) -> Any:
    """
    Safely load JSON from a file with error handling.
    
    Args:
        file_path: Path to the JSON file
        default: Default value to return if file doesn't exist or is invalid
        
    Returns:
        Parsed JSON data or default value
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.debug(f"File not found: {file_path}")
        return default if default is not None else {}
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in file: {file_path}")
        return default if default is not None else {}
    except Exception as e:
        logger.error(f"Error loading JSON file {file_path}: {str(e)}")
        return default if default is not None else {}


def save_json_file(file_path: str, data: Any) -> bool:
    """
    Safely save data to a JSON file with error handling.
    
    Args:
        file_path: Path to save the JSON file
        data: Data to save
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Prepare data for serialization
        serializable_data = safe_serialize(data)
        
        # Write to file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(serializable_data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"Error saving JSON file {file_path}: {str(e)}")
        return False


def extract_topics(text: str, max_topics: int = 3) -> List[str]:
    """
    Extract main topics from text using simple keyword extraction.
    
    This is a simplified implementation. In a production system,
    you would use NLP techniques like TF-IDF or topic modeling.
    
    Args:
        text: The text to extract topics from
        max_topics: Maximum number of topics to extract
        
    Returns:
        List of topic strings
    """
    # Sanitize input
    text = sanitize_input(text)
    
    # Remove common stopwords (simplified list)
    stopwords = {
        "a", "an", "the", "and", "or", "but", "if", "is", "are", "was", "were",
        "i", "you", "he", "she", "it", "we", "they", "my", "your", "his", "her",
        "its", "our", "their", "have", "has", "had", "do", "does", "did", "can",
        "could", "will", "would", "shall", "should", "may", "might", "must", "to",
        "in", "on", "at", "by", "for", "with", "about", "against", "between", "into",
        "through", "during", "before", "after", "above", "below", "from", "up", "down",
        "of", "off", "over", "under", "again", "further", "then", "once", "here", "there",
        "when", "where", "why", "how", "all", "any", "both", "each", "few", "more",
        "most", "other", "some", "such", "no", "nor", "not", "only", "own", "same",
        "so", "than", "too", "very", "s", "t", "just", "don", "now"
    }
    
    # Tokenize and clean text
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    filtered_words = [word for word in words if word not in stopwords]
    
    # Count word frequencies
    word_counts = {}
    for word in filtered_words:
        word_counts[word] = word_counts.get(word, 0) + 1
    
    # Get top words by frequency
    sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
    top_words = [word for word, count in sorted_words[:max_topics] if count > 1]
    
    return top_words 