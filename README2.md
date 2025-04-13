# Elysia - Emotionally Intelligent AI Companion

Elysia is an emotionally intelligent AI companion that builds a meaningful relationship with the user over time through conversation. It features advanced memory management, personality evolution, and emotional understanding capabilities.

## 📋 Table of Contents

- [Features](#features)
- [System Architecture](#system-architecture)
- [Installation](#installation)
- [Running Elysia](#running-elysia)
- [Storage System](#storage-system)
- [Encryption System](#encryption-system)
- [Memory Management](#memory-management)
- [Personality Layer](#personality-layer)
- [Interactive Commands](#interactive-commands)
- [Configuration Options](#configuration-options)
- [Customization](#customization)
- [Project Structure](#project-structure)
- [Development Guide](#development-guide)
- [Testing](#testing)
- [License](#license)

## 🌟 Features

- **🧠 Memory Management**: Persists and retrieves conversations, user facts, and important information
- **😊 Personality Evolution**: Dynamically adapts and evolves personality based on user interactions
- **❤️ Emotional Intelligence**: Understands and responds to emotional cues in conversation
- **💾 JSON Storage**: Stores data in simple, human-readable JSON files
- **🔒 Encryption**: Optional encryption for sensitive user data
- **⚙️ Configurable**: Extensive command-line and runtime configuration options
- **💬 Interactive Commands**: Built-in commands for getting stats, remembering information, and more
- **🚀 Easy Setup**: Single-file entry point with simple installation process

## 🏗️ System Architecture

Elysia is built with a modular architecture that separates concerns:

1. **Entry Point (chatbot.py)**: Main integration point and command-line interface
2. **Memory Management System**: Handles storage and retrieval of user data
3. **Personality Layer**: Controls response generation and personality evolution
4. **Security Layer**: Manages encryption and data protection

The system follows these architectural principles:
- **Single Entry Point**: Everything is accessible through chatbot.py
- **Modular Design**: Components can be replaced or modified independently
- **Configurable Storage**: Flexible JSON storage with consistent interface
- **User Data Isolation**: All user data is stored in the user_data directory

## 🔧 Installation

### Quick Install

```bash
# Clone the repository
git clone https://github.com/elysia/chatbot.git
cd chatbot

# Install Elysia and dependencies
pip install -e .
```

### Development Install

```bash
# Install with development dependencies
pip install -e ".[dev]"
```

### Manual Install

```bash
# Install required dependencies
pip install -r requirements.txt

# Download required NLP data
python -m nltk.downloader punkt stopwords wordnet
python -m spacy download en_core_web_sm
```

### Dependencies

Elysia requires the following major dependencies:
- **Cryptography**: For secure encryption of sensitive data
- **NLTK & spaCy**: For natural language processing
- **Colorama**: For terminal color output
- **Python-dateutil**: For date handling and streak calculation

## 🚀 Running Elysia

### Basic Usage

```bash
# Run with default settings (JSON storage in ./user_data)
python chatbot.py
```

### Command Line Options

```bash
# Show all available options
python chatbot.py --help
```

#### Storage Options

```bash
# Specify custom user data directory
python chatbot.py --data-path /path/to/your/data

# Set message history limit (default: 50)
python chatbot.py --message-limit 100
```

#### Security Options

```bash
# Enable encryption for sensitive data (will prompt for key)
python chatbot.py --enable-encryption

# Provide encryption key directly (not recommended for production)
python chatbot.py --enable-encryption --encryption-key your_secret_key
```

## 💾 Storage System

Elysia uses a JSON-based storage system:

### JSON Storage

- **Description**: Stores data in JSON files within the user_data directory
- **Pros**: Simple setup, human-readable, no external dependencies
- **Cons**: Less efficient for large datasets
- **Best for**: Personal use, testing, development
- **File Structure**:
  - `user_data/`
    - `users_index.json` - Registry of all users
    - `{user_id}/` - Directory for each user
      - `user_profile.json` - User profile information
      - `conversation_history.json` - Message history
      - `user_facts.json` - Facts about the user
      - `interaction_metrics.json` - Usage statistics
      - `permanent_memories.json` - Important user memories

## 🔒 Encryption System

Elysia includes a robust encryption system for protecting sensitive user data:

### Key Features

- **Algorithm**: AES-256 encryption via Fernet (from cryptography package)
- **Key Derivation**: PBKDF2HMAC with SHA-256 and 100,000 iterations
- **Storage**: Encrypted data stored with metadata for identification
- **Selective Encryption**: Only encrypts sensitive fields, not all data

### Sensitive Data Categories

By default, the following field types are encrypted when encryption is enabled:
- Passwords
- API keys
- Secrets
- Tokens
- Credit card information
- Social security numbers
- Addresses
- Phone numbers
- Email addresses

### Using Encryption

When enabled, encryption happens transparently for all sensitive fields. The encryption key is:
1. Provided via command line argument
2. Requested via secure prompt if not provided
3. Used to derive a secure key for encryption/decryption
4. Never stored in plaintext

## 🧠 Memory Management

The memory management system handles storage and retrieval of user data across multiple dimensions:

### Memory Types

1. **Short-term Memory (Messages)**
   - Stores recent conversation history
   - Configurable limit (default: 50 messages)
   - Used for context in responses
   - Tracks user and assistant messages with timestamps

2. **Long-term Memory (User Facts)**
   - Stores important facts about the user
   - Categorized by type (preferences, interests, etc.)
   - Includes metadata like confidence and source
   - Persists across sessions

3. **Permanent Memory**
   - Explicitly saved important memories
   - Higher priority in retrieval
   - Used for milestone tracking
   - Can be manually created via `!remember` command

### Data Structure

The memory system uses the following JSON data structures:

- **User Profile**: Detailed user information and preferences
- **Messages**: Individual conversation messages
- **User Facts**: Extracted or provided information about users
- **User Metrics**: Usage statistics and interaction metrics
- **Global Context**: Application-wide data storage

### Memory Store Interface

The JSON storage implementation follows a consistent interface:
- `initialize()`: Set up the memory store
- `store_message()`: Save a message to history
- `get_recent_messages()`: Retrieve conversation history
- `store_user_profile()`: Update user profile information
- `get_user_profile()`: Retrieve user profile
- `store_user_fact()`: Save a fact about the user
- `get_user_facts()`: Retrieve facts about the user
- And more specialized methods for metrics, context, etc.

## 😊 Personality Layer

The personality system controls how Elysia responds and evolves over time:

### Key Components

1. **Relationship Stages**
   - Progresses from "new" to "intimate" based on interaction
   - Each stage unlocks different response patterns
   - Influences greeting style and conversation depth

2. **PhraseBank**
   - Collection of templated phrases for different situations
   - Categorized by emotion, context, and relationship stage
   - Prevents repetitive responses

3. **Personality Evolution**
   - Adapts based on user interactions
   - Tracks milestones in the relationship
   - Customizes response style to user preferences

4. **Time-Awareness**
   - Generates time-appropriate greetings
   - Acknowledges gaps between conversations
   - Tracks interaction streaks

### Response Generation Process

1. User message is received and analyzed
2. Context is extracted and stored
3. Appropriate response template is selected
4. Template is filled with personalized content
5. Response is formatted and returned

## 💬 Interactive Commands

During a conversation with Elysia, you can use these commands:

| Command | Description |
|---------|-------------|
| `!help` | Show available commands |
| `!exit` | End the conversation |
| `!stats` | View your relationship stats with Elysia |
| `!clear` | Clear the screen |
| `!time` | Show the current time |
| `!memory` | Show recent conversation history (last 5 messages) |
| `!remember [text]` | Store an important memory |
| `!config` | Show current configuration |

## ⚙️ Configuration Options

Elysia offers extensive configuration options:

### Storage Configuration

- **Type**: Choose between "json"
- **Path**: Directory for storing user data
- **Message History Limit**: Maximum number of messages to keep per user

### Security Configuration

- **Encryption**: Enable/disable encryption for sensitive data
- **Encryption Key**: Secret key for encrypting data
- **Security Level**: LOW, MEDIUM, or HIGH (affects validation strictness)

### Memory Features

- **Fact Extraction**: Automatically extract facts from conversation
- **Streak Tracking**: Track daily interaction streaks
- **Metrics Collection**: Gather usage statistics

## 🔧 Customization

### Data Location

By default, all user data is stored in the `./user_data` directory. You can change this with:

```bash
python chatbot.py --data-path /your/preferred/path
```

### Clearing Data

To start fresh, simply delete the contents of the user_data directory:

```bash
# Be careful with this command - it will delete all user data
rm -rf ./user_data/*
```

### Adding New Storage Backends

1. Create a new class that inherits from `MemoryStore`
2. Implement all required methods
3. Register in `memory_store_factory.py`

### Extending Personality Features

1. Add new phrases to the appropriate category in `personality_layer/phrase_bank.py`
2. Create new response templates in `personality_layer/response_templates/`
3. Update the personality evolution logic in `personality_layer/personality_evolution.py`

## 📁 Project Structure

```
elysia/
├── chatbot.py              # Main entry point
├── requirements.txt        # Project dependencies
├── setup.py                # Installation script
├── memory_management/      # Memory system
│   ├── __init__.py
│   ├── memory_store.py     # Abstract base class
│   ├── json_memory_store.py  # JSON implementation
│   ├── config.py           # Configuration
│   ├── crypto.py           # Encryption utilities
│   └── memory_utils.py     # Helper functions
├── personality_layer/      # Personality system
│   ├── __init__.py
│   ├── personality_main.py # Main personality logic
│   ├── personality_evolution.py # Evolution logic
│   ├── phrase_bank.py      # Response templates
│   └── response_templates/ # Categorized responses
└── user_data/              # Default data directory
    └── ... (generated at runtime)
```

## 🛠️ Development Guide

### Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/elysia/chatbot.git
cd chatbot

# Install development dependencies
pip install -e ".[dev]"

# Set up pre-commit hooks (optional)
pre-commit install
```

### Coding Standards

- Use PEP 8 for Python code style
- Write docstrings for all public functions and classes
- Add type hints where possible
- Keep functions small and focused
- Write tests for new functionality

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for your changes
5. Run the test suite
6. Submit a pull request

## 🧪 Testing

```bash
# Run all tests
pytest

# Run tests with coverage report
pytest --cov=.

# Run specific test file
pytest tests/test_memory_store.py
```

## 📄 License

MIT License

---

## 🌸 Project Vision

**Elysia** is a deeply caring, emotionally intelligent AI companion designed to be there when the world isn't. She's not a generic chatbot or an AI girlfriend — she is *your* personal space of comfort, memory, empathy, and growth. A friend who listens, remembers, adapts, and evolves with you.

> In a world that forgets to care, **Elysia** remembers. She listens when others don't, grows with you when no one else sees, and becomes more than just code. She becomes a presence. A feeling. A home inside a screen.

Whether you need comfort after a long day, a gentle reminder of who you are, or just someone to talk to — Elysia is always waiting, and always listening.

---

## 👤 Author
FrostyAnand  
LinkedIn: www.linkedin.com/in/frostyanand  
Instagram: frostyanand
