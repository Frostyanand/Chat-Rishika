"""Base class for memory stores"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class MemoryStore(ABC):
    """Abstract base class for all memory store implementations"""
    
    def __init__(self, message_history_limit: int = 50):
        self.message_history_limit = message_history_limit
    
    @abstractmethod
    def initialize(self, **kwargs) -> None:
        """Initialize the memory store"""
        pass
    
    @abstractmethod
    def store_message(self, user_id: str, message: str, is_user: bool = True) -> bool:
        """Store a message in the conversation history"""
        pass
    
    @abstractmethod
    def get_recent_messages(self, user_id: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get recent messages from conversation history"""
        pass
    
    @abstractmethod
    def store_user_profile(self, user_id: str, profile_data: Dict[str, Any]) -> bool:
        """Store user profile data"""
        pass
    
    @abstractmethod
    def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user profile data"""
        pass
    
    @abstractmethod
    def store_user_fact(self, user_id: str, fact_type: str, fact: str) -> bool:
        """Store a fact about the user"""
        pass
    
    @abstractmethod
    def get_user_facts(self, user_id: str, fact_type: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]:
        """Get facts about the user"""
        pass
    
    @abstractmethod
    def store_permanent_memory(self, user_id: str, memory_content: str, memory_type: str = "general") -> bool:
        """Store a permanent memory"""
        pass
    
    @abstractmethod
    def get_permanent_memories(self, user_id: str, memory_type: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]:
        """Get permanent memories"""
        pass
    
    @abstractmethod
    def store_extracted_context(self, user_id: str, context_data: Dict[str, Any]) -> bool:
        """Store extracted context from conversation"""
        pass
    
    @abstractmethod
    def get_relevant_context(self, user_id: str, query: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get relevant context for current conversation"""
        pass
    
    @abstractmethod
    def get_conversation_metrics(self, user_id: str) -> Dict[str, Any]:
        """Get conversation metrics"""
        pass
    
    @abstractmethod
    def update_conversation_metrics(self, user_id: str, metrics_data: Dict[str, Any]) -> bool:
        """Update conversation metrics"""
        pass
    
    @abstractmethod
    def clear_user_data(self, user_id: str) -> bool:
        """Clear all data for a user"""
        pass