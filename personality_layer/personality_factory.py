from .base_personality import BasePersonality
from .response_templates.user_based_responses import UserBasedResponses
import json
import os
import datetime
import random

class PersonalityResponseFactory:
    def __init__(self, base_traits=None, user_data_path=None):
        """Initialize the personality factory with base traits and user data path"""
        self.base_traits = base_traits or {
            "formality": 0.3,
            "empathy": 0.9,
            "humor": 0.5
        }
        
        self.user_data_path = user_data_path or "user_data"
        
        # Create user data directory if it doesn't exist
        if not os.path.exists(self.user_data_path):
            os.makedirs(self.user_data_path)
        
        self.personalities = {}  # Cache of created personalities
        
        # Create stub for personality_adaptation (will be set properly later)
        self.personality_adaptation = None
    
    def get_personality(self, user_id, refresh=False):
        """Get a personality for a specific user, optionally refresh from storage"""
        if user_id in self.personalities and not refresh:
            return self.personalities[user_id]
            
        # Create or load user data
        user_data = self._load_user_data(user_id)
        
        # Create a base personality with the user's preferred name
        personality_name = user_data.get("companion_name", "Elysia")
        personality = BasePersonality(name=personality_name)
        
        # Set personality_factory reference to self
        personality.personality_factory = self
        
        # Apply user preferences to personality traits if available
        if "personality_traits" in user_data:
            personality.adapt_to_user(user_data["personality_traits"])
            
        # Add user data to the personality for reference
        personality.user_data = user_data
        
        # Create user-based response handler
        personality.user_responses = UserBasedResponses(user_data)
        
        # Store in cache
        self.personalities[user_id] = personality
        return personality
    
    def _load_user_data(self, user_id):
        """Load user data from storage"""
        user_file = os.path.join(self.user_data_path, f"{user_id}.json")
        
        if os.path.exists(user_file):
            try:
                with open(user_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading user data: {e}")
                return self._create_default_user_data(user_id)
        else:
            return self._create_default_user_data(user_id)
    
    def _create_default_user_data(self, user_id):
        """Create default user data for a new user"""
        default_data = {
            "user_id": user_id,
            "name": "there",  # Default until user provides a name
            "companion_name": "Elysia",
            "created_at": datetime.datetime.now().isoformat(),
            "personality_traits": {
                "empathy": 0.9,
                "supportive": 0.9,
                "warmth": 0.8,
                "humor": 0.5,
                "formality": 0.3
            },
            "interests": [],
            "important_dates": {},
            "preferences": {
                "conversation_style": "supportive",
                "response_length": "medium"
            },
            "memory": {
                "short_term": [],
                "long_term": {}
            }
        }
        
        # Save default data to file
        self._save_user_data(user_id, default_data)
        return default_data
    
    def _save_user_data(self, user_id, user_data):
        """Save user data to storage"""
        user_file = os.path.join(self.user_data_path, f"{user_id}.json")
        
        try:
            with open(user_file, 'w') as f:
                json.dump(user_data, f, indent=2)
        except Exception as e:
            print(f"Error saving user data: {e}")
    
    def update_user_data(self, user_id, updates):
        """Update user data with new information"""
        # Load current data
        user_data = self._load_user_data(user_id)
        
        # Apply updates (deep merge)
        self._deep_update(user_data, updates)
        
        # Save updated data
        self._save_user_data(user_id, user_data)
        
        # Refresh personality if it exists in cache
        if user_id in self.personalities:
            self.personalities[user_id] = self.get_personality(user_id, refresh=True)
    
    def _deep_update(self, original, updates):
        """Deep update a nested dictionary"""
        for key, value in updates.items():
            if key in original and isinstance(original[key], dict) and isinstance(value, dict):
                self._deep_update(original[key], value)
            else:
                original[key] = value
    
    def add_to_short_term_memory(self, user_id, message, is_user=True):
        """Add a message to the user's short-term memory"""
        user_data = self._load_user_data(user_id)
        
        # Initialize if not present
        if "memory" not in user_data:
            user_data["memory"] = {"short_term": [], "long_term": {}}
        
        # Add message with metadata
        user_data["memory"]["short_term"].append({
            "content": message,
            "timestamp": datetime.datetime.now().isoformat(),
            "is_user": is_user
        })
        
        # Limit to last 100 messages
        if len(user_data["memory"]["short_term"]) > 100:
            user_data["memory"]["short_term"] = user_data["memory"]["short_term"][-100:]
        
        # Save updated data
        self._save_user_data(user_id, user_data)
    
    def add_to_long_term_memory(self, user_id, key, value):
        """Add or update a key-value pair in long-term memory"""
        user_data = self._load_user_data(user_id)
        
        # Initialize if not present
        if "memory" not in user_data:
            user_data["memory"] = {"short_term": [], "long_term": {}}
        
        # Add with timestamp
        user_data["memory"]["long_term"][key] = {
            "value": value,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        # Save updated data
        self._save_user_data(user_id, user_data)
        
    def generate_response(self, user_id, message, relationship_stage="new"):
        """Generate a response for a user message"""
        # Get the personality
        personality = self.get_personality(user_id)
        
        # Ensure personality_factory is set
        if not hasattr(personality, 'personality_factory') or not personality.personality_factory:
            personality.personality_factory = self
        
        # Add message to short-term memory
        self.add_to_short_term_memory(user_id, message, is_user=True)
        
        # Get user data
        user_data = personality.user_data
        if user_data:
            user_data["user_id"] = user_id
            user_data["relationship_stage"] = relationship_stage
        
        try:
            # Check for emotional distress including loneliness
            user_mood = personality.detect_mood(message)
            if user_mood in ["depressed", "sad", "anxious", "overwhelmed", "lonely"]:
                # Get appropriate comfort phrase
                comfort_response = personality.phrase_bank.get_comfort_phrase(user_mood)
                
                # Add empathetic follow-up
                if random.random() < 0.7:  # 70% chance
                    follow_up = personality.phrase_bank.get_phrase("empathy")
                    comfort_response = f"{comfort_response} {follow_up}"
                
                # Add validation for emotional support
                if random.random() < 0.5:  # 50% chance
                    validation = personality.phrase_bank.get_phrase("validation")
                    comfort_response = f"{comfort_response} {validation}"
                
                response = comfort_response
            else:
                # Generate normal response using the personality
                response = personality.generate_response(message, user_data)
            
            return response
            
        except Exception as e:
            # Fallback response if an error occurs
            print(f"Error generating response: {e}")
            return "I'm here to chat with you. How can I help you today?"
    
    # Memory system methods
    def add_user_interest(self, user_id, interest):
        """Add a user interest to their profile."""
        user_data = self._load_user_data(user_id)
        
        # Initialize interests if not present
        if "interests" not in user_data:
            user_data["interests"] = []
            
        # Avoid duplicates
        if interest not in user_data["interests"]:
            user_data["interests"].append(interest)
            
        # Save updated user data
        self._save_user_data(user_id, user_data)
        
    def add_important_date(self, user_id, date_str, description):
        """Add an important date to user profile."""
        user_data = self._load_user_data(user_id)
        
        # Initialize important_dates if not present
        if "important_dates" not in user_data:
            user_data["important_dates"] = {}
            
        # Add or update the date
        user_data["important_dates"][description] = date_str
            
        # Save updated user data
        self._save_user_data(user_id, user_data)
        
    def add_user_fact(self, user_id, fact_category, fact_value):
        """Add a fact about the user to their profile."""
        user_data = self._load_user_data(user_id)
        
        # Initialize personal_facts if not present
        if "personal_facts" not in user_data:
            user_data["personal_facts"] = {}
            
        # Add or update the fact
        user_data["personal_facts"][fact_category] = fact_value
            
        # Save updated user data
        self._save_user_data(user_id, user_data)
        
    def get_user_interests(self, user_id):
        """Get the user's interests."""
        user_data = self._load_user_data(user_id)
        return user_data.get("interests", [])
        
    def get_important_dates(self, user_id):
        """Get the user's important dates."""
        user_data = self._load_user_data(user_id)
        return user_data.get("important_dates", {})
        
    def get_personal_facts(self, user_id):
        """Get facts about the user."""
        user_data = self._load_user_data(user_id)
        return user_data.get("personal_facts", {})
        
    def get_relevant_memories(self, user_id, context):
        """Get memories relevant to the current conversation context."""
        # This is a simple implementation that could be enhanced with more sophisticated retrieval
        user_data = self._load_user_data(user_id)
        relevant_memories = {
            "interests": [],
            "important_dates": {},
            "personal_facts": {}
        }
        
        # Look for interests mentioned in context
        interests = self.get_user_interests(user_id)
        for interest in interests:
            if interest.lower() in context.lower():
                relevant_memories["interests"].append(interest)
                
        # Look for date-related keywords in context
        important_dates = self.get_important_dates(user_id)
        date_keywords = ["birthday", "anniversary", "holiday", "event", "date", "celebration", "remember"]
        
        if any(keyword in context.lower() for keyword in date_keywords):
            relevant_memories["important_dates"] = important_dates
        else:
            # Check for specific important dates mentioned
            for description, date_str in important_dates.items():
                if description.lower() in context.lower():
                    relevant_memories["important_dates"][description] = date_str
        
        # Look for personal fact keywords in context
        personal_facts = self.get_personal_facts(user_id)
        for category, value in personal_facts.items():
            if category.lower() in context.lower():
                relevant_memories["personal_facts"][category] = value
                
        return relevant_memories
        
    def update_user_name(self, user_id, name):
        """Update the user's name."""
        user_data = self._load_user_data(user_id)
        
        # Initialize profile if not present
        if "profile" not in user_data:
            user_data["profile"] = {}
            
        user_data["profile"]["name"] = name
        
        # Save updated user data
        self._save_user_data(user_id, user_data)
        
    def get_user_name(self, user_id):
        """Get the user's name."""
        user_data = self._load_user_data(user_id)
        return user_data.get("profile", {}).get("name", "User")