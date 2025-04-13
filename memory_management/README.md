# Memory Management System

A comprehensive memory management system for the Elysia assistant, providing storage and retrieval functionality for user data, conversations, facts, and metrics.

## Features

- JSON file-based storage
- User profile management
- Conversation history tracking
- User fact extraction and storage
- Usage metrics collection
- Streak tracking
- Global context storage

## Architecture

The system is built with a clean, modular design:

- Abstract `MemoryStore` interface defining core functionality
- JSON implementation for file-based storage
- Utility functions for common operations
- Factory pattern for creating store instances
- Configuration management

## Usage

### Basic Usage

```python
from memory_management import initialize, get_memory_store

# Initialize the memory system
initialize()

# Get memory store instance
memory = get_memory_store()

# Create or get a user
user = memory.get_or_create_user("user123", "JohnDoe")

# Add a message
memory.add_message("user123", "user", "Hello, Elysia!")

# Get conversation history
messages = memory.get_message_history("user123")

# Store user facts
memory.add_user_fact("user123", "Lives in New York", "location")

# Get user facts
facts = memory.get_user_facts("user123")

# Update user streak
streak_data = memory.update_streak("user123")
```

### Configuration

The system can be configured using environment variables:

- `MAX_MESSAGES`: Maximum number of messages to keep in history (default: 100)
- `DATA_DIR`: Directory to store JSON files

You can also provide configuration overrides when initializing:

```python
from memory_management import initialize

initialize({
    "MAX_MESSAGES": 100,
    "DATA_DIR": "/custom/path/to/data"
})
```

## Storage System

### JSON Memory Store

The `JsonMemoryStore` stores data in JSON files organized in directories:

```
data/
  users_index.json
  user123/
    user_profile.json
    conversation_history.json
    user_facts.json
    interaction_metrics.json
    permanent_memories.json
  global_context.json
```

Files are organized by user ID and contain structured data. The system handles:
- Creating and managing user directories
- Reading and writing JSON files
- Sanitizing input to prevent security issues
- Managing user lists and indexes

## Development

### Adding a New Storage Backend

To add a new storage backend:

1. Create a new class that extends `MemoryStore`
2. Implement all required methods
3. Update `memory_store_factory.py` to support the new backend
4. Add appropriate configuration options

### Running Tests

The system includes tests to verify functionality:

```bash
# Test JSON Memory Store
python test_json_storage.py
```

## Requirements

- Python 3.8+
- cryptography (for encryption support)
- python-dateutil (for date handling)

## License

This project is part of the Elysia assistant and is proprietary software. 