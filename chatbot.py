#!/usr/bin/env python3
"""
chatbot.py - Main entry point for the Elysia chatbot
"""
import os
import time
import random
import getpass
import argparse
import logging
from datetime import datetime

# Import colorama for cross-platform colored terminal output
from colorama import Fore, Style, init
init()  # Initialize colorama

# Configure logging - only show WARNING and above to keep conversations natural
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import our personality layer
from personality_layer import ElysiaPersonalitySystem

# Import our memory management system components
from memory_management.memory_store_factory import create_memory_store
from memory_management.json_memory_store import JsonMemoryStore
from memory_management.crypto import set_encryption_key

# Default Configuration
DEFAULT_CONFIG = {
    "storage": {
        "type": "json",  # Only json is supported
        "path": "./user_data",
        "message_history_limit": 100
    },
    "security": {
        "encryption_enabled": False,
        "encryption_key": None
    },
    "api": {
        "enabled": False,
        "api_key": None,
        "max_tokens": 1000,
        "model": None
    }
}

class ElysiaChatbot:
    """Main integration class for Elysia chatbot system"""
    
    def __init__(self, config=None):
        """Initialize Elysia chatbot with all its components"""
        print(f"{Fore.CYAN}Initializing Elysia Chatbot...{Style.RESET_ALL}")
        
        # Use provided config or default
        self.config = config or DEFAULT_CONFIG.copy()
        
        # Ensure storage config exists
        if "storage" not in self.config:
            self.config["storage"] = DEFAULT_CONFIG["storage"].copy()
        if "security" not in self.config:
            self.config["security"] = DEFAULT_CONFIG["security"].copy()
        if "api" not in self.config:
            self.config["api"] = DEFAULT_CONFIG["api"].copy()
        
        # Force JSON storage type
        self.config["storage"]["type"] = "json"
        
        # Ensure user_data directory exists
        user_data_path = self.config["storage"]["path"]
        os.makedirs(user_data_path, exist_ok=True)
        
        # Set up encryption if enabled
        if self.config["security"]["encryption_enabled"]:
            encryption_key = self.config["security"]["encryption_key"]
            if encryption_key:
                print(f"{Fore.YELLOW}Setting up encryption for sensitive data...{Style.RESET_ALL}")
                if set_encryption_key(encryption_key):
                    print(f"{Fore.GREEN}Encryption enabled successfully.{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}Failed to enable encryption. Proceeding without encryption.{Style.RESET_ALL}")
                    self.config["security"]["encryption_enabled"] = False
        
        # Initialize the memory store
        try:
            # Create memory store (JSON storage)
            self.memory_store = create_memory_store(**self.config)
            
            # Initialize memory store with data path
            print(f"{Fore.YELLOW}Initializing JSON storage in {user_data_path}{Style.RESET_ALL}")
            self.memory_store.initialize(user_data_path=user_data_path)
                
        except Exception as e:
            print(f"{Fore.RED}Error initializing storage: {e}. Creating new JSON storage.{Style.RESET_ALL}")
            self.memory_store = JsonMemoryStore(
                message_history_limit=self.config["storage"].get("message_history_limit", 100)
            )
            self.memory_store.initialize(user_data_path=user_data_path)
        
        # Initialize the personality system
        self.personality_system = ElysiaPersonalitySystem(storage_path=user_data_path)
        
        # Add conversation tracking
        self.conversation_history = []
        
        print(f"{Fore.GREEN}Elysia initialization complete.{Style.RESET_ALL}")
    
    def process_user_message(self, user_id, message):
        """Process user message and generate a response"""
        if not message or not user_id:
            return "I didn't catch that. Could you please try again?"
        
        try:
            # Store message in memory system and conversation history
            self.memory_store.store_message(user_id, message, is_user=True)
            
            self.conversation_history.append({
                "sender": "user",
                "message": message,
                "timestamp": datetime.now().isoformat()
            })
            
            # Process the message through personality system
            response = self.personality_system.process_message(user_id, message)
            
            # Store Elysia's response in memory system and conversation history
            self.memory_store.store_message(user_id, response, is_user=False)
            
            self.conversation_history.append({
                "sender": "elysia",
                "message": response,
                "timestamp": datetime.now().isoformat()
            })
            
            return response
        except Exception as e:
            print(f"{Fore.RED}Error processing message: {e}{Style.RESET_ALL}")
            return "I'm sorry, I encountered an issue processing your message. Could we try again?"
    
    def get_user_profile(self, user_id):
        """Get the user's profile data"""
        try:
            return self.memory_store.get_user_profile(user_id)
        except Exception as e:
            print(f"{Fore.RED}Error retrieving user profile: {e}{Style.RESET_ALL}")
            return {}
    
    def update_user_profile(self, user_id, updates):
        """Update user profile with new information"""
        try:
            current_profile = self.memory_store.get_user_profile(user_id) or {}
            updated_profile = current_profile.copy()
            self._deep_update(updated_profile, updates)
            self.memory_store.store_user_profile(user_id, updated_profile)
        except Exception as e:
            print(f"{Fore.RED}Error updating user profile: {e}{Style.RESET_ALL}")
    
    def _deep_update(self, original, updates):
        """Deep update a nested dictionary"""
        for key, value in updates.items():
            if key in original and isinstance(original[key], dict) and isinstance(value, dict):
                self._deep_update(original[key], value)
            else:
                original[key] = value
    
    def get_relationship_stage(self, user_id):
        """Get current relationship stage with user"""
        # This still uses the personality system for relationship stages
        return self.personality_system.get_relationship_stage(user_id)
    
    def get_greeting(self, user_id):
        """Get a time and relationship-appropriate greeting"""
        # This still uses the personality system for greetings
        return self.personality_system.get_time_appropriate_greeting(user_id)
    
    def get_recent_messages(self, user_id, limit=50):
        """Get recent conversation messages"""
        try:
            return self.memory_store.get_recent_messages(user_id, limit)
        except Exception as e:
            print(f"{Fore.RED}Error retrieving messages: {e}{Style.RESET_ALL}")
            return []

    def store_user_fact(self, user_id, fact_type, fact_value):
        """Store a fact about the user"""
        try:
            return self.memory_store.store_user_fact(user_id, fact_type, fact_value)
        except Exception as e:
            print(f"{Fore.RED}Error storing user fact: {e}{Style.RESET_ALL}")
            return False
    
    def get_user_facts(self, user_id, fact_type=None):
        """Get facts about the user"""
        try:
            return self.memory_store.get_user_facts(user_id, fact_type)
        except Exception as e:
            print(f"{Fore.RED}Error retrieving user facts: {e}{Style.RESET_ALL}")
            return {}
    
    def get_conversation_metrics(self, user_id):
        """Get metrics about the user's conversation patterns"""
        try:
            return self.memory_store.get_conversation_metrics(user_id)
        except Exception as e:
            print(f"{Fore.RED}Error retrieving conversation metrics: {e}{Style.RESET_ALL}")
            return {}
    
    def update_conversation_metrics(self, user_id, metrics_data):
        """Update metrics about the user's conversation patterns"""
        try:
            return self.memory_store.update_conversation_metrics(user_id, metrics_data)
        except Exception as e:
            print(f"{Fore.RED}Error updating conversation metrics: {e}{Style.RESET_ALL}")
            return False
    
    def store_extracted_context(self, user_id, context_data):
        """Store extracted context from conversation"""
        try:
            return self.memory_store.store_extracted_context(user_id, context_data)
        except Exception as e:
            print(f"{Fore.RED}Error storing context: {e}{Style.RESET_ALL}")
            return False
    
    def get_relevant_context(self, user_id, query=None):
        """Get relevant context for the current conversation"""
        try:
            return self.memory_store.get_relevant_context(user_id, query)
        except Exception as e:
            print(f"{Fore.RED}Error retrieving context: {e}{Style.RESET_ALL}")
            return []
    
    def clear_user_data(self, user_id):
        """Clear all data for a specific user"""
        try:
            return self.memory_store.clear_user_data(user_id)
        except Exception as e:
            print(f"{Fore.RED}Error clearing user data: {e}{Style.RESET_ALL}")
            return False
    
    def store_permanent_memory(self, user_id, memory_content, memory_type="general"):
        """Store a permanent memory for the user that should be preserved long-term"""
        try:
            return self.memory_store.store_permanent_memory(user_id, memory_content, memory_type)
        except Exception as e:
            print(f"{Fore.RED}Error storing permanent memory: {e}{Style.RESET_ALL}")
            return False
    
    def get_permanent_memories(self, user_id, memory_type=None):
        """Get permanent memories for the user"""
        try:
            return self.memory_store.get_permanent_memories(user_id, memory_type)
        except Exception as e:
            print(f"{Fore.RED}Error retrieving permanent memories: {e}{Style.RESET_ALL}")
            return {}

