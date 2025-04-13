"""Factory for creating memory store instances."""
import logging
from typing import Dict, Any

from .memory_store import MemoryStore
from .json_memory_store import JsonMemoryStore
from .config import get_config

logger = logging.getLogger(__name__)

def create_memory_store(**kwargs) -> MemoryStore:
    """Create and initialize JSON memory store based on configuration.
    
    Returns:
        MemoryStore: Configured JSON memory store instance
    """
    config = get_config()
    storage_config = kwargs.get('storage', {})
    
    # Create JSON store with appropriate message history limit
    json_store = JsonMemoryStore(
        message_history_limit=storage_config.get('message_history_limit', config.MAX_MESSAGES)
    )
    
    # Initialize the store with the configured data directory
    json_store.initialize(user_data_path=config.DATA_DIR)
    
    logger.info("Using JSON storage backend")
    return json_store