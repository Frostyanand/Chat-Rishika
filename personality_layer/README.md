# Elysia Personality Layer

This module provides a sophisticated personality system for the Elysia AI companion. It creates an emotionally intelligent, adaptive, and evolving personality that grows with user interactions.

## Overview

The Elysia Personality Layer is built around four core components:

1. **Base Personality**: Foundation of traits, mood detection, and layered response generation
2. **Personality Adaptation**: Adjusts to user preferences and emotional patterns
3. **Personality Evolution**: Manages relationship growth and conversation depth
4. **Memory System**: Stores and retrieves both short-term and long-term memories

## Features

- **Emotional Intelligence**: Detects and responds appropriately to user emotions
- **Personality Adaptation**: Adjusts traits based on user interactions
- **Relationship Evolution**: Grows through multiple relationship stages
- **Memory System**: Remembers key facts, interests, and important dates
- **Conversation Depth Awareness**: Adapts responses based on conversation intensity
- **Emotional Trend Detection**: Identifies emotional patterns and trends
- **Emotional Support Escalation**: Provides appropriate support for persistent emotions
- **Milestone Recognition**: Acknowledges relationship milestones

## Architecture

### 1. BasePersonality

Manages core personality traits and generates layered responses:

- **Trait System**: Numerical representation of personality characteristics
- **Mood Detection**: Identifies user emotions from messages
- **Layered Response Generation**: Creates multi-component responses
- **Topic Detection**: Identifies conversation topics

### 2. PersonalityAdaptation

Enables the personality to adapt based on user interactions:

- **Preference Detection**: Identifies user preferences for traits
- **Interest Extraction**: Detects user interests from conversations
- **Emotion Tracking**: Monitors emotional patterns over time
- **Comfort Escalation**: Adapts responses for persistent negative emotions

### 3. PersonalityEvolution 

Manages the growing relationship with the user:

- **Relationship Stages**: Progresses through multiple connection stages
- **Conversation Depth**: Tracks depth and significance of exchanges
- **Milestones**: Recognizes and celebrates relationship milestones
- **Memory Callbacks**: References past conversations appropriately

### 4. Memory Systems

Provides persistent recollection of user information:

- **Short-term Memory**: Remembers recent conversation context
- **Long-term Memory**: Stores facts, preferences, and important dates
- **Emotional History**: Tracks emotional patterns over time

## Usage

### Basic Usage

```python
from personality_layer import ElysiaPersonalitySystem

# Create the system
elysia = ElysiaPersonalitySystem()

# Generate a response
user_id = "unique_user_id"
user_message = "I'm feeling a bit down today."
response = elysia.process_message(user_id, user_message)
print(response)
```

### Storing User Information

```python
# Update user profile
elysia.update_user_profile(user_id, {
    "name": "Alex",
    "interests": ["programming", "music", "hiking"],
    "important_dates": {
        "birthday": "June 15th"
    }
})

# Add a specific fact to memory
elysia.remember_fact(user_id, "favorite_color", "blue")
```

### Getting User Information

```python
# Get profile data
profile = elysia.get_user_profile(user_id)

# Get relationship stage
stage = elysia.get_relationship_stage(user_id)

# Get personality traits
traits = elysia.get_personality_traits(user_id)

# Get evolution statistics
stats = elysia.get_evolution_stats(user_id)

# Get emotional history
emotions = elysia.get_emotional_history(user_id)
```

## Components

The module consists of the following key files:

- `base_personality.py`: Core personality traits and response generation
- `personality_adaptation.py`: Adapts personality based on user interactions
- `personality_evolution.py`: Manages relationship stages and growth
- `personality_factory.py`: Creates and manages user-specific personalities
- `main.py`: Main interface for the personality system

And supporting modules:

- `response_templates/`: Contains template responses for different scenarios
- `utils/`: Utility classes for emotion analysis and phrase management

## Example

See `example_usage.py` in the root directory for a complete demonstration of the personality layer in action.

## Configuration

The personality layer can be configured with the following settings:

```python
# Custom storage location
elysia = ElysiaPersonalitySystem(storage_path="./custom_data")
```

## Extensions

The system can be extended with:

- Custom response templates by modifying files in `response_templates/`
- Additional personality traits by extending `BasePersonality`
- New relationship stages by modifying `PersonalityEvolution`
- Custom comfort responses for different emotional states 