# Helper functions for the CLI interface
def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def format_elysia_message(message):
    """Format Elysia's responses with color and styling"""
    return f"{Fore.CYAN}Elysia: {message}{Style.RESET_ALL}"

def format_user_message(name, message):
    """Format user messages with color and styling"""
    return f"{Fore.GREEN}{name}: {message}{Style.RESET_ALL}"

def format_system_message(message):
    """Format system messages with color and styling"""
    return f"{Fore.YELLOW}System: {message}{Style.RESET_ALL}"

def show_help():
    """Display help information for the chatbot"""
    clear_screen()
    print(f"{Fore.MAGENTA}======== Elysia Commands ========{Style.RESET_ALL}")
    print(f"{Fore.CYAN}Available commands:{Style.RESET_ALL}")
    print("  !exit     - End the conversation with Elysia")
    print("  !stats    - View your relationship stats with Elysia")
    print("  !help     - Show this help message")
    print("  !clear    - Clear the screen")
    print("  !time     - Show the current time")
    print("  !memory   - Show recent conversation history")
    print("  !remember - Save an important memory (e.g., !remember I enjoy hiking)")
    print("  !config   - Show current configuration")
    print()
    print(f"{Fore.CYAN}Tips for interacting with Elysia:{Style.RESET_ALL}")
    print("- Share how you're feeling to experience Elysia's emotional intelligence")
    print("- Return regularly to develop your relationship over time")
    print("- Try sharing some personal interests or important dates")
    print("- Deeper conversations help strengthen your connection")
    print()
    input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
    clear_screen()

