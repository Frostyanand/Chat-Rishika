#!/usr/bin/env python3
"""
Demo script to show JSON storage functionality in action.
This will create demo data and show the JSON files that are created.
"""
import os
import json
from memory_management import initialize, get_memory_store

# Directory to store demo data
DEMO_DIR = "./demo_data"

def print_json_file(filepath):
    """Pretty print a JSON file's contents"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(json.dumps(data, indent=2))
    except Exception as e:
        print(f"Error reading {filepath}: {e}")

def main():
    # Create and initialize demo directory
    if os.path.exists(DEMO_DIR):
        print(f"Removing existing {DEMO_DIR} directory")
        import shutil
        shutil.rmtree(DEMO_DIR)
    
    os.makedirs(DEMO_DIR, exist_ok=True)
    print(f"Created {DEMO_DIR} directory")
    
    # Initialize memory management with demo directory
    initialize({"DATA_DIR": DEMO_DIR})
    print("Initialized memory management system")
    
    # Get memory store
    memory = get_memory_store()
    
    # Create demo user
    user_id = "demo_user"
    print(f"Creating user with ID: {user_id}")
    memory.create_user(user_id, {"name": "Demo User", "preferences": {"theme": "light"}})
    
    # Store messages
    print("Storing messages")
    memory.store_message(user_id, "Hello Elysia!", is_user=True)
    memory.store_message(user_id, "Hello Demo User! How can I help you today?", is_user=False)
    memory.store_message(user_id, "I'm interested in AI and programming.", is_user=True)
    memory.store_message(user_id, "That's great! I can help you with AI and programming topics.", is_user=False)
    
    # Store user facts
    print("Storing user facts")
    memory.store_user_fact(user_id, "interests", "programming")
    memory.store_user_fact(user_id, "interests", "artificial intelligence")
    memory.store_user_fact(user_id, "location", "New York")
    
    # Store permanent memory
    print("Storing permanent memory")
    memory.store_permanent_memory(user_id, "First conversation with Demo User", "first_meeting")
    
    # Update user profile
    print("Updating user profile")
    memory.update_user_profile(user_id, {"bio": "A demo user for testing", "timezone": "UTC-5"})
    
    # Update metrics
    print("Updating metrics")
    memory.update_conversation_metrics(user_id, {"sentiment_score": 0.85, "topics": ["ai", "programming"]})
    
    # Set global context
    print("Setting global context")
    memory.set_global_context("system_version", "1.0.0")
    
    # Show created files
    print("\nFiles created in JSON storage:")
    for root, dirs, files in os.walk(DEMO_DIR):
        for file in files:
            print(f"  {os.path.join(root, file)}")
    
    # Show content of some files
    user_dir = os.path.join(DEMO_DIR, user_id)
    
    print("\nUser profile:")
    print_json_file(os.path.join(user_dir, "user_profile.json"))
    
    print("\nConversation history:")
    print_json_file(os.path.join(user_dir, "conversation_history.json"))
    
    print("\nUser facts:")
    print_json_file(os.path.join(user_dir, "user_facts.json"))
    
    print("\nPermanent memories:")
    print_json_file(os.path.join(user_dir, "permanent_memories.json"))
    
    print("\nDemo completed! All JSON storage features are working correctly.")

if __name__ == "__main__":
    main() 