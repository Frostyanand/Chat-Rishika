"""
JSON-based implementation of the memory store.
"""
import os
import json
import re
import html
from datetime import datetime, timedelta
import shutil
import logging
from typing import Dict, Any, List, Optional, Union
from .memory_store import MemoryStore

logger = logging.getLogger(__name__)

class JsonMemoryStore(MemoryStore):
    """
    JSON implementation of the memory store. 
    Stores user data in JSON files within a directory structure.
    """
    
    def __init__(self, message_history_limit=100):
        """
        Initialize the JSON memory store.
        
        Args:
            message_history_limit (int): Maximum number of messages to store per user
        """
        self.user_data_path = None
        self.message_history_limit = message_history_limit
        logger.info("JsonMemoryStore initialized with message_history_limit=%d", message_history_limit)
    
    def initialize(self, user_data_path="./user_data"):
        """
        Initialize the memory store with configuration settings.
        
        Args:
            user_data_path (str): Path to store user data
        """
        self.user_data_path = user_data_path
        os.makedirs(user_data_path, exist_ok=True)
        logger.info("JsonMemoryStore initialized with user_data_path=%s", user_data_path)
        
        # Create a users index file if it doesn't exist
        users_index_path = os.path.join(user_data_path, "users_index.json")
        if not os.path.exists(users_index_path):
            self._write_json_file(users_index_path, {"users": []})
            
        return True
    
    def cleanup(self):
        """Clean up any resources"""
        # Nothing specific to clean up for JSON storage
        pass
    
    def _sanitize_user_id(self, user_id):
        """
        Sanitize user ID to prevent injection attacks
        
        Args:
            user_id (str): User ID to sanitize
            
        Returns:
            str: Sanitized user ID
        """
        if not isinstance(user_id, str):
            raise ValueError("User ID must be a string")
            
        # Strip and limit to alphanumeric, underscore, and hyphen
        # This prevents path traversal attacks and other injection types
        sanitized = re.sub(r'[^a-zA-Z0-9_\-]', '', user_id.strip())
        
        # Ensure we have a valid ID after sanitization
        if not sanitized:
            raise ValueError("User ID contains no valid characters")
            
        return sanitized
    
    def _sanitize_string(self, text):
        """
        Sanitize a string to prevent injection attacks
        
        Args:
            text (str): Text to sanitize
            
        Returns:
            str: Sanitized text
        """
        if text is None:
            return None
            
        if not isinstance(text, str):
            text = str(text)
            
        # Remove any potentially dangerous HTML/script tags
        # This is a basic implementation - in production, consider using a library
        # like bleach for more thorough sanitization
        sanitized = re.sub(r'<[^>]*>', '', text)
        
        return sanitized
    
    def _sanitize_dict(self, data):
        """
        Recursively sanitize all string values in a dictionary
        
        Args:
            data (dict): Dictionary to sanitize
            
        Returns:
            dict: Sanitized dictionary
        """
        if not isinstance(data, dict):
            return data
            
        result = {}
        for key, value in data.items():
            safe_key = self._sanitize_string(key)
            
            if isinstance(value, dict):
                result[safe_key] = self._sanitize_dict(value)
            elif isinstance(value, list):
                result[safe_key] = [
                    self._sanitize_dict(item) if isinstance(item, dict) 
                    else self._sanitize_string(item) if isinstance(item, str)
                    else item
                    for item in value
                ]
            elif isinstance(value, str):
                result[safe_key] = self._sanitize_string(value)
            else:
                result[safe_key] = value
                
        return result
    
    def create_user(self, user_id, initial_data=None):
        """
        Create a new user in the memory store.
        
        Args:
            user_id (str): Unique identifier for the user
            initial_data (dict, optional): Initial profile data for the user
            
        Returns:
            bool: True if successful, False if user already exists or error
        """
        try:
            # Sanitize user ID
            safe_user_id = self._sanitize_user_id(user_id)
            
            # Check if users index exists
            users_index_path = os.path.join(self.user_data_path, "users_index.json")
            users_index = self._read_json_file(users_index_path, {"users": []})
            
            # Check if user already exists
            if safe_user_id in users_index.get("users", []):
                logger.warning(f"User {safe_user_id} already exists")
                return False  # User already exists
            
            # Create user directory
            user_dir = self._get_user_dir(safe_user_id)
            
            # Sanitize initial data
            safe_initial_data = self._sanitize_dict(initial_data) if initial_data else {"created_at": datetime.now().isoformat()}
            
            # Initialize basic files
            self._write_json_file(self._get_file_path(safe_user_id, "user_profile.json"), 
                                 safe_initial_data)
            self._write_json_file(self._get_file_path(safe_user_id, "conversation_history.json"), 
                                 {"messages": []})
            self._write_json_file(self._get_file_path(safe_user_id, "user_facts.json"), 
                                 {"categories": {}})
            self._write_json_file(self._get_file_path(safe_user_id, "interaction_metrics.json"), 
                                 {"message_count": 0, "total_words": 0, 
                                  "first_interaction": datetime.now().isoformat()})
            self._write_json_file(self._get_file_path(safe_user_id, "permanent_memories.json"),
                                 {"memories": {}})
            
            # Add user to index
            users_index["users"].append(safe_user_id)
            users_index["users"] = sorted(users_index["users"])
            self._write_json_file(users_index_path, users_index)
            
            logger.info(f"Created user {safe_user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            return False
        
    def get_all_users(self):
        """
        Get a list of all user IDs in the memory store.
        
        Returns:
            list: List of user IDs
        """
        users_index_path = os.path.join(self.user_data_path, "users_index.json")
        users_index = self._read_json_file(users_index_path, {"users": []})
        return users_index.get("users", [])
    
    def _get_user_dir(self, user_id):
        """Get the directory for a specific user's data."""
        safe_user_id = self._sanitize_user_id(user_id)
        user_dir = os.path.join(self.user_data_path, safe_user_id)
        os.makedirs(user_dir, exist_ok=True)
        return user_dir
    
    def _get_file_path(self, user_id, file_name):
        """Get the full path to a user's data file."""
        safe_user_id = self._sanitize_user_id(user_id)
        # Prevent path traversal in file_name
        safe_file_name = os.path.basename(file_name)
        return os.path.join(self._get_user_dir(safe_user_id), safe_file_name)
    
    def _read_json_file(self, file_path, default=None):
        """Read data from a JSON file with error handling."""
        if default is None:
            default = {}
        
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return default
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON format in file {file_path}")
            return default
        except Exception as e:
            logger.error(f"Error reading JSON file {file_path}: {e}")
            return default
    
    def _write_json_file(self, file_path, data):
        """Write data to a JSON file with error handling."""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Write to a temporary file first to avoid corruption
            temp_file = f"{file_path}.tmp"
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            # Replace the original file with the temporary one
            if os.path.exists(file_path):
                os.replace(temp_file, file_path)
            else:
                os.rename(temp_file, file_path)
                
            return True
        except Exception as e:
            logger.error(f"Error writing JSON file {file_path}: {e}")
            return False
    
    def store_message(self, user_id, message, is_user=True, timestamp=None, metadata=None):
        """
        Store a message in the user's conversation history.
        
        Args:
            user_id (str): Unique identifier for the user
            message (str): The message content
            is_user (bool): Whether the message is from the user (True) or Elysia (False)
            timestamp (str, optional): ISO format timestamp
            metadata (dict, optional): Additional metadata about the message
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Sanitize inputs
            safe_user_id = self._sanitize_user_id(user_id)
            safe_message = self._sanitize_string(message)
            
            if not timestamp:
                timestamp = datetime.now().isoformat()
            
            if not metadata:
                metadata = {}
            else:
                metadata = self._sanitize_dict(metadata)
            
            # Prepare message entry
            message_entry = {
                "content": safe_message,
                "timestamp": timestamp,
                "is_user": bool(is_user),
                "metadata": metadata
            }
            
            # Calculate message details for metrics
            word_count = len(safe_message.split())
            message_entry["word_count"] = word_count
            
            # Create user if not exists
            if not self.user_exists(safe_user_id):
                self.create_user(safe_user_id)
            
            # Update conversation history
            history_file = self._get_file_path(safe_user_id, "conversation_history.json")
            conversation_history = self._read_json_file(history_file, {"messages": []})
            
            # Add new message
            conversation_history["messages"].append(message_entry)
            
            # Trim to the message history limit
            if len(conversation_history["messages"]) > self.message_history_limit:
                conversation_history["messages"] = conversation_history["messages"][-self.message_history_limit:]
            
            # Update metrics
            self._update_message_metrics(safe_user_id, message_entry)
            
            # Save updated history
            success = self._write_json_file(history_file, conversation_history)
            if success:
                logger.info(f"Stored message for user {safe_user_id}")
            return success
            
        except Exception as e:
            logger.error(f"Error storing message: {str(e)}")
            return False
            
    def _update_message_metrics(self, user_id, message_entry):
        """Update metrics based on a new message."""
        try:
            metrics_file = self._get_file_path(user_id, "interaction_metrics.json")
            metrics = self._read_json_file(metrics_file, {
                "message_count": 0,
                "total_words": 0,
                "first_interaction": None,
                "last_interaction": None,
                "interaction_dates": []
            })
            
            # Update basic counts
            metrics["message_count"] = metrics.get("message_count", 0) + 1
            metrics["total_words"] = metrics.get("total_words", 0) + message_entry.get("word_count", 0)
            
            # Update timestamps
            current_time = message_entry.get("timestamp", datetime.now().isoformat())
            if not metrics.get("first_interaction"):
                metrics["first_interaction"] = current_time
            metrics["last_interaction"] = current_time
            
            # Update interaction dates (for streak tracking)
            current_date = current_time.split("T")[0]  # Get just the date part
            interaction_dates = metrics.get("interaction_dates", [])
            if current_date not in interaction_dates:
                interaction_dates.append(current_date)
                metrics["interaction_dates"] = sorted(interaction_dates)
            
            # Calculate streak
            if message_entry.get("is_user", False):
                self.update_streak(user_id)
            
            # Save updated metrics
            return self._write_json_file(metrics_file, metrics)
            
        except Exception as e:
            logger.error(f"Error updating metrics: {str(e)}")
            return False
    
    def get_recent_messages(self, user_id, limit=None):
        """
        Get recent messages for a user.
        
        Args:
            user_id (str): User ID
            limit (int, optional): Maximum number of messages to return
            
        Returns:
            list: List of message dictionaries
        """
        try:
            safe_user_id = self._sanitize_user_id(user_id)
            
            # Check if user exists
            if not self.user_exists(safe_user_id):
                return []
                
            history_file = self._get_file_path(safe_user_id, "conversation_history.json")
            conversation_history = self._read_json_file(history_file, {"messages": []})
            
            messages = conversation_history.get("messages", [])
            
            # Apply limit if provided
            if limit and isinstance(limit, int) and limit > 0:
                messages = messages[-limit:]
                
            return messages
            
        except Exception as e:
            logger.error(f"Error getting recent messages: {str(e)}")
            return []
    
    def store_user_profile(self, user_id, profile_data):
        """
        Store or update a user's profile.
        
        Args:
            user_id (str): User ID
            profile_data (dict): Profile data to store
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            safe_user_id = self._sanitize_user_id(user_id)
            safe_profile_data = self._sanitize_dict(profile_data)
            
            # Create user if not exists
            if not self.user_exists(safe_user_id):
                self.create_user(safe_user_id)
            
            # Write profile data
            profile_file = self._get_file_path(safe_user_id, "user_profile.json")
            
            # Read existing profile to update it
            existing_profile = self._read_json_file(profile_file, {})
            
            # Update profile (deep merge)
            updated_profile = self._deep_update(existing_profile, safe_profile_data)
            
            success = self._write_json_file(profile_file, updated_profile)
            if success:
                logger.info(f"Updated profile for user {safe_user_id}")
            return success
            
        except Exception as e:
            logger.error(f"Error storing user profile: {str(e)}")
            return False
    
    def update_user_profile(self, user_id, profile_data):
        """
        Update specific fields in a user's profile.
        
        Args:
            user_id (str): User ID
            profile_data (dict): Profile data to update
            
        Returns:
            bool: True if successful, False otherwise
        """
        return self.store_user_profile(user_id, profile_data)
    
    def _deep_update(self, target, source):
        """
        Deep update a nested dictionary.
        
        Args:
            target (dict): Dictionary to update
            source (dict): Dictionary with updates
            
        Returns:
            dict: Updated dictionary
        """
        if not isinstance(target, dict) or not isinstance(source, dict):
            return source if isinstance(source, dict) else target if isinstance(target, dict) else {}
            
        result = target.copy()
        for key, value in source.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_update(result[key], value)
            else:
                result[key] = value
        return result
    
    def get_user_profile(self, user_id):
        """
        Get a user's profile.
        
        Args:
            user_id (str): User ID
            
        Returns:
            dict: User profile data or empty dict if not found
        """
        try:
            safe_user_id = self._sanitize_user_id(user_id)
            
            # Check if user exists
            if not self.user_exists(safe_user_id):
                return {}
                
            profile_file = self._get_file_path(safe_user_id, "user_profile.json")
            return self._read_json_file(profile_file, {})
            
        except Exception as e:
            logger.error(f"Error getting user profile: {str(e)}")
            return {}
    
    def store_user_fact(self, user_id, fact_type, fact_value):
        """
        Store a fact about a user.
        
        Args:
            user_id (str): User ID
            fact_type (str): Type/category of fact
            fact_value (str): The fact to store
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            safe_user_id = self._sanitize_user_id(user_id)
            safe_fact_type = self._sanitize_string(fact_type)
            safe_fact_value = self._sanitize_string(fact_value)
            
            # Create user if not exists
            if not self.user_exists(safe_user_id):
                self.create_user(safe_user_id)
            
            facts_file = self._get_file_path(safe_user_id, "user_facts.json")
            facts = self._read_json_file(facts_file, {"categories": {}})
            
            # Initialize category if it doesn't exist
            if safe_fact_type not in facts.get("categories", {}):
                facts.setdefault("categories", {})[safe_fact_type] = []
            
            # Add fact if it doesn't exist already
            if safe_fact_value not in facts["categories"][safe_fact_type]:
                facts["categories"][safe_fact_type].append(safe_fact_value)
            
            # Add timestamp to mark when fact was added/updated
            facts["last_updated"] = datetime.now().isoformat()
            
            success = self._write_json_file(facts_file, facts)
            if success:
                logger.info(f"Stored fact for user {safe_user_id}: {safe_fact_type} - {safe_fact_value}")
            return success
            
        except Exception as e:
            logger.error(f"Error storing user fact: {str(e)}")
            return False
    
    def get_user_facts(self, user_id, fact_type=None):
        """
        Get facts about a user.
        
        Args:
            user_id (str): User ID
            fact_type (str, optional): Type of facts to retrieve
            
        Returns:
            dict: Facts organized by category or list if fact_type is specified
        """
        try:
            safe_user_id = self._sanitize_user_id(user_id)
            
            # Check if user exists
            if not self.user_exists(safe_user_id):
                return {} if fact_type is None else []
            
            facts_file = self._get_file_path(safe_user_id, "user_facts.json")
            facts = self._read_json_file(facts_file, {"categories": {}})
            
            # Return specific fact type if requested
            if fact_type:
                safe_fact_type = self._sanitize_string(fact_type)
                return facts.get("categories", {}).get(safe_fact_type, [])
            
            # Return all facts organized by category
            return facts.get("categories", {})
            
        except Exception as e:
            logger.error(f"Error getting user facts: {str(e)}")
            return {} if fact_type is None else []
    
    def update_conversation_metrics(self, user_id, metrics_data):
        """
        Update conversation metrics.
        
        Args:
            user_id (str): User ID
            metrics_data (dict): Metrics data to update
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            safe_user_id = self._sanitize_user_id(user_id)
            safe_metrics_data = self._sanitize_dict(metrics_data)
            
            # Create user if not exists
            if not self.user_exists(safe_user_id):
                self.create_user(safe_user_id)
            
            metrics_file = self._get_file_path(safe_user_id, "interaction_metrics.json")
            metrics = self._read_json_file(metrics_file, {})
            
            # Update metrics with new data
            updated_metrics = self._deep_update(metrics, safe_metrics_data)
            
            success = self._write_json_file(metrics_file, updated_metrics)
            if success:
                logger.info(f"Updated conversation metrics for user {safe_user_id}")
            return success
            
        except Exception as e:
            logger.error(f"Error updating conversation metrics: {str(e)}")
            return False
    
    def get_conversation_metrics(self, user_id):
        """
        Get conversation metrics.
        
        Args:
            user_id (str): User ID
            
        Returns:
            dict: Conversation metrics
        """
        try:
            safe_user_id = self._sanitize_user_id(user_id)
            
            # Check if user exists
            if not self.user_exists(safe_user_id):
                return {}
            
            metrics_file = self._get_file_path(safe_user_id, "interaction_metrics.json")
            return self._read_json_file(metrics_file, {})
            
        except Exception as e:
            logger.error(f"Error getting conversation metrics: {str(e)}")
            return {}
    
    def store_extracted_context(self, user_id, context_data):
        """
        Store extracted context from conversation.
        
        Args:
            user_id (str): User ID
            context_data (dict): Extracted context data
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            safe_user_id = self._sanitize_user_id(user_id)
            safe_context_data = self._sanitize_dict(context_data)
            
            # Create user if not exists
            if not self.user_exists(safe_user_id):
                self.create_user(safe_user_id)
            
            # Store each context item as a fact
            for context_type, context_value in safe_context_data.items():
                if isinstance(context_value, str) and context_value.strip():
                    self.store_user_fact(safe_user_id, f"extracted_{context_type}", context_value)
            
            return True
            
        except Exception as e:
            logger.error(f"Error storing extracted context: {str(e)}")
            return False
    
    def get_relevant_context(self, user_id, query=None):
        """
        Get relevant context for a conversation.
        
        Args:
            user_id (str): User ID
            query (str, optional): Search query to filter relevant context
            
        Returns:
            list: List of relevant context items
        """
        try:
            safe_user_id = self._sanitize_user_id(user_id)
            
            # Check if user exists
            if not self.user_exists(safe_user_id):
                return []
            
            # Get user profile
            profile = self.get_user_profile(safe_user_id)
            
            # Get recent messages
            messages = self.get_recent_messages(safe_user_id, 5)  # Last 5 messages for context
            
            # Get facts
            facts = self.get_user_facts(safe_user_id)
            
            # Compile relevant context
            context = []
            
            # Add relevant profile information
            if profile:
                context.append({
                    "type": "profile",
                    "content": f"User name: {profile.get('name', 'Unknown')}",
                    "category": "identity"
                })
                
                # Add interests if available
                interests = profile.get("interests", [])
                if interests:
                    context.append({
                        "type": "profile",
                        "content": f"User interests: {', '.join(interests)}",
                        "category": "interests"
                    })
            
            # Add relevant facts as context
            for category, category_facts in facts.items():
                for fact in category_facts:
                    # Skip if fact is not relevant to query (if query provided)
                    if query and isinstance(query, str) and query.lower() not in fact.lower():
                        continue
                        
                    context.append({
                        "type": "fact",
                        "content": fact,
                        "category": category
                    })
            
            # Add recent messages for conversation context
            for msg in messages:
                context.append({
                    "type": "message",
                    "content": msg.get("content", ""),
                    "is_user": msg.get("is_user", True),
                    "timestamp": msg.get("timestamp", "")
                })
            
            return context
            
        except Exception as e:
            logger.error(f"Error getting relevant context: {str(e)}")
            return []
    
    def clear_user_data(self, user_id):
        """
        Clear all data for a user.
        
        Args:
            user_id (str): User ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            safe_user_id = self._sanitize_user_id(user_id)
            
            # Check if user exists
            if not self.user_exists(safe_user_id):
                return False
            
            user_dir = self._get_user_dir(safe_user_id)
            
            # Remove user's directory
            if os.path.exists(user_dir):
                shutil.rmtree(user_dir)
            
            # Remove user from index
            users_index_path = os.path.join(self.user_data_path, "users_index.json")
            users_index = self._read_json_file(users_index_path, {"users": []})
            
            if safe_user_id in users_index.get("users", []):
                users_index["users"].remove(safe_user_id)
                self._write_json_file(users_index_path, users_index)
            
            logger.info(f"Cleared all data for user {safe_user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing user data: {str(e)}")
            return False
    
    def store_permanent_memory(self, user_id, memory_content, memory_type="general"):
        """
        Store a permanent memory for a user.
        
        Args:
            user_id (str): User ID
            memory_content (str): Memory content
            memory_type (str): Type of memory
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            safe_user_id = self._sanitize_user_id(user_id)
            safe_memory_content = self._sanitize_string(memory_content)
            safe_memory_type = self._sanitize_string(memory_type)
            
            # Create user if not exists
            if not self.user_exists(safe_user_id):
                self.create_user(safe_user_id)
            
            memories_file = self._get_file_path(safe_user_id, "permanent_memories.json")
            memories = self._read_json_file(memories_file, {"memories": {}})
            
            # Make sure memories section exists
            memories.setdefault("memories", {})
            
            # Make sure memory type section exists
            memories["memories"].setdefault(safe_memory_type, [])
            
            # Add the new memory with metadata
            memory_entry = {
                "content": safe_memory_content,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            memories["memories"][safe_memory_type].append(memory_entry)
            
            success = self._write_json_file(memories_file, memories)
            if success:
                logger.info(f"Stored permanent memory for user {safe_user_id}: {safe_memory_type}")
            return success
            
        except Exception as e:
            logger.error(f"Error storing permanent memory: {str(e)}")
            return False
    
    def get_permanent_memories(self, user_id, memory_type=None):
        """
        Get permanent memories for a user.
        
        Args:
            user_id (str): User ID
            memory_type (str, optional): Type of memories to get
            
        Returns:
            dict: Dictionary of memories by type, or list if memory_type specified
        """
        try:
            safe_user_id = self._sanitize_user_id(user_id)
            
            # Check if user exists
            if not self.user_exists(safe_user_id):
                return {} if memory_type is None else []
            
            memories_file = self._get_file_path(safe_user_id, "permanent_memories.json")
            memories = self._read_json_file(memories_file, {"memories": {}})
            
            # Return specific memory type if requested
            if memory_type:
                safe_memory_type = self._sanitize_string(memory_type)
                return memories.get("memories", {}).get(safe_memory_type, [])
            
            # Return all memories
            return memories.get("memories", {})
            
        except Exception as e:
            logger.error(f"Error getting permanent memories: {str(e)}")
            return {} if memory_type is None else []
    
    def update_permanent_memory(self, user_id, memory_index, memory_type, updates):
        """
        Update a permanent memory.
        
        Args:
            user_id (str): User ID
            memory_index (int): Index of memory to update
            memory_type (str): Type of memory
            updates (dict): Updates to apply to memory
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            safe_user_id = self._sanitize_user_id(user_id)
            safe_memory_type = self._sanitize_string(memory_type)
            safe_updates = self._sanitize_dict(updates)
            
            # Validate memory_index
            if not isinstance(memory_index, int) or memory_index < 0:
                return False
            
            # Check if user exists
            if not self.user_exists(safe_user_id):
                return False
            
            memories_file = self._get_file_path(safe_user_id, "permanent_memories.json")
            memories = self._read_json_file(memories_file, {"memories": {}})
            
            # Check if memory type and index exist
            if (safe_memory_type not in memories.get("memories", {}) or
                memory_index >= len(memories["memories"][safe_memory_type])):
                return False
            
            # Update the memory
            memory = memories["memories"][safe_memory_type][memory_index]
            if "content" in safe_updates:
                memory["content"] = safe_updates["content"]
            memory["updated_at"] = datetime.now().isoformat()
            
            success = self._write_json_file(memories_file, memories)
            if success:
                logger.info(f"Updated permanent memory for user {safe_user_id}: {safe_memory_type} at index {memory_index}")
            return success
            
        except Exception as e:
            logger.error(f"Error updating permanent memory: {str(e)}")
            return False
    
    def delete_permanent_memory(self, user_id, memory_index, memory_type):
        """
        Delete a permanent memory.
        
        Args:
            user_id (str): User ID
            memory_index (int): Index of memory to delete
            memory_type (str): Type of memory
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            safe_user_id = self._sanitize_user_id(user_id)
            safe_memory_type = self._sanitize_string(memory_type)
            
            # Validate memory_index
            if not isinstance(memory_index, int) or memory_index < 0:
                return False
            
            # Check if user exists
            if not self.user_exists(safe_user_id):
                return False
            
            memories_file = self._get_file_path(safe_user_id, "permanent_memories.json")
            memories = self._read_json_file(memories_file, {"memories": {}})
            
            # Check if memory type and index exist
            if (safe_memory_type not in memories.get("memories", {}) or
                memory_index >= len(memories["memories"][safe_memory_type])):
                return False
            
            # Delete the memory
            del memories["memories"][safe_memory_type][memory_index]
            
            # Clean up empty memory types
            if not memories["memories"][safe_memory_type]:
                del memories["memories"][safe_memory_type]
            
            success = self._write_json_file(memories_file, memories)
            if success:
                logger.info(f"Deleted permanent memory for user {safe_user_id}: {safe_memory_type} at index {memory_index}")
            return success
            
        except Exception as e:
            logger.error(f"Error deleting permanent memory: {str(e)}")
            return False

    def user_exists(self, user_id):
        """
        Check if a user exists.
        
        Args:
            user_id (str): User ID to check
            
        Returns:
            bool: True if user exists, False otherwise
        """
        try:
            safe_user_id = self._sanitize_user_id(user_id)
            
            # Check users index first (more efficient)
            users_index_path = os.path.join(self.user_data_path, "users_index.json")
            users_index = self._read_json_file(users_index_path, {"users": []})
            
            if safe_user_id in users_index.get("users", []):
                return True
            
            # Double-check if directory exists (in case index is out of sync)
            user_dir = os.path.join(self.user_data_path, safe_user_id)
            if os.path.exists(user_dir) and os.path.isdir(user_dir):
                # Update users index
                users_index["users"].append(safe_user_id)
                users_index["users"] = sorted(users_index["users"])
                self._write_json_file(users_index_path, users_index)
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"Error checking if user exists: {str(e)}")
            return False
    
    def update_streak(self, user_id):
        """
        Update a user's interaction streak.
        
        Args:
            user_id (str): User ID
            
        Returns:
            dict: Updated streak information
        """
        try:
            safe_user_id = self._sanitize_user_id(user_id)
            
            # Check if user exists
            if not self.user_exists(safe_user_id):
                return {}
            
            metrics_file = self._get_file_path(safe_user_id, "interaction_metrics.json")
            metrics = self._read_json_file(metrics_file, {
                "streak_days": 0,
                "longest_streak": 0,
                "last_interaction_date": None,
                "interaction_dates": []
            })
            
            today = datetime.now().date()
            today_str = today.isoformat()
            
            # Get last interaction date
            last_date_str = metrics.get("last_interaction_date")
            last_date = None
            
            if last_date_str:
                try:
                    last_date = datetime.fromisoformat(last_date_str).date()
                except (ValueError, TypeError):
                    last_date = None
            
            # Initialize dates if needed
            if "interaction_dates" not in metrics:
                metrics["interaction_dates"] = []
            
            # Add today if not already in the list
            if today_str not in metrics["interaction_dates"]:
                metrics["interaction_dates"].append(today_str)
                metrics["interaction_dates"] = sorted(metrics["interaction_dates"])
            
            # Calculate streak
            current_streak = metrics.get("streak_days", 0)
            new_streak = current_streak
            
            if not last_date:
                # First interaction
                new_streak = 1
                
            elif last_date == today:
                # Already counted today, no change
                pass
                
            elif last_date == today - timedelta(days=1):
                # Consecutive day, increment streak
                new_streak += 1
                
            else:
                # Streak broken, reset
                new_streak = 1
            
            # Update metrics
            metrics["streak_days"] = new_streak
            metrics["last_interaction_date"] = today_str
            
            # Update longest streak if needed
            longest_streak = metrics.get("longest_streak", 0)
            if new_streak > longest_streak:
                metrics["longest_streak"] = new_streak
            
            # Save updated metrics
            success = self._write_json_file(metrics_file, metrics)
            
            if success:
                logger.info(f"Updated streak for user {safe_user_id}: {new_streak} days")
                
            return {
                "current_streak": new_streak,
                "longest_streak": metrics["longest_streak"],
                "last_interaction": today_str
            }
            
        except Exception as e:
            logger.error(f"Error updating streak: {str(e)}")
            return {}
    
    def set_global_context(self, key, value):
        """
        Set a global context value.
        
        Args:
            key (str): Context key
            value (any): Context value (must be JSON serializable)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            safe_key = self._sanitize_string(key)
            
            # Handle different types of values
            if isinstance(value, dict):
                safe_value = self._sanitize_dict(value)
            elif isinstance(value, str):
                safe_value = self._sanitize_string(value)
            else:
                # For other JSON-serializable types
                safe_value = value
            
            # Store in global context file
            global_context_file = os.path.join(self.user_data_path, "global_context.json")
            context = self._read_json_file(global_context_file, {})
            
            # Update the context
            context[safe_key] = {
                "value": safe_value,
                "updated_at": datetime.now().isoformat()
            }
            
            success = self._write_json_file(global_context_file, context)
            if success:
                logger.info(f"Set global context: {safe_key}")
            return success
            
        except Exception as e:
            logger.error(f"Error setting global context: {str(e)}")
            return False
    
    def get_global_context(self, key):
        """
        Get a global context value.
        
        Args:
            key (str): Context key
            
        Returns:
            any: Context value or None if not found
        """
        try:
            safe_key = self._sanitize_string(key)
            
            global_context_file = os.path.join(self.user_data_path, "global_context.json")
            context = self._read_json_file(global_context_file, {})
            
            context_entry = context.get(safe_key)
            if context_entry and "value" in context_entry:
                return context_entry["value"]
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting global context: {str(e)}")
            return None
    
    def delete_global_context(self, key):
        """
        Delete a global context value.
        
        Args:
            key (str): Context key to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            safe_key = self._sanitize_string(key)
            
            global_context_file = os.path.join(self.user_data_path, "global_context.json")
            context = self._read_json_file(global_context_file, {})
            
            if safe_key in context:
                del context[safe_key]
                success = self._write_json_file(global_context_file, context)
                if success:
                    logger.info(f"Deleted global context: {safe_key}")
                return success
            
            return True  # Key doesn't exist, consider it deleted
            
        except Exception as e:
            logger.error(f"Error deleting global context: {str(e)}")
            return False

    def get_or_create_user(self, user_id, name=None):
        """
        Get a user by ID, creating them if they don't exist.
        
        Args:
            user_id (str): User ID
            name (str, optional): User's name for creating new profile
            
        Returns:
            dict: User profile data
        """
        try:
            safe_user_id = self._sanitize_user_id(user_id)
            
            # Try to get existing user
            profile = self.get_user_profile(safe_user_id)
            if profile:
                logger.info(f"Retrieved existing user: {safe_user_id}")
                return profile
                
            # Create new user if doesn't exist
            initial_data = {
                "created_at": datetime.now().isoformat(),
                "name": self._sanitize_string(name) if name else None
            }
            
            success = self.create_user(safe_user_id, initial_data)
            if success:
                logger.info(f"Created new user: {safe_user_id}")
                return self.get_user_profile(safe_user_id)
            
            logger.error(f"Failed to create user: {safe_user_id}")
            return {}
            
        except Exception as e:
            logger.error(f"Error in get_or_create_user: {str(e)}")
            return {}