def show_relationship_stats(elysia, user_id, user_name):
    """Display the relationship stats between user and Elysia"""
    clear_screen()
    print(f"{Fore.MAGENTA}======== Your Relationship with Elysia ========{Style.RESET_ALL}")
    
    # Get relationship stage
    relationship_stage = elysia.get_relationship_stage(user_id)
    
    # Stage descriptions
    stage_descriptions = {
        "new": "We're just getting to know each other. Every conversation helps us build a foundation.",
        "acquaintance": "We've had a few meaningful exchanges. I'm learning about what matters to you.",
        "familiar": "We've developed a comfortable rapport. I've begun to understand your unique perspective.",
        "close": "We've shared deeper conversations and built a meaningful connection over time.",
        "trusted": "We've developed a significant level of trust through our many conversations.",
        "intimate": "We've built a deep connection with substantial emotional understanding and trust."
    }
    
    print(f"{Fore.CYAN}Relationship Stage:{Style.RESET_ALL} {relationship_stage.title()}")
    print(f"{Fore.CYAN}Stage Description:{Style.RESET_ALL} {stage_descriptions.get(relationship_stage, '')}")
    print()
    
    # Get conversation metrics from memory system
    metrics = elysia.get_conversation_metrics(user_id)
    
    # Show metrics if available
    if metrics:
        print(f"{Fore.CYAN}Conversation Stats:{Style.RESET_ALL}")
        print(f"Total Messages: {metrics.get('total_messages', 0)}")
        print(f"Session Count: {metrics.get('session_count', 1)}")
        print(f"Current Streak: {metrics.get('streak_days', 0)} days")
        print()
    
    input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
    clear_screen()

