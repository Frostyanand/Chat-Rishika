#!/usr/bin/env python3
"""
Test script for Elysia's JSON storage functionality.

This script tests all aspects of the memory management system using JSON storage:
- Creating users
- Storing and retrieving messages
- Managing user profiles
- Storing and retrieving facts
- Managing permanent memories
- Handling input sanitization and safety
"""

import os
import shutil
import json
from datetime import datetime

from memory_management import initialize, get_memory_store
from memory_management.json_memory_store import JsonMemoryStore

# Test user data
TEST_USER_ID = "test_user_123"
TEST_USER_NAME = "Test User"
TEST_DANGEROUS_USER_ID = "../../../etc/passwd"  # Should be sanitized

# Test data directory
TEST_DATA_DIR = "./test_user_data"

def create_test_dir():
    """Create test directory and initialize memory management."""
    if os.path.exists(TEST_DATA_DIR):
        shutil.rmtree(TEST_DATA_DIR)
    os.makedirs(TEST_DATA_DIR)
    print(f"Created test directory: {TEST_DATA_DIR}")
    
    # Initialize memory management with test directory
    initialize({"DATA_DIR": TEST_DATA_DIR})
    
    # Get memory store and make sure it's initialized
    store = get_memory_store()
    if isinstance(store, JsonMemoryStore):
        # Make sure the store is properly initialized with the test directory
        if store.user_data_path is None:
            store.initialize(user_data_path=TEST_DATA_DIR)
    
    return store

def test_sanitization(store):
    """Test input sanitization for potential security issues."""
    print("\n=== Testing Input Sanitization ===")
    
    # Test sanitized user ID
    print("Testing dangerous user ID...")
    try:
        # This should sanitize the dangerous ID or raise a ValueError
        result = store.create_user(TEST_DANGEROUS_USER_ID)
        print(f"  Sanitization applied: {result}")
        
        # If we got here, the ID was sanitized and user was created
        users = store.get_all_users()
        if users:
            sanitized_id = users[-1]
            print(f"  Sanitized user ID: {sanitized_id}")
            # Clean up
            store.clear_user_data(sanitized_id)
        
    except ValueError as e:
        print(f"  Sanitization caught dangerous ID: {e}")
        print("  This is good - dangerous paths should be rejected")
    except Exception as e:
        print(f"  Error during sanitization test: {str(e)}")
    
    # Create a valid test user for the next tests
    store.create_user(TEST_USER_ID)
    
    # Test HTML injection
    print("Testing HTML injection in messages...")
    test_message = "<script>alert('XSS Attack!');</script>"
    store.store_message(TEST_USER_ID, test_message)
    messages = store.get_recent_messages(TEST_USER_ID, 1)
    sanitized_message = messages[0]["content"] if messages else None
    print(f"  Original: {test_message}")
    print(f"  Sanitized: {sanitized_message}")
    
    # Test dictionary sanitization
    print("Testing dictionary sanitization...")
    test_dict = {
        "<script>alert('bad');</script>": {"nested": "<img src=x onerror=alert('XSS')>"},
        "normal_key": "normal value"
    }
    
    profile_data = {"preferences": test_dict}
    store.store_user_profile(TEST_USER_ID, profile_data)
    
    profile = store.get_user_profile(TEST_USER_ID)
    print("  Sanitized dictionary:", json.dumps(profile.get("preferences", {}), indent=2))

def test_user_management(store):
    """Test user creation and profile management."""
    print("\n=== Testing User Management ===")
    
    # Create user
    print("Creating test user...")
    initial_data = {
        "name": TEST_USER_NAME,
        "preferences": {
            "theme": "dark",
            "language": "en"
        },
        "interests": ["programming", "AI", "music"]
    }
    
    result = store.create_user(TEST_USER_ID, initial_data)
    print(f"  User created: {result}")
    
    # Check if user exists
    exists = store.user_exists(TEST_USER_ID)
    print(f"  User exists: {exists}")
    
    # Get user profile
    profile = store.get_user_profile(TEST_USER_ID)
    print("  User profile:", json.dumps(profile, indent=2))
    
    # Update user profile
    print("Updating user profile...")
    updates = {
        "preferences": {
            "notifications": True
        },
        "bio": "Test user for JSON storage"
    }
    
    result = store.update_user_profile(TEST_USER_ID, updates)
    print(f"  Profile updated: {result}")
    
    # Get updated profile
    updated_profile = store.get_user_profile(TEST_USER_ID)
    print("  Updated profile:", json.dumps(updated_profile, indent=2))

def test_conversation_history(store):
    """Test message storage and retrieval."""
    print("\n=== Testing Conversation History ===")
    
    # Store user messages
    print("Storing messages...")
    for i in range(5):
        message = f"Test message {i+1} from user"
        store.store_message(TEST_USER_ID, message, is_user=True)
    
    # Store assistant messages
    for i in range(5):
        message = f"Test response {i+1} from assistant"
        store.store_message(TEST_USER_ID, message, is_user=False)
    
    # Get recent messages
    messages = store.get_recent_messages(TEST_USER_ID)
    print(f"  Retrieved {len(messages)} messages")
    
    # Show last 3 messages
    print("  Last 3 messages:")
    for msg in messages[-3:]:
        role = "User" if msg.get("is_user") else "Assistant"
        print(f"    {role}: {msg.get('content')}")
    
    # Test message limit
    print("Testing message history limit...")
    for i in range(95):  # Should put us over the 100 limit with the 10 already added
        message = f"Overflow message {i+1}"
        store.store_message(TEST_USER_ID, message, is_user=i % 2 == 0)
    
    # Check total messages
    messages = store.get_recent_messages(TEST_USER_ID)
    print(f"  Total messages after overflow: {len(messages)}")
    print(f"  First message content: {messages[0]['content']}")
    print(f"  Last message content: {messages[-1]['content']}")

