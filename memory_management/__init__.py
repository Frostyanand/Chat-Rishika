"""Memory Management System for Elysia"""
import os
import json
import logging
from typing import Optional, Dict, Any

from .config import initialize as initialize_config, get_config
from .memory_store import MemoryStore
from .json_memory_store import JsonMemoryStore
from .memory_store_factory import create_memory_store

logger = logging.getLogger(__name__)

# Global memory store instance
_memory_store: Optional[MemoryStore] = None

def initialize(config_override: Optional[Dict[str, Any]] = None) -> None:
    """
    Initialize the memory management system.
    
    Args:
        config_override: Optional configuration overrides
    """
    global _memory_store
    
    try:
        # Initialize configuration first
        initialize_config(config_override)
        config = get_config()
        
        # Create appropriate memory store
        _memory_store = create_memory_store()
        
        logger.info("Memory management system initialized successfully")
        
    except Exception as e:
        error_msg = f"Error initializing memory management system: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg)

def get_memory_store() -> MemoryStore:
    """
    Get the global memory store instance.
    
    Returns:
        MemoryStore: The configured memory store instance
        
    Raises:
        RuntimeError: If the memory system is not initialized
    """
    if _memory_store is None:
        initialize()
    return _memory_store

def reset(keep_data: bool = False) -> None:
    """
    Reset the memory management system.
    
    Args:
        keep_data: If True, preserve stored data
    """
    global _memory_store
    
    if _memory_store is not None:
        try:
            if not keep_data:
                # Clean up data if requested
                config = get_config()
                if os.path.exists(config.DATA_DIR):
                    import shutil
                    shutil.rmtree(config.DATA_DIR)
            
            # Clean up any resources
            _memory_store.cleanup()
            
        except Exception as e:
            logger.error("Error during memory system reset: %s", str(e))
        finally:
            _memory_store = None
    
    logger.info("Memory management system reset")

# Version
__version__ = '0.1.0'

# Public API
__all__ = [
    'MemoryStore',
    'JsonMemoryStore',
    'create_memory_store',
    'initialize',
    'get_memory_store',
    'reset',
    '__version__'
]