def show_config(elysia):
    """Display the current configuration"""
    clear_screen()
    print(f"{Fore.MAGENTA}======== Elysia Configuration ========{Style.RESET_ALL}")
    print(f"{Fore.CYAN}Storage Settings:{Style.RESET_ALL}")
    print(f"Type: {elysia.config['storage']['type']}")
    print(f"Path: {elysia.config['storage']['path']}")
    print(f"Message History Limit: {elysia.config['storage']['message_history_limit']}")
    
    print()
    print(f"{Fore.CYAN}Security Settings:{Style.RESET_ALL}")
    print(f"Encryption Enabled: {elysia.config['security']['encryption_enabled']}")
    print(f"Encryption Key Set: {'Yes' if elysia.config['security']['encryption_key'] else 'No'}")
    
    print()
    print(f"{Fore.CYAN}API Settings:{Style.RESET_ALL}")
    print(f"API Enabled: {elysia.config['api']['enabled']}")
    print(f"Model: {elysia.config['api']['model'] or 'Not set'}")
    print(f"API Key: {'Set' if elysia.config['api']['api_key'] else 'Not set'}")
    
    print()
    input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
    clear_screen()

def simulate_memory_creation(elysia, user_id, user_name):
    """Simulate memory creation for demonstration purposes"""
    # Only do this for new users
    user_profile = elysia.get_user_profile(user_id)
    if user_profile and user_profile.get("interests"):
        return
    
    # Initialize basic user profile with name and creation time
    elysia.update_user_profile(user_id, {
        "name": user_name,
        "created_at": datetime.now().isoformat(),
        "personality_traits": {
            "empathy": 0.9,
            "supportive": 0.9,
            "warmth": 0.8,
            "humor": 0.5,
            "formality": 0.3
        },
        "preferences": {
            "conversation_style": "supportive",
            "response_length": "medium"
        }
    })
    
    # Add sample interests
    sample_interests = ["reading", "music", "technology", "nature", "art", "gaming", "cooking", "travel"]
    interests = random.sample(sample_interests, 3)
    elysia.update_user_profile(user_id, {"interests": interests})
    
    # Store initial facts about the user
    for interest in interests:
        elysia.store_user_fact(user_id, "interest", f"You enjoy {interest}")
    
    # Store first meeting memory
    elysia.store_permanent_memory(
        user_id,
        f"First conversation with {user_name}. They enjoy {', '.join(interests[:-1])} and {interests[-1]}.",
        "first_meeting"
    )

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Elysia Chatbot')
    
    # Storage arguments
    parser.add_argument('--data-path', help='Path to store user data')
    
    # Security arguments
    parser.add_argument('--enable-encryption', action='store_true', 
                        help='Enable encryption for sensitive data')
    parser.add_argument('--encryption-key', help='Key for encrypting sensitive data')
    
    # Other settings
    parser.add_argument('--message-limit', type=int, help='Maximum message history to store')
    
    return parser.parse_args()

def create_config_from_args(args):
    """Create config dictionary from command line arguments"""
    config = DEFAULT_CONFIG.copy()
    
    # Update storage settings
    if args.data_path:
        config["storage"]["path"] = args.data_path
    if args.message_limit:
        config["storage"]["message_history_limit"] = args.message_limit
    
    # Update security settings
    if args.enable_encryption:
        config["security"]["encryption_enabled"] = True
    if args.encryption_key:
        config["security"]["encryption_key"] = args.encryption_key
    
    return config