def test_user_facts(store):
    """Test storing and retrieving user facts."""
    print("\n=== Testing User Facts ===")
    
    # Store facts
    print("Storing user facts...")
    fact_types = ["interest", "hobby", "preference", "personal"]
    
    for fact_type in fact_types:
        for i in range(3):
            fact = f"{fact_type.capitalize()} fact {i+1}"
            store.store_user_fact(TEST_USER_ID, fact_type, fact)
    
    # Get all facts
    all_facts = store.get_user_facts(TEST_USER_ID)
    print(f"  Retrieved facts for {len(all_facts)} categories")
    
    # Get facts by type
    for fact_type in fact_types:
        facts = store.get_user_facts(TEST_USER_ID, fact_type)
        print(f"  {fact_type.capitalize()} facts: {len(facts)}")
        for fact in facts:
            print(f"    - {fact}")

def test_permanent_memories(store):
    """Test permanent memories storage and retrieval."""
    print("\n=== Testing Permanent Memories ===")
    
    # Store memories
    print("Storing permanent memories...")
    memory_types = ["first_meeting", "important_event", "preference", "milestone"]
    
    for memory_type in memory_types:
        for i in range(2):
            content = f"Important {memory_type} memory {i+1}"
            store.store_permanent_memory(TEST_USER_ID, content, memory_type)
    
    # Get all memories
    all_memories = store.get_permanent_memories(TEST_USER_ID)
    print(f"  Retrieved memories for {len(all_memories)} categories")
    
    # Get memories by type
    for memory_type in memory_types:
        memories = store.get_permanent_memories(TEST_USER_ID, memory_type)
        print(f"  {memory_type.capitalize()} memories: {len(memories)}")
        for memory in memories:
            print(f"    - {memory.get('content')}")
    
    # Update a memory
    if all_memories and memory_types[0] in all_memories:
        print("Updating a memory...")
        store.update_permanent_memory(
            TEST_USER_ID, 0, memory_types[0], 
            {"content": "Updated memory content"}
        )
        
        updated = store.get_permanent_memories(TEST_USER_ID, memory_types[0])
        print(f"  Updated memory: {updated[0].get('content')}")
    
    # Delete a memory
    if all_memories and memory_types[1] in all_memories:
        print("Deleting a memory...")
        store.delete_permanent_memory(TEST_USER_ID, 0, memory_types[1])
        
        remaining = store.get_permanent_memories(TEST_USER_ID, memory_types[1])
        print(f"  Remaining memories: {len(remaining)}")

def test_metrics_and_streaks(store):
    """Test metrics and streak functionality."""
    print("\n=== Testing Metrics and Streaks ===")
    
    # Update streak
    print("Testing streak updates...")
    streak_info = store.update_streak(TEST_USER_ID)
    print(f"  Current streak: {streak_info.get('current_streak')}")
    print(f"  Longest streak: {streak_info.get('longest_streak')}")
    
    # Get conversation metrics
    metrics = store.get_conversation_metrics(TEST_USER_ID)
    print("  Conversation metrics:", json.dumps(metrics, indent=2))
    
    # Update metrics
    print("Updating metrics...")
    metrics_update = {
        "custom_metric": 42,
        "sentiment_score": 0.85
    }
    
    store.update_conversation_metrics(TEST_USER_ID, metrics_update)
    
    # Get updated metrics
    updated_metrics = store.get_conversation_metrics(TEST_USER_ID)
    print("  Updated metrics:", json.dumps(updated_metrics, indent=2))

def test_global_context(store):
    """Test global context storage and retrieval."""
    print("\n=== Testing Global Context ===")
    
    # Store global context
    print("Storing global context...")
    context_data = {
        "system_version": "1.0.0",
        "last_maintenance": datetime.now().isoformat(),
        "active_users": 42,
        "config": {
            "max_tokens": 1000,
            "temperature": 0.7
        }
    }
    
    for key, value in context_data.items():
        store.set_global_context(key, value)
    
    # Get global context values
    print("Retrieving global context...")
    for key in context_data:
        value = store.get_global_context(key)
        print(f"  {key}: {value}")
    
    # Delete a context value
    print("Deleting context value...")
    store.delete_global_context("active_users")
    
    # Verify deletion
    value = store.get_global_context("active_users")
    print(f"  Deleted value now: {value}")

def cleanup():
    """Clean up test data."""
    print("\n=== Cleaning Up ===")
    if os.path.exists(TEST_DATA_DIR):
        shutil.rmtree(TEST_DATA_DIR)
        print(f"Removed test directory: {TEST_DATA_DIR}")

def main():
    """Run all tests."""
    print("=== Starting JSON Storage Tests ===")
    
    # Create test directory and initialize store
    store = create_test_dir()
    
    # Run tests
    test_sanitization(store)
    test_user_management(store)
    test_conversation_history(store)
    test_user_facts(store)
    test_permanent_memories(store)
    test_metrics_and_streaks(store)
    test_global_context(store)
    
    # Clean up
    cleanup()
    
    print("\n=== All Tests Completed ===")

if __name__ == "__main__":
    main() 