def main():
    """Main function to run the Elysia chatbot"""
    # Parse command line arguments
    args = parse_arguments()
    config = create_config_from_args(args)
    
    # If encryption is enabled but no key provided, prompt for one
    if config["security"]["encryption_enabled"] and not config["security"]["encryption_key"]:
        print(f"{Fore.YELLOW}Encryption is enabled. Please provide an encryption key.{Style.RESET_ALL}")
        encryption_key = getpass.getpass("Encryption key: ")
        if encryption_key:
            config["security"]["encryption_key"] = encryption_key
        else:
            print(f"{Fore.RED}No encryption key provided. Disabling encryption.{Style.RESET_ALL}")
            config["security"]["encryption_enabled"] = False
    
    # Clear the screen and show welcome message
    clear_screen()
    print(f"{Fore.MAGENTA}======== Welcome to Elysia ========{Style.RESET_ALL}")
    print(format_system_message("Elysia is your emotionally intelligent AI companion."))
    print(format_system_message("Features:"))
    print(format_system_message("- Emotional understanding and adaptive responses"))
    print(format_system_message("- Memory of your conversations and important information"))
    print(format_system_message("- Relationship that evolves over time"))
    print(format_system_message("- Awareness of conversation depth and emotional patterns"))
    print(format_system_message("Type !help for available commands"))
    print()
    
    # Initialize the chatbot with the configuration
    elysia = ElysiaChatbot(config)
    
    # Get user's name
    user_name = input(f"{Fore.YELLOW}What's your name? {Style.RESET_ALL}")
    user_id = f"user_{user_name.lower().replace(' ', '_')}"
    
    # Simulate memory creation for demo
    simulate_memory_creation(elysia, user_id, user_name)
    
    # Get personalized greeting
    greeting = elysia.get_greeting(user_id)
    print()
    print(format_elysia_message(f"{greeting} {user_name}! How are you today?"))
    
    # Main conversation loop
    conversation_active = True
    while conversation_active:
        # Get user input
        user_input = input(f"{Fore.GREEN}{user_name}: {Style.RESET_ALL}")

        # Handle empty input
        if not user_input.strip():
            continue

        # Handle commands
        if user_input.startswith("!"):
            command = user_input[1:].lower()

            if command == "exit":
                print(format_elysia_message(f"Goodbye, {user_name}! I'll remember our conversation. Come back soon!"))
                conversation_active = False
                continue
            elif command == "help":
                show_help()
                continue
            elif command == "clear":
                clear_screen()
                continue
            elif command == "stats":
                show_relationship_stats(elysia, user_id, user_name)
                continue
            elif command == "time":
                current_time = time.strftime("%H:%M:%S")
                print(format_system_message(f"Current time: {current_time}"))
                continue
            elif command == "config":
                show_config(elysia)
                continue
            elif command == "memory":
                messages = elysia.get_recent_messages(user_id, 10)
                print(format_system_message("Recent Conversation:"))
                for msg in messages:
                    if msg["is_user"]:
                        print(format_user_message(user_name, msg["content"]))
                    else:
                        print(format_elysia_message(msg["content"]))
                continue
            elif command.startswith("remember "):
                memory_content = user_input[10:].strip()
                if memory_content:
                    if elysia.store_permanent_memory(user_id, memory_content):
                        print(format_system_message("Memory stored successfully!"))
                    else:
                        print(format_system_message("Failed to store memory. Please try again."))
                else:
                    print(format_system_message("Please provide something to remember. Usage: !remember [your memory]"))
                continue
            
        # Process regular input and get response
        response = elysia.process_user_message(user_id, user_input)
        print(format_elysia_message(response))

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nGoodbye!")
    except Exception as e:
        